# coding=utf-8
import logging
import os
import sys

import itchat

from config import BASE_DIR
from utils import get_tuling_reply

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(
    filename=os.path.join(BASE_DIR, 'autoreply.log'),
    format="%(asctime)-15s [%(levelname)s] %(message)s",
)
LOG = logging.getLogger('itchat_autoreply')
INFO, DEBUG = LOG.info, LOG.debug


def main():
    """"""

    @itchat.msg_register(itchat.content.TEXT)
    def text_reply(msg):
        msg_text = msg.get(u'Text', u'')
        msg_from_user = msg.get(u'FromUserName', u'Unknown')
        print(u'Got msg from user: {}, text: {}'.format(msg_from_user, msg_text))
        print(u'Full msg: {}'.format(msg))
        ret_msg = u'[机器人]' + get_tuling_reply(msg_text).decode('utf-8')
        print(u'Reply text: {}'.format(ret_msg))
        return ret_msg

    itchat.auto_login(enableCmdQR=True)
    itchat.run()


def test_friend():
    itchat.auto_login(hotReload=True)

    chatroomUserName = '@1234567'
    friends = itchat.get_friends()
    print friends

    # r = itchat.add_member_into_chatroom(chatroomUserName, [friend])
    # if r['BaseResponse']['ErrMsg'] == '':
    #     status = r['MemberList'][0]['MemberStatus']
    #     itchat.delete_member_from_chatroom(chatroom['UserName'], [friend])
    #     return {3: u'该好友已经将你加入黑名单。',
    #             4: u'该好友已经将你删除。', }.get(status,
    #                                     u'该好友仍旧与你是好友关系。')


if __name__ == '__main__':
    main()