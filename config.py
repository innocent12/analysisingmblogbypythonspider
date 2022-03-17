import os

# 工作目录
path = os.getcwd()
data_path = path + '/data'
static_path = path + '/static'
dataColumn = {'comment': ['id', 'created_at', 'text', 'source', 'floor_number', 'like_count', 'rootid', 'mid'],
              'userinfo': ['id', 'screen_name', 'profile_url', 'gender', 'followers_count', 'follow_count',
                           'statuses_count'],
              'mblog': ['id', 'mid', 'created_at', 'text', 'source', 'reposts_count', 'comments_count',
                        'attitudes_count', 'origin']}
origin_record = []

# 设置heades
headers = {
    'Cookie': '',
    'Referer': 'no-referer',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

weibo_api = {
    'base_url': 'https://m.weibo.cn/api/container/getIndex?containerid=100103type{0}&page_type=searchall',
    'referer_url': 'https://m.weibo.cn/search?containerid=100103type{0}',
    'user_url': 'https://m.weibo.cn/api/container/getIndex?uid={0}&t=0&luicode=10000011&lfid=100103type{1}&'
                'featurecode=10000326&type=uid&value={0}&containerid=1076031878136331',
    'weibo_base_url': 'https://m.weibo.cn/api/container/getIndex?containerid=231522type',
    'comment_url': 'https://m.weibo.cn/comments/hotflow?id={0}&mid={0}&max_id_type=0',
    'comment_referer': 'https://m.weibo.cn/detail/{0}'
}

weibo_param = {
    'user_param': '=3&q={0}&t=0',
    'topic_param': '=38&q={0}&t=0',
    'referer_param': '=1&q={0}',
    'actual': '=61&q={0}',
    'hot_weibo': '=60&q={0}'
}

if __name__ == '__main__':
    print(os.getcwd())
