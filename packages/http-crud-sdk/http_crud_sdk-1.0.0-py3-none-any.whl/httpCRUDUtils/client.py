from typing import Optional

import requests
import logging

from requests import Response

from httpCRUDUtils.utils import get_url

logger = logging.getLogger(__name__)


class HttpCRUDUtils:
    headers = {"Content-Type": "application/json"}

    @classmethod
    def base_post(cls, base_path: str = '', detail_path: str = '', params: Optional[dict] = None) -> Response:
        """
        POST请求
        """
        logger.info("请求方式：POST, 请求url:  %s  ,请求参数： %s " % (base_path + detail_path, params))
        response = requests.post(base_path + detail_path, data=params, headers=cls.headers)
        logger.info("请求方式：POST, 请求url:  %s  , 请求参数： %s , 结果：%s" % (base_path + detail_path, params, response))
        return response

    @classmethod
    def base_get(cls, base_path: str = '', detail_path: str = '', params: Optional[dict] = None) -> Response:
        """
            GET请求
        :param base_path: 域名
        :param detail_path: 接口详情
        :param params: 参数
        :return:
        """
        logger.info("请求方式：GET, 请求url:  %s  , 请求参数： %s " % (base_path + detail_path, params))
        response = requests.get(base_path + detail_path, params=params)
        logger.info("请求方式：GET, 请求url:  %s  , 请求参数： %s , 结果：%s" % (base_path + detail_path, params, response))
        return response

    @classmethod
    def base_put(cls, base_path: str = '', detail_path: str = '', resource_id: Optional[str] = None,
                 params: Optional[dict] = None) -> Response:
        """
        PUT请求
        """
        url = get_url(base_path, detail_path, resource_id)
        logger.info("请求方式：PUT, 请求url:  %s  , 请求参数： %s " % (url, params))
        response = requests.put(url, data=params, headers=cls.headers)
        logger.info("请求方式：PUT, 请求url:  %s  , 请求参数： %s , 结果：%s" % (url, params, response))
        return response

    @classmethod
    def base_delete(cls, base_path: str = '', detail_path: str = '', resource_id: Optional[str] = None,
                    params: Optional[dict] = None) -> Response:
        """
        DELETE请求
        """
        url = get_url(base_path, detail_path, resource_id)
        logger.info("请求方式：DELETE, 请求url:  %s  , 请求参数： %s " % (url, params))
        response = requests.delete(url, data=params, headers=cls.headers)
        logger.info("请求方式：DELETE, 请求url:  %s  , 请求参数： %s , 结果：%s" % (url, params, response))
        return response
