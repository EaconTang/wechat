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
    if isinstance(content, unicode):
        content = content.encode('utf8')
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


def get_tuling_reply(content):
    url = 'http://www.tuling123.com/openapi/api'
    ret = requests.post(url, data=json.dumps(dict(
        key=TULING_API_KEY,
        info=content,
    )))
    if ret.status_code == 200:
        res = json.loads(ret.text)
        # print res
        res_code = res.get('code', -1)
        if res_code == 100000:
            # just text
            return res['text'].encode('utf8')
        elif res_code == 200000:
            # link
            return '\n'.join([res['text'], u'点击链接: ' + res['url']]).encode('utf8')
        elif res_code == 302000:
            # news
            news_list = res.get('list', [])
            news_list = ['\n'.join([str(i) + ') ' + news['article'], u'点击链接: ' + news['detailurl']]) for i, news in
                         enumerate(news_list, start=1)]
            return '\n'.join([res['text'], '\n'.join(news_list)]).encode('utf8')
        elif res_code == 308000:
            # food menu
            menu_list = res.get('list', [])
            menus = '\n'.join(
                ['\n'.join([str(i) + u') 菜名: ' + menu['name'], u'菜谱信息: ' + menu['info'], u'点击链接: ' + menu['detailurl']])
                 for i, menu in enumerate(menu_list, start=1)])
            return '\n'.join([res['text'], menus]).encode('utf8')
        elif res_code == 40004:
            # requests times used up
            return u'我今天聊的太多了, 好累, 让我休息下...'.encode('utf8')
        else:
            return res.encode('utf8')
    else:
        return ret.text.encode('utf8')


################################################################################
def policy():
    foo_list = (
        u'钟泳芳', u'花娃娃',
        u'江坤娟', u'江小花', u'小花', u'姑子', u'大拿', u'王妮丹'
        u'丘茜', u'陈利利', u'汤玉云', u'阿云妹',
        u'汤晓君', u'阿君妹', u'汤红艳', u'啊艳妹',
    )
    return [
        # [(key words), reply]
        [
            (u'help', u'帮助', u'说明'),
            HELP
        ],
        [
            (u'汤英康', u'小康'),
            u'我的主人汤英康是最棒哒!'
        ],
        [
            foo_list,
            u'别跟我提那个逗比'
        ],
        [
            (u'笑话',),
            get_joke
        ],
        [
            ('joke',),
            get_dark_humor_joke
        ],
        # [(u'博客', ), get_blog_titles],
    ]


HELP = u"""
你好, 欢迎关注Eacon的个人公众号。
我是Eacon手下的人工智能机器人哦! 你可以和我聊天, 谈任何话题(非限制级)~
对于包含特定关键词的内容, 主人会指导我进行回复, 不信你可以试试输入下面这些关键字看看:
1) 输入"笑话"或者包含"笑话"的短句, 我找个笑话给你乐乐(不好笑别打我)
2) 输入"joke", 我从jokes.cc网上给你找个黑色幽默(冷)
3) 输入"XX的图片", 我可以帮你搜索XX的相关图片哦(请不要搜黄图我还是个孩子)
4) 输入"看新闻", 我会把今天的热门新闻发给你
5) 输入"XX的天气", 我会告诉你XX今天的天气如何
6) 输入"XX到XX的车票", 我帮你查下这两地的来往车票
7) 输入"XX座的运势", 看你今天如何逢凶化吉
8) 输入"XX的简介", 我告你它是什么鬼
9) 输入"查询快递<快递单号>", 我帮你查下单号<快递单号>的物流情况(支持申通/顺丰/圆通/韵达/中通/汇通等快递公司)
10) 输入"天为什么是蓝的"/"地球为什么是圆的"之类的问题试试?
11) 输入你的名字试试, 说不定中奖了呢? 嘿嘿嘿(坏笑脸)
"""


if __name__ == '__main__':
    for k, v in policy():
        print k, v
