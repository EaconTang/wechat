# coding=utf-8
import json
import requests
from config import *


def get_access_token(app_id, app_secret):
    """
    get wechat ACCESS_TOKEN
    :param app_id:
    :param app_secret:
    :return: str, access_token
    """
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(app_id,
                                                                                                           app_secret)
    ret_dict = json.loads(requests.get(url).text)
    if 'errcode' in ret_dict:
        raise Exception('Error while trying to get access_token: ', ret_dict.get('errmsg'))
    return ret_dict.get('access_token')


def get_wechat_server_ip(access_token):
    """
    :param access_token:
    :return: list, ip list
    """
    url = 'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={}'.format(access_token)
    ret_dict = json.loads(requests.get(url).text)
    if 'errcode' in ret_dict:
        raise Exception('Error while trying to get wechat server ip: ', ret_dict.get('errmsg'))
    return ret_dict.get('ip_list')


def create_menu(access_token, menu):
    """

    :param menu: dict,
    :param access_token:
    :return:
    """
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={}'.format(access_token)
    ret_dict = json.loads(requests.post(url, data=menu).text)
    if ret_dict.get('errcode') != 0:
        raise Exception('Error while trying to create menu: ', ret_dict.get('errcode'), ret_dict.get('errmsg'))
    print 'Create menu success!'
    return ret_dict.get('errmsg')  # 'ok'


def get_autoreply_info(access_token):
    """

    :param access_token:
    :return:
    """
    url = 'https://api.weixin.qq.com/cgi-bin/get_current_autoreply_info?access_token={}'.format(access_token)
    ret_dict = json.loads(requests.get(url).text)
    return ret_dict


def upload_media_tmp(access_token, type, media_data):
    url = 'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}'.format(access_token, type)
    ret_dict = json.loads(requests.post(url, data=media_data).text)
    if 'errcode' in ret_dict:
        raise Exception('Error while trying to upload media temporary: ', ret_dict.get('errcode'), ret_dict.get('errmsg'))
    print 'Upload media temparary success!'
    return ret_dict.get('media_id')

if __name__ == '__main__':
    token = get_access_token(APP_ID, APP_SECRET)
    print upload_media_tmp(token, 'image', {'media': open('003.jpg', 'rb')})
