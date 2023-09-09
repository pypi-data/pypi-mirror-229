supportedLang = ['zh', 'en']


class l:
    LANGS = {
        'zh': 0,
        'en': 1,
    }
    n = None  # 当前使用的语言编号


import sys

if '--lang' in sys.argv:
    try:
        idx = sys.argv.index('--lang')
        lang = sys.argv[idx + 1]
        if lang in supportedLang:
            l.n = l.LANGS[lang]
    except:
        ...

if l.n is None:
    import locale

    if 'zh_CN' in locale.getdefaultlocale():
        l.n = l.LANGS['zh']
    else:
        l.n = l.LANGS['en']
