import time

def getWord(sentence):
    """
    网页富文本解析文字
    :param sentence:
    :return:
    """
    word = ''
    tag = 0
    for i in sentence:
        if i is '<':
            tag = 1
            continue
        elif i is '>':
            tag = 0
            continue
        elif tag == 0:
            word += i
    return word

def trans_format(time_string, from_format, to_format='%Y.%m.%d %H:%M:%S'):
    """
    @note 时间格式转化
    :param time_string:
    :param from_format:
    :param to_format:
    :return:
    """
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times