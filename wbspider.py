import requests
import time
from urllib.parse import quote
import pandas as pd
import config as cfg
import wordCloud
from util import getWord
import sentiment
import os


class Spider:
    """
    @site https://space.bilibili.com/385873520?spm_id_from=333.1007.0.0
    """
    def __init__(self):
        self.comment_file = '/comment.xlsx'
        self.blog_file = '/mblog.xlsx'
        self.user_file = '/userinfo.xlsx'
        self.comments = '/comment.csv'

    # 从本地文件中获取mid列表
    def hot_flow_list(self):
        d1 = pd.read_excel(cfg.data_path + self.blog_file)
        # print(d1)
        mids = d1['id']
        it = iter(mids)
        for i in it:
            try:
                self.get_hot_flow(i)
            except:
                print('error occur')

    # 微博热评
    # 从获取的mblog的文件中多线程发起评论查询请求
    def get_hot_flow(self, mid=None):
        base_url = cfg.weibo_api['comment_url'].format(mid)
        referer = cfg.weibo_api['comment_referer'].format(mid)
        cfg.headers['Referer'] = referer
        response = requests.request(method='get', url=base_url, headers=cfg.headers).json()
        if 'data' not in response or 'data' not in response['data']:
            return
        self.json2model(response['data']['data'], type='comment')
        user = []
        for i in response['data']['data']:
            user.append(i['user'])
        self.json2model(user, type='user')

    # 获取话题下的实时和热门微博数据
    def get_topic_mblog(self, topic='#武汉大学#', page=10):
        print('----------开始爬取微博话题{0}---------'.format(topic))
        params = {'实时微博': {'baseurl': 'https://m.weibo.cn/api/container/getIndex?containerid=231522type',
                           'param': '=61&q={0}', 'de': '&t=0', 'suffix': '&page_type=searchall&page={0}'},
                  '热门微博': {'baseurl': 'https://m.weibo.cn/api/container/getIndex?containerid=231522type',
                           'param': '=60&q={0}', 'de': '&t=0', 'suffix': '&page_type=searchall&page={0}'}}
        blogs, users = [], []
        for o in params.values():
            quote_param = quote(o['param'].format(topic))
            url = o['baseurl'] + quote_param + quote(o['de']) + o['suffix']
            referer = o['baseurl'] + quote_param
            cfg.headers['Referer'] = referer
            for i in range(page):
                print('page {0}'.format(i))
                u = url.format(i)
                # print(u)
                res = requests.request(method='get', url=u, headers=cfg.headers).json()
                for weibo in res['data']['cards']:
                    # 原微博9
                    # 转发微博11
                    if weibo['card_type'] == 9:
                        blogs.append(weibo['mblog'])
                        users.append(weibo['mblog']['user'])
        # print('共计微博条数:{0}'.format(blogs.__len__()))
        # print('共计用户数:{0}'.format(users.__len__()))
        self.json2model(blogs, type='blog', origin=topic)
        self.json2model(users, type='user')

    def get_user_mblog(self, uid=None, name='武汉大学'):
        """
        获取知名官方微博实时微博
        :param uid:
        :param name:
        :return:
        """
        print('-----------开始爬取用户-----{0}-----'.format(name))
        param = quote(cfg.weibo_param['user_param'].format(name))
        url = cfg.weibo_api['user_url'].format(uid, param)
        response = requests.request(method='get', url=url, headers=cfg.headers).json()
        blogs, users = [], []
        for weibo in response['data']['cards']:
            if weibo['card_type'] == 9:
                blogs.append(weibo['mblog'])
                users.append(weibo['mblog']['user'])
        self.json2model(blogs, type='blog', origin=name)
        self.json2model(users, type='user')

    # json数据封装成model
    def json2model(self, jsondata, type='blog', origin=''):
        # origin_record.append({'name': origin, 'value': jsondata.__len__()})
        d1 = pd.DataFrame(jsondata)
        if type is 'blog':
            d1['origin'] = origin
            print('add {0}数目{1},存入文件'.format(type, d1.__len__()))
            df = pd.read_excel(cfg.data_path + self.blog_file)
            df = df.append(d1)
            df.to_excel(cfg.data_path + self.blog_file, index=False)
        elif type is "user":
            print('add {0}数目{1},存入文件'.format(type, jsondata.__len__()))
            df = pd.read_excel(cfg.data_path + self.user_file)
            df = df.append(d1)
            df.to_excel(cfg.data_path + self.user_file, index=False)
        elif type is 'comment':
            print('add {0}数目{1},存入文件'.format(type, jsondata.__len__()))
            df = pd.read_excel(cfg.data_path + self.comment_file)
            df = df.append(d1)
            df.to_excel(cfg.data_path + self.comment_file, index=False)
        return

    def scrapy_target(self, key='武汉大学'):
        """
        根据关键词获取爬取的目标话题
        :param key:
        :return:
        """
        print('-----获取关键词---话题-----')
        data = {'topiclist': [], 'userlist': []}
        base_url = cfg.weibo_api['base_url']
        user_url = base_url.format(quote(cfg.weibo_param['user_param'].format(key)))
        topic_url = base_url.format(quote(cfg.weibo_param['topic_param'].format(key)))
        referer = cfg.weibo_api['referer_url'].format(quote(cfg.weibo_param['referer_param'].format(key)))
        cfg.headers['Referer'] = referer
        # 获取用户和话题
        response = requests.request(method='get', url=user_url, headers=cfg.headers).json()
        response2 = requests.request(method='get', url=topic_url, headers=cfg.headers).json()
        it = iter(response2['data']['cards'][0]['card_group'])
        for i in it:
            data['topiclist'].append(i['title_sub'])
        users = []
        # if not empty then iterate the obj
        if len(response['data']['cards']) != 0:
            for i in response['data']['cards'][1]['card_group']:
                users.append(i['user'])
                data['userlist'].append({'id': i['user']['id'], 'name': i['user']['screen_name']})
            self.json2model(users, type='user')
        return data

    def data_cleaning(self):
        """
        数据清洗去重并存入数据库
        :param :
        :return:
        """
        print('-------------数据去重----------')
        files = [self.comment_file, self.blog_file, self.user_file]
        for i in files:
            df1 = pd.read_excel(cfg.data_path + i)
            if not df1.empty:
                name = i.split('.')[0].split('/')[2]
                df1 = df1[cfg.dataColumn[name]]
            print('{1} 之前数目:{0}'.format(df1.__len__(), i))
            df1 = df1.drop_duplicates(subset=['id'], keep='first')
            print('{1} 之后数目:{0}'.format(df1.__len__(), i))

            df1 = df1.replace(pd.NA, '')
            # df1 = df1.replace('?')
            df1.to_excel(cfg.data_path + i, index=False)
            # 保存至数据库

    def start_scrapy(self, key):
        """
        spider 流程 (pre half hour)
        requests to excel:获取话题微博、用户微博、
        excel to requests to excel:从微博数据中获取评论
        清洗 userinfo.excel, 清洗 mblog.excel, 清洗comment.excel
        excel to db 存入数据库 mysql: mblog
        :param key:
        :return:
        """
        t1 = time.time()
        data = self.scrapy_target(key)
        users, topics = data['userlist'][0:5], data['topiclist'][0:5]
        for i in users:
            self.get_user_mblog(uid=i['id'], name=i['name'])
        for i in topics:
            self.get_topic_mblog(topic=i, page=20)
        self.data_cleaning()
        self.hot_flow_list()
        self.data_cleaning()
        t2 = time.time()
        print('耗费的时间{0} minute'.format((t2 - t1) / 60))

    def produce_csv(self):
        """
        产生中文文本txt文件
        :param df:
        :return:
        """
        df = pd.read_excel(cfg.data_path + self.comment_file)
        df = df['text']
        df = df.apply(getWord)
        df.dropna(inplace=True)
        df.to_csv(cfg.data_path + self.comments, index=False, mode='a')

    def clear_file(self):
        files = [self.comment_file, self.blog_file, self.user_file]
        for i in files:
            df = pd.DataFrame()
            df.to_excel(cfg.data_path + i, header=False)
        with open(cfg.data_path + '/word.txt', 'w', encoding='utf8') as f:
            f.write('')
        with open(cfg.data_path + self.comments, 'w', encoding='utf8') as f1:
            f1.write('')

    def task(self, words):
        for i in words:
            self.comment_file = '/' + i + '/comment.xlsx'
            self.blog_file = '/' + i + '/mblog.xlsx'
            self.user_file = '/' + i + '/userinfo.xlsx'
            self.comments = '/' + i + '/comment.csv'
            self.clear_file()
            path = cfg.data_path + '/' + i
            if not os.path.exists(path):
                os.mkdir(path)
                file = open(cfg.data_path + self.comment_file, 'w')
                file = open(cfg.data_path + self.blog_file, 'w')
                file = open(cfg.data_path + self.user_file, 'w')
                file = open(cfg.data_path + self.comments, 'w')
            self.start_scrapy(key=i)
            self.produce_csv()
            wordCloud.word_cloud(sub_path=i)
            sentiment.sentiment_analysis(sub_path=i)
            sentiment.sentiment_line(start='2021-12-05', end='2021-12-25', sub_path=i)


if __name__ == '__main__':
    spider = Spider()
    keys = ['浙世界那么多人抗疫mv', '宁波疫情']
    spider.task(words=keys)


