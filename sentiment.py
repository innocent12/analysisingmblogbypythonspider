import datetime
import math
from snownlp import SnowNLP
import pandas as pd
from util import getWord,trans_format
import config as cfg
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False   #这两行需要手动设置


def sentiment_line(start, end, sub_path):
    """
    情绪随时间变化曲线
    舆情计算公式:average value of all scores during the day
    :return:
    """
    df = pd.read_excel(cfg.data_path + '/' + sub_path + '/mblog.xlsx')
    df['date'] = df['created_at'].apply(lambda x: trans_format(x, '%a %b %d %H:%M:%S +0800 %Y','%Y-%m-%d %H:%M:%S'))
    df = df[['date', 'created_at', 'text']]
    # 生成datetime64日期索引
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    df.set_index(keys=['date'], inplace=True)
    df.sort_index(inplace=True)
    # print(df)
    # 数据处理获取中文
    df['text'] = df['text'].apply(getWord)
    # 生成情绪分数
    df['emotional'] = df['text'].apply(lambda x: SnowNLP(x).sentiments)
    date1 = start
    list1 = {}
    while date1 < end:
        indexs = df.index.to_list()
        for idx in indexs:
            if date1 in str(idx):
                temp = df[date1]
                # 当天日期的情绪均值
                list1[date1] = temp['emotional'].mean()
                break
        dt = datetime.datetime.strptime(date1, '%Y-%m-%d')
        dt += datetime.timedelta(days=1)
        date1 = dt.strftime('%Y-%m-%d')
    plt.plot(list1.keys(), list1.values(), linestyle='-')
    plt.xticks(())
    plt.title('{0}至{1}的舆情曲线'.format(start, end))
    plt.savefig(cfg.data_path + '/' + sub_path + '/emotion.png')
    plt.show()


def sentiment_analysis(sub_path):
    """
    # 情感分析
    # 基于微博和评论进行情感分析
    # 展现所抓取的微博和评论的情感，并随即分布到散点图上
    # 评论按照时间排序，筛选前100条
    """
    df = pd.read_csv(cfg.data_path + '/' + sub_path + '/comment.csv')
    df.dropna(inplace=True)
    dict1 = df['text'].tolist()
    score = []
    for i in dict1:
        try:
            score.append(SnowNLP(i).sentiments)
        except Exception as e:
            print(i)
    # 首先确定x轴,然后确定y轴
    new_score = []
    for s in score:
        new_score.append(math.floor(s*100)/100)
    result = pd.value_counts(new_score)
    result = result.to_dict()
    x = list(result.keys())
    y = list(result.values())
    plt.bar(x=x, height=y, width=0.01)
    plt.xlabel("情绪值")
    plt.ylabel("评论数量")
    plt.title('评论情绪值')
    plt.savefig(cfg.data_path + '/' + sub_path + '/sentiment.jpg')
    plt.show()


if __name__ == '__main__':
    # sentiment_analysis()
    # sentiment_line(start='2022-01-05', end='2022-03-10')
    url = 'https://m.weibo.cn/api/container/getIndex?containerid=231522type%3D61%26q%3D%23%E6%B5' \
          '%99%E4%B8%96%E7%95%8C%E9%82%A3%E4%B9%88%E5%A4%9A%E4%BA%BA%E6%8A%97%E7%96%ABmv%23%26t%3D0' \
          '&page_type=searchall&page={0}'
    url = url.format(1)
