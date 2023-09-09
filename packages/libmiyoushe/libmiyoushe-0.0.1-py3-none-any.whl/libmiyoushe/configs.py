import json
import logging
from typing import Type

from . import account_file, account_default, get_current_user, set_current_user, md5

logger = logging.getLogger('libhoyolab.configs')


def readAccount(return_type: str | Type[str | dict], uid: str = 'current'):
    """
    获取用户信息
    :param uid: 需要读取的uid（默认‘current’为当前设置的uid）
    :param return_type: 期望返回的类型
    :return:
    """
    try:
        with open(account_file) as f:
            account_set = json.load(f)
    except:
        account_set = account_default
        with open(account_file, 'w') as f:
            json.dump(account_set, f, indent=2, ensure_ascii=False)
    try:
        if uid == 'current':
            uid = get_current_user()
            if uid == '-1':
                raise Exception
        account = account_set['account'][uid]
        if return_type is dict or return_type.lower == 'dict':
            return account
        elif return_type is str or return_type.lower == 'str':
            account_str = '; '.join([f'{key}={account[key]}' for key in account])
            return account_str
    except:
        if return_type is dict or return_type.lower == 'dict':
            return dict()
        elif return_type is str or return_type.lower == 'str':
            return ''


def writeAccount(uid, account):
    try:
        with open(account_file) as f:
            account_set = json.load(f)
    except:
        account_set = account_default
        with open(account_file, 'w') as f:
            json.dump(account_set, f, indent=2, ensure_ascii=False)
    with open(account_file, 'w') as f:
        account_set['account'][str(uid)] = account
        account_set['account_hash'] = md5(json.dumps(account_set['account']))
        json.dump(account_set, f, indent=2, ensure_ascii=False)
    return True


def clearAccount(uid: str):
    try:
        with open(account_file) as f:
            account_set = json.load(f)
    except:
        account_set = account_default
        with open(account_file, 'w') as f:
            json.dump(account_set, f, indent=2, ensure_ascii=False)
    if uid.lower() == 'all':
        account_set = account_default
        with open(account_file, 'w') as f:
            json.dump(account_set, f, indent=2, ensure_ascii=False)
    elif uid.isdigit():
        account_set['account'].pop(uid, '')
        account_set['account_hash'] = md5(json.dumps(account_set['account']))
        with open(account_file, 'w') as f:
            json.dump(account_set, f, indent=2)


