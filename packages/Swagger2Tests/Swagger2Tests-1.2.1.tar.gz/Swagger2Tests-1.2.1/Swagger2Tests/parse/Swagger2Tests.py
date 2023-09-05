from jinja2 import Environment, FileSystemLoader, Template
import json
from enum import Enum
from pathlib import Path
from Swagger2Tests.utils import *
import requests


class BaseEnum(Enum):

    @classmethod
    def get_enum_by_value(cls, value):
        for enum in cls.__members__.values():
            if enum.value == value:
                return enum
        raise ValueError('No matching enum for value: {}'.format(value))


class HttpMethodEnum(BaseEnum):
    POST = 'post'
    GET = 'get'


class HttpParameterLocationEnum(BaseEnum):
    BODY = 'body'
    QUERY = 'query'


class SwaggerPathParameter:
    paramsLocation: HttpParameterLocationEnum
    params: dict
    query: dict

    def __init__(self, location: str, params: dict) -> None:
        self.paramsLocation = HttpParameterLocationEnum.get_enum_by_value(
            location)
        self.params = params
        self.query = {}


class SwaggerPathObject:
    url: str
    method: HttpMethodEnum
    tags: list
    summary: str
    operationId: str
    consumes: list
    parameters: list[SwaggerPathParameter] = []
    responses: dict
    query: dict

    def __init__(self, pathUrl: str, pathdata: dict, pathMethod: str):
        self.url = pathUrl
        self.method = HttpMethodEnum.get_enum_by_value(pathMethod)
        self.tags = pathdata.get('tags')
        self.summary = pathdata.get('summary')
        self.consumes = pathdata.get('consumes')
        self.operationId = pathdata.get('operationId')
        self.responses = pathdata.get('responses')
        self.query = {}


class SwaggerParse:

    swaggerJson: dict
    definitions: dict
    paths: list[SwaggerPathObject] = []

    def __init__(self, fp: str = None, swaggerUrl: str = None) -> None:
        if swaggerUrl is not None:
            self.swaggerJson = self.requestSwaggerJson(swaggerUrl)
        else:
            self.swaggerJson = json.load(open(fp))
        self.definitions = self.swaggerJson.get("definitions")
        pathsValue: dict = self.swaggerJson.get("paths")
        for path, pathData in pathsValue.items():
            for method, methodData in pathData.items():
                swaggerPathObj = SwaggerPathObject(pathUrl=path,
                                                   pathMethod=method,
                                                   pathdata=methodData)
                if 'parameters' not in methodData:
                    continue
                swaggerPathParametters = []
                swaggerPathResponses = {}
                swaggerPathQuery = {}
                for items in methodData['parameters']:
                    swaggerPathParametter = SwaggerPathParameter(
                        location=items['in'], params={})
                    if 'schema' in items and 'originalRef' in items['schema']:
                        properties = self.definitions.get(
                            items['schema']['originalRef']).get('properties')
                        swaggerPathParametter.params = self.reassemble_properties(
                            properties)
                    elif items['in'] == HttpParameterLocationEnum.QUERY.value:
                        swaggerPathQuery[items['name']] = items['type'] 
                    swaggerPathParametters.append(swaggerPathParametter)
                responses = methodData['responses']
                swaggerPathResponses = self.parsePathResponse(responses)
                swaggerPathObj.parameters = swaggerPathParametters
                swaggerPathObj.responses = swaggerPathResponses
                swaggerPathObj.query = swaggerPathQuery
                self.paths.append(swaggerPathObj)

    def parsePathResponse(self, response: dict) -> dict:
        """格式化输出 path的response

        Args:
            response (dict): _description_

        Returns:
            dict: _description_
        """
        result = {}
        for httpStatus, responseObj in response.items():
            if 'schema' in responseObj and 'originalRef' in responseObj[
                    'schema']:
                properties = self.definitions.get(
                    responseObj['schema']['originalRef']).get('properties')
                result[httpStatus] = self.reassemble_properties(properties)
        return result

    def requestSwaggerJson(self, pathUrl) -> dict:
        response = requests.get(pathUrl)
        content = response.json()
        return content

    @staticmethod
    def parseParameters2Jinja(
            parameters: list[SwaggerPathParameter]) -> list[dict]:
        """格式化输出参数到jinja适合处理的

        Args:
            parameters (list[SwaggerPathParameter]): _description_
        """
        result = []
        for item in parameters:
            obj = {}
            obj['in'] = item.paramsLocation.value
            obj['params'] = SwaggerParse.parsePathRequestBody(item.params)
            result.append(obj)
        return result

    @classmethod
    def parsePathRequestBody(cls, params: dict):
        for key, value in params.items():
            if isinstance(value, dict):
                cls.parsePathRequestBody(value)
            else:
                if value == 'integer':
                    params[key] = FuncHelper.get_random_int()
                if value == 'boolean':
                    params[key] = FuncHelper.get_random_bool()
                if value == 'number':
                    params[key] = FuncHelper.get_random_float()
        return params

    def reassemble_properties(self, properties: dict) -> dict:
        """解析请求体

        Args:
            properties (dict): _description_

        Returns:
            _type_: _description_
        """
        new_properties = {}
        for key, value in properties.items():
            if isinstance(value, dict) and '$ref' in value:
                ref_key = value.get('originalRef')
                new_properties[key] = self.reassemble_properties(
                    self.definitions.get(ref_key).get('properties'))
            else:
                new_properties[key] = value.get('type')

        return new_properties


class Swagger2Tests:

    pytestTpl: Template

    def __init__(self, pytestTpl: str, templateDir: str) -> None:
        env = Environment(loader=FileSystemLoader(templateDir))
        self.pytestTpl = env.get_template(pytestTpl)

    def generatePytestContent(self, value: dict) -> str:
        return self.pytestTpl.render(value)

    def writeTestContentToFile(self, targetFile: Path, content: str) -> bool:
        if not targetFile.exists():
            targetFile.touch()
        oldContent = targetFile.read_text('utf-8')
        if oldContent != '' and oldContent != content:
            user_input = input("目标文件 %s 已被更新过，是否确认覆盖？(y/n): " %
                               targetFile.as_posix())
            if user_input.lower() != 'y':
                return False
        targetFile.write_text(content)
        return True