import pytest
from apps.constants.base_constants import *
import requests
import logging
import json

class {{ pytestCaseName }}Case:

    @staticmethod
    def {{ swaggerPathObject.operationId }}(base_url:str=None) -> RequestInfo:
        # {{ swaggerPathObject.summary }}
        if base_url is None:
            base_url = BASE_URL
        requestPath = '{{ swaggerPathObject.url }}'
        requestUrl = base_url+requestPath
        requestBody = None
        {% for obj in parameters -%}
            {% if obj['in'] == 'body' -%}
        requestBody = {
            "appid": REQUEST_APPID,
            "bizContent": {{ obj.params.bizContent }},
            "sign": "string",
            "timestamp": Helper.get_random_datetime()
        }
        sign: str
        sign = Helper.generate_sign(requestBody.copy(), REQUEST_SECRECT)
        requestBody.update({"sign": sign})
        logging.info("请求数据: url %s 参数 %s" % (requestUrl,json.dumps(requestBody)))
            {% endif -%}
        {% endfor %}
        {% if swaggerPathObject.query is not none -%}
            params = {{ swaggerPathObject.query }}
        {% endif %}
        
        # response = requests.request('{{ swaggerPathObject.method.value }}',requestUrl 
        #,json= requestBody
        # ,params= params)
        # logging.info("请求返回: %s" % (response.content.decode("utf-8")))
        # assert response.status_code == 200
        # assert response.json()["ret"] == 0
        request_info:RequestInfo = RequestInfo()
        request_info.request_url = requestUrl
        request_info.request_path = requestPath
        request_info.request_method = '{{ swaggerPathObject.method.value }}'
        request_info.request_body = requestBody
        request_info.request_params = params
        return request_info
        
