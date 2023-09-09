# import argparse
# from version import __version__
# from cfg import l
#
#
# def run():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--version', action='version', version=f'TtTest v{__version__}',
#                         help=("显示版本号", 'display tttest version')[l.n])
#     args = parser.parse_args()
#
#     # 有参数放在文件中，必须首先处理
#     if args.argfile:
#         fileArgs = [para for para in args.argfile.read().replace('\n', ' ').split() if para]
#         print(fileArgs)
#         args = parser.parse_args(fileArgs, args)
#
#     # 看命令行中是否设置了语言
#     if args.lang:
#         l.n = l.LANGS[args.lang]
#
#
# if __name__ == '__main__':
#     exit(run())

import itertools

case_list = ['用户名', '密码']
value_list = ['正确', '不正确', '特殊符号', '超过最大长度']


def gen_case(item=case_list, value=value_list):
    """输出笛卡尔用例集合"""
    for i in itertools.product(item, value):
        print('输入'.join(i))


def test_print():
    print("欢迎搜索关注公众号: 「测试开发技术」!")


if __name__ == '__main__':
    test_print()
