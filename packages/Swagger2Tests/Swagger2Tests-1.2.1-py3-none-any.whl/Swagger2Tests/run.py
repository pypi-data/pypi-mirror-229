import coloredlogs
import logging
from pathlib import Path
from Swagger2Tests.parse.Swagger2Tests import *
import argparse
import os
import shutil
from urllib.parse import urlparse

coloredlogs.install()


logging.info("Running...")


def convert_to_camel_case(string):
    words = string.replace('_', '-').split('-')
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])
    return camel_case


def parse_swagger_test_file(swagger:SwaggerParse,swagger2Tests:Swagger2Tests,target:Path):
    for swaggerPathObject in swagger.paths:
        swaggerPathObject: SwaggerPathObject
        directories = swaggerPathObject.url.split("/")
        # 去除空字符串和最后一个元素
        directories = [d for d in directories if d]  # 去除空字符串
        className = directories[-1].capitalize()  # 首
        classFileName = className + "Case.py"
        #     print(last_directory)
        filePath = target/'testCases'
        for directory in directories[:-1]:
            filePath = filePath / convert_to_camel_case(directory)
        Path(filePath).mkdir(parents=True, exist_ok=True)
        parameters = SwaggerParse.parseParameters2Jinja(
            swaggerPathObject.parameters)
        pytestValue: dict = {
            "pytestCaseName": className,
            "parameters": parameters,
            'swaggerPathObject': swaggerPathObject
        }
        targetFile = (Path(filePath) / classFileName)
        writeRes: bool = swagger2Tests.writeTestContentToFile(
            targetFile, swagger2Tests.generatePytestContent(pytestValue))
        if writeRes:
            logging.info("%s 写入成功" % targetFile.as_posix())

def parse_arguments():
    parser = argparse.ArgumentParser(description='swagger2test by vison')
    parser.add_argument('--init',action="store_true" ,help='init project,then you can modify template')
    parser.add_argument('--swagger', type=str, help='swagger file or url')
    parser.add_argument('--target', type=str, help='path to target',default="./")
    return parser.parse_args()

def copy(srcPath:Path,targetPath:Path):
    # 复制 constants
    copyConstant:bool = True
    if targetPath.exists():
        user_input = input("%s 已存在，是否确认覆盖？(y/n): " % targetPath.as_posix())
        if user_input.lower() != 'y':
            copyConstant = False
    if copyConstant:
        shutil.copytree(srcPath,targetPath,dirs_exist_ok=True)

def applicationExit(msg:str="程序退出"):
    logging.error("程序非正常退出 %s"%msg)
    os._exit(1)

def init_project(srcPath, targetPath:Path):
    if targetPath.exists():
        applicationExit("apps目录已存在")
    targetPath.mkdir(exist_ok=False)
    Path(targetPath/'__init__.py').touch(exist_ok=True)
    copy(Path(srcPath)/'constants',targetPath/'constants')
    copy(Path(srcPath)/'templates',targetPath/'templates')
    copy(Path(srcPath)/'helpers',targetPath/'helpers')
    logging.info("project init complete")

def is_url(path):
    parsed_url = urlparse(path)
    if parsed_url.scheme and parsed_url.netloc:
        return True
    return False

def main():
    args = parse_arguments()
    current_path = os.path.dirname(os.path.abspath(__file__))
    # swaggerFile = 'https://refuel-openapi-stg.huolala.cn/v2/api-docs'
    
    appPath: Path = Path(args.target)/'apps'
    if args.init and args.target:
        init_project(current_path,appPath)
    if args.swagger:
        swaggerFile = args.swagger
        if not is_url(swaggerFile):
            swagger = SwaggerParse(fp=swaggerFile)
        else:
            swagger = SwaggerParse(swaggerUrl=swaggerFile)
        templateDir = appPath.as_posix()+'/templates'
        swagger2Tests = Swagger2Tests(templateDir=templateDir,
                                pytestTpl='pytestcase.tpl')
        parse_swagger_test_file(swagger=swagger,swagger2Tests=swagger2Tests,target=appPath)
    logging.info("End...")