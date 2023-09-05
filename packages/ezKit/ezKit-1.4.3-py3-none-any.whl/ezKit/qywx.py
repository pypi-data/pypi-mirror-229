import json
import time

import requests


class QYWX(object):
    """企业微信"""

    """
    企业微信开发者中心

        https://developer.work.weixin.qq.com/
        https://developer.work.weixin.qq.com/document/path/90313 (全局错误码)

    参考文档:

        https://www.gaoyuanqi.cn/python-yingyong-qiyewx/
        https://www.jianshu.com/p/020709b130d3
    """

    url_prefix = 'https://qyapi.weixin.qq.com'
    work_id: str | None = None
    agent_id: str | None = None
    agent_secret: str | None = None
    access_token: str | None = None

    def __init__(self, work_id: str | None, agent_id: str | None, agent_secret: str | None):
        ''' Initiation '''
        self.work_id = work_id
        self.agent_id = agent_id
        self.agent_secret = agent_secret

        ''' 获取 Token '''
        self.getaccess_token()

    def getaccess_token(self) -> bool:
        try:
            _response = requests.get(f'{self.url_prefix}/cgi-bin/gettoken?corpid={self.work_id}&corpsecret={self.agent_secret}')
            if _response.status_code == 200:
                _result: dict = _response.json()
                self.access_token = _result.get('access_token')
            else:
                self.access_token = None
            return True
        except:
            return False

    def get_agent_list(self) -> dict | None:
        try:
            self.getaccess_token() if self.access_token == None else next
            _response = requests.get(f'{self.url_prefix}/cgi-bin/agent/list?access_token={self.access_token}')
            if _response.status_code == 200:
                _response_data: dict = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.get_agent_list()
                return _response_data
            return {'response': _response.text}
        except:
            return None

    def get_department_list(self, id) -> dict | None:
        try:
            self.getaccess_token() if self.access_token == None else next
            _response = requests.get(f'{self.url_prefix}/cgi-bin/department/list?access_token={self.access_token}&id={id}')
            if _response.status_code == 200:
                _response_data: dict = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.get_department_list(id)
                return _response_data
            return {'response': _response.text}
        except:
            return None

    def get_user_list(self, id) -> dict | None:
        try:
            self.getaccess_token() if self.access_token == None else next
            _response = requests.get(f'{self.url_prefix}/cgi-bin/user/list?access_token={self.access_token}&department_id={id}')
            if _response.status_code == 200:
                _response_data: dict = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.get_user_list(id)
                return _response_data
            return {'response': _response.text}
        except:
            return None

    def get_user_id_by_mobile(self, mobile) -> dict | None:
        try:
            self.getaccess_token() if self.access_token == None else next
            _json_dict = {'mobile': mobile}
            _json_string = json.dumps(_json_dict)
            _response = requests.post(f'{self.url_prefix}/cgi-bin/user/getuserid?access_token={self.access_token}', data=_json_string)
            if _response.status_code == 200:
                _response_data: dict = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.get_user_id_by_mobile(id)
                return _response_data
            return {'response': _response.text}
        except:
            return None

    def get_user_info(self, id) -> dict | None:
        try:
            self.getaccess_token() if self.access_token == None else next
            _response = requests.get(f'{self.url_prefix}/cgi-bin/user/get?access_token={self.access_token}&userid={id}')
            if _response.status_code == 200:
                _response_data: dict = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.get_user_info(id)
                return _response_data
            return {'response': _response.text}
        except:
            return None

    def send_text(self, users, message) -> dict | None:
        """发送消息"""
        """
        参考文档:

            https://developer.work.weixin.qq.com/document/path/90235
        """
        try:
            self.getaccess_token() if self.access_token == None else next
            _json_dict = {
                'touser': users,
                'msgtype': 'text',
                'agentid': self.agent_id,
                'text': {'content': message},
                'safe': 0,
                'enable_id_trans': 0,
                'enable_duplicate_check': 0,
                'duplicate_check_interval': 1800
            }
            _json_string = json.dumps(_json_dict)
            _response = requests.post(f'{self.url_prefix}/cgi-bin/message/send?access_token={self.access_token}', data=_json_string)
            if _response.status_code == 200:
                _response_data = _response.json()
                if _response_data.get('errcode') == 42001:
                    self.getaccess_token()
                    time.sleep(1)
                    self.send_text(users, message)
                return _response_data
            return {'response': _response.text}
        except:
            return None
