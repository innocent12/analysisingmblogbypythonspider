import collections
import jieba
import re

import pandas as pd
from imageio import imread
from random import randint
from io import BytesIO
from wordcloud import WordCloud
import config as cfg


# 随机颜色
def random_color(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    r = randint(30, 255)
    g = randint(30, 180)
    b = int(100.0 * float(randint(60, 120)) / 255.0)
    return "rgb({:.0f}, {:.0f}, {:.0f})".format(r, g, b)


def remove_digits(input_str):
    punc = u'0123456789.'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str

# 停用词表创建
def get_stopwords_list():
    stopwords = [line.strip() for line in
                 open(cfg.static_path + '/' + 'baidu_stopwords.txt', encoding='UTF-8').readlines()]
    return stopwords


def move_stopwords(sentence_list, stopwords_list):
    # 去停用词
    out_list = []
    for word in sentence_list:
        if word not in stopwords_list:
            if not remove_digits(word):
                continue
            if word is '\n':
                continue
            if word is ' ':
                continue
            if word != '\t':
                out_list.append(word)
    return out_list


def word_cloud(sub_path):
    """
    1.词云图-
    数据选择：热门微博的文字内容以及微博的评论数据
    wordcloud
    :return:
    """
    print('----词云图----绘制----')
    stop_words = get_stopwords_list()
    # 词库源文件
    # text = open(cfg.data_path + '/word.txt', 'r', encoding='utf-8').read()  # 读取文本
    text = pd.read_csv(cfg.data_path + '/' + sub_path + '/comment.csv')
    text_cut = jieba.cut(text.to_string(), cut_all=True)  # 分词
    text_cut = move_stopwords(text_cut, stop_words)
    # 统计词频
    word_counts = collections.Counter(text_cut)

    data = []
    for k, v in word_counts.items():
        data.append({'name': k, 'value': v})
    print('--------------------词频统计--------------------')
    print(data)
    new_textlist = ' '.join(text_cut)  # 组合
    pic_address = cfg.static_path + '/map.png'
    pic = imread(pic_address)  # 读取图片
    wc = WordCloud(background_color='white',  # 构造 wordcloud类
                   mask=pic,
                   max_font_size=80,
                   random_state=30,
                   font_path=cfg.static_path + '/' + 'YSHaoShenTi-2.ttf',
                   max_words=1000,
                   min_font_size=10,
                   color_func=random_color)
    wc.generate(new_textlist)  # 生成词云图
    wc.to_file(cfg.data_path + '/' + sub_path + "/_wc.png")  # 保存图片
    img = wc.to_image()
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    # binary_content = img_bytes.getvalue()
    print('词云图 success')


if __name__ == '__main__':
    word_cloud()

