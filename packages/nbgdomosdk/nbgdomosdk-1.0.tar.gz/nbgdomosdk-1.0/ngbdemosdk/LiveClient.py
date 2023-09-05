# coding:utf-8
import requests

class LiveClient(object):

    def __init__(self, appId, appSecret, baseUrl):
        self.appId = appId
        self.appSecret = appSecret
        self.baseUrl = baseUrl

    def wrap_header(self, headers, params):
        headers["user-agent"] = "nbg-demo-python-sdk/v1.0"


    def authorization_code(self, code):
        api = self.baseUrl
        params = {
            "appId": self.appId,
            "code": code,
            "grant_type": "authorization_code"}
        headers = {}
        self.wrap_header(headers, params)
        response = requests.post(api, params=params, headers=headers)
        return response.json()

    def close(self):
        pass
