# coding=utf-8
import hashlib
import random
import re

from flask import make_response

from api import *
from config import *


def auth_weixin(token, signature, timestamp, nonce, echostr):
    s = ''.join(sorted([timestamp, nonce, token]))
    if (hashlib.sha1(s).hexdigest() == signature):
        return make_response(echostr)
    else:
        return make_response('Weixin token auth fail!')


def reply_text(to_user_name, from_user_name, create_time, msg_type, content):
    REPLY = """
    <xml>
    <ToUserName><![CDATA[{}]]></ToUserName>
    <FromUserName><![CDATA[{}]]></FromUserName>
    <CreateTime>{}</CreateTime>
    <MsgType><![CDATA[{}]]></MsgType>
    <Content><![CDATA[{}]]></Content>
    </xml>
    """
    return REPLY.format(to_user_name, from_user_name, create_time, msg_type, content)


def reply_image(to_user_name, from_user_name, create_time, msg_type, media_id):
    REPLY = """
    <xml>
    <ToUserName><![CDATA[{}]]></ToUserName>
    <FromUserName><![CDATA[{}]]></FromUserName>
    <CreateTime>{}</CreateTime>
    <MsgType><![CDATA[{}]]></MsgType>
    <Image>
    <MediaId><![CDATA[{}]]></MediaId>
    </Image>
    </xml>
    """
    return REPLY.format(to_user_name, from_user_name, create_time, msg_type, media_id)


def reverse(content):
    if type(content).__name__ == "unicode":
        _content = content[::-1]
        ret_content = _content.encode('UTF-8')
    elif type(content).__name__ == "str":
        _content = content.decode('utf-8')
        ret_content = _content[::-1]
    return ret_content


def get_media_id(*args, **kwargs):
    if kwargs.get('src', None) == 'xkcd':
        return get_xkcd_media_id()
    return None


def get_xkcd_media_id():
    token = get_access_token(APP_ID, APP_SECRET)
    return upload_media_tmp(token, 'image', {'media': get_xkcd_img()})


def get_xkcd_img():
    url = 'http://c.xkcd.com/random/comic/'
    html_text = requests.get(url).text
    img_url = re.findall(r'Image URL \(for hotlinking/embedding\): (.+)\n', html_text)[0]
    return requests.get(img_url).content


def get_joke():
    return random.choice(get_jokes())


def get_jokes():
    url_qiubai = 'http://www.qiushibaike.com/text/'
    ret = requests.get(url_qiubai)
    p = r'<div class="content">(.*?)</div>'
    content_list = re.compile(p, flags=re.S).findall(ret.text)
    jokes = [_.strip('\n').lstrip('<span>').rstrip('</span>').replace('<br/>', '\n') for _ in content_list]
    return jokes


def get_dark_humor_joke():
    urls = get_dark_humor_jokes_links()
    _html = requests.get(random.choice(urls)).text
    title = re.compile(r"""<h2><span class="bgb">(.+?)</span></h2>""").findall(_html)[0]
    _content = re.compile(r"""<div class='content_wrap'>.+?<p>(.+?)</p>.+?</div>""", flags=re.S).findall(_html)[0]
    content = _content.replace('<p>', '').replace('<br>', '').replace('<BR>', '')
    return '\n==========\n'.join((title, content))


def get_dark_humor_jokes_links():
    # get urls of jokes
    list_url = 'http://jokes.cc.com/funny-dark-humor'
    list_html = requests.get(list_url).text
    return [_ for _ in re.compile(r'<a href="(.+?)">').findall(list_html) if
            _.startswith('http://jokes.cc.com/funny-dark-humor/')]


def get_blog_titles():
    ret = requests.get(url='http://localhost:5000/blogs')
    if ret.status_code == 200:
        blog_titles = json.loads(ret.text).get('blogs')
    else:
        blog_titles = []
    return '\n'.join(blog_titles)


def policy():
    return [
        (u'娃娃', u'小傻瓜'),
        (u'宝宝', u'好棒棒'),
        (u'笑话', get_joke()),
        (u'博客', get_blog_titles()),
    ]


if __name__ == '__main__':
    print get_dark_humor_joke()
