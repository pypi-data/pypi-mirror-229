from enum import Enum


class RequestParams:

    @staticmethod
    def getCookies(cookiesStr):
        cookies = {}
        for cookie in cookiesStr.split("; "):
            cookieKeyValue = cookie.split("=")
            cookies[cookieKeyValue[0]] = cookieKeyValue[1]

        return cookies

    @staticmethod
    def getHeaders():
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-xsrf-token": "3f492c8c-81b4-478d-9c21-9c7e7fa59d23"
        }
        return headers

    @staticmethod
    def getCookiesFromFile(file):
        cookies = {}
        fileObj = open(file,"r")
        try:
            for line in fileObj.readlines():
                line = line.strip('\n')
                if line.__contains__('cookie'):
                    cookieKeyAndValues = line.replace('cookie: ','').split("; ")
                    for cookieKeyAndValue in cookieKeyAndValues:
                        keyvalues = cookieKeyAndValue.split("=")
                        cookies[keyvalues[0]] = keyvalues[1]
        finally:
            if  not fileObj:
                fileObj.close()
        return cookies

    def getHeadersFromFile(file):
        headers = {}
        fileObj = open(file, "r")
        try:
            for line in fileObj.readlines():
                line = line.strip('\n')
                if not line.__contains__('cookie'):
                    cookieKeyAndValue = line.split(": ")
                    headers[cookieKeyAndValue[0]] = cookieKeyAndValue[1]
        finally:
            if not fileObj:
                fileObj.close()

        return headers

class ContentTypeEnum(Enum):
    """ContentType的格式枚举
    """
    FormUrlencoded = 'application/x-www-form-urlencoded'

    ApplicationJson = 'application/json'

    def __init__(self,contentType):
        self.contentType = contentType

    @staticmethod
    def getEnum(contentType):
        """
        根据枚举字符变量，找到对应枚举实例
        :param method: 枚举字符变量
        :return: 返回对应枚举实例
        """
        for name, contentTypeEnum in ContentTypeEnum.__members__.items():
            # print(status)
            if contentTypeEnum.contentType == contentType:
                return contentTypeEnum

class MethodEnum(Enum):
    """http请求方式枚举类
    """

    POST = 'POST'

    GET = 'GET'

    DELETE = 'DELETE'

    PUT = "PUT"

    HEAD = 'HEAD'

    OPTIONS = 'OPTIONS'

    PATCH = 'PATCH'

    TRACE = 'TRACE'

    CONNECT = 'CONNECT'

    def __init__(self,method):
        self.method = method

    @staticmethod
    def getEnum(method):
        """
        根据枚举字符变量，找到对应枚举实例
        :param method: 枚举字符变量
        :return: 返回对应枚举实例
        """
        for name, methodEnum in MethodEnum.__members__.items():
            if methodEnum.method == method:
                return methodEnum