import re
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import config as cfg
from util import getWord
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False   #这两行需要手动设置

class KmeansClustering():
    def __init__(self, stopwords_path=None):
        """
        # 聚类k-means分析
        # 2.生成关键词矩阵
        # 3.k-means聚类结果
        :param stopwords_path:
        """
        # self.stopwords = self.load_stopwords(stopwords_path)
        self.corpus = None
        self.vectorizer = CountVectorizer()
        self.transformer = TfidfTransformer()

    # 数据集处理函数
    @staticmethod
    def chinese_word_cut(mytext):
        stopword_list = open(cfg.static_path + '/baidu_stopwords.txt', encoding='utf-8')
        stop_list = []
        for line in stopword_list:
            line = re.sub(u'\n|\\r', '', line)
            stop_list.append(line)
        list = jieba.lcut(mytext, cut_all=True)
        for w in list:
            if w in stop_list:
                list.remove(w)
        str = ' '.join(list)
        return str

    # 1.微博数据处理，文本段落划分，提取出关键词
    def data_resolve(self, corpus_path):
        df = pd.read_excel(corpus_path)
        df = df['text']
        df = df.apply(getWord)
        df['cutted'] = df.apply(self.chinese_word_cut)
        self.corpus = df['cutted']
        return df['cutted']

    def load_stopwords(self, stopwords=None):
        """
        加载停用词
        :param stopwords:
        :return:
        """
        if stopwords:
            with open(stopwords, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        else:
            return []

    def preprocess_data(self, corpus_path):
        """
        文本预处理，每行一个文本
        :param corpus_path:
        :return:
        """
        corpus = []
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                corpus.append(' '.join([word for word in jieba.lcut(line.strip()) if word not in self.stopwords]))
        return corpus

    def get_text_tfidf_matrix(self, corpus):
        """
        获取tfidf矩阵
        :param corpus:
        :return:
        """
        tfidf = self.transformer.fit_transform(self.vectorizer.fit_transform(corpus))

        # 获取词袋中所有词语
        # words = self.vectorizer.get_feature_names()

        # 获取tfidf矩阵中权重
        weights = tfidf.toarray()
        return weights

    def kmeans(self, corpus_path, n_clusters=5):
        """
        KMeans文本聚类
        :param corpus_path: 语料路径（每行一篇）,文章id从0开始
        :param n_clusters: ：聚类类别数目
        :return: {cluster_id1:[text_id1, text_id2]}
        """
        # corpus = self.preprocess_data(corpus_path)
        corpus = self.data_resolve(corpus_path)
        weights = self.get_text_tfidf_matrix(corpus)

        clf = KMeans(n_clusters=n_clusters)

        # clf.fit(weights)

        y = clf.fit_predict(weights)
        self.toView(clf,weights)
        self.toView2(clf,weights)
        # 中心点
        # centers = clf.cluster_centers_

        # 用来评估簇的个数是否合适,距离约小说明簇分得越好,选取临界点的簇的个数
        score = clf.inertia_
        print(score)
        # 每个样本所属的簇
        result = {}
        for text_idx, label_idx in enumerate(y):
            if label_idx not in result:
                result[label_idx] = [text_idx]
            else:
                result[label_idx].append(text_idx)
        return result

    def toView(self,k_means,tfidf_weight):
        # 使用T-SNE算法，对权重进行降维，准确度比PCA算法高，但是耗时长
        tsne = TSNE(n_components=2)
        decomposition_data = tsne.fit_transform(tfidf_weight)

        x = []
        y = []

        for i in decomposition_data:
            x.append(i[0])
            y.append(i[1])

        fig = plt.figure(figsize=(8, 5))
        # ax = plt.axes()
        plt.scatter(x, y, c=k_means.labels_, marker="x")
        plt.xticks(())
        plt.yticks(())
        plt.savefig(cfg.static_path+'/sample.png')
        plt.show()

    # extern
    def labels_to_original(self,labels, forclusterlist):
        assert len(labels) == len(forclusterlist)
        maxlabel = max(labels)
        numberlabel = [i for i in range(0, maxlabel + 1, 1)]
        numberlabel.append(-1)
        result = [[] for i in range(len(numberlabel))]
        for i in range(len(labels)):
            index = numberlabel.index(labels[i])
            result[index].append(forclusterlist[i])
        return result

    def toView2(self,k_means,tfidf_weight):
        clf = k_means
        # 每个样本所属的簇
        label = []
        i = 1
        while i <= len(clf.labels_):
            label.append(clf.labels_[i - 1])
            i = i + 1
        # 获取标签聚类
        y_pred = clf.labels_

        tsne = TSNE(n_components=2)
        decomposition_data = tsne.fit_transform(tfidf_weight)

        xs, ys = decomposition_data[:, 0], decomposition_data[:, 1]
        # 设置颜色
        cluster_colors = {0: 'r', 1: 'yellow', 2: 'b', 3: 'chartreuse', 4: 'purple', 5: '#FFC0CB', 6: '#6A5ACD',
                          7: '#98FB98'}

        # 设置类名
        cluster_names = {0: u'类0', 1: u'类1', 2: u'类2', 3: u'类3', 4: u'类4', 5: u'类5', 6: u'类6', 7: u'类7'}

        df = pd.DataFrame(dict(x=xs, y=ys, label=y_pred, title=self.corpus))
        groups = df.groupby('label')

        fig, ax = plt.subplots(figsize=(8, 5))  # set size
        ax.margins(0.02)
        for name, group in groups:
            ax.plot(group.x, group.y, marker='o', linestyle='', ms=10, label=cluster_names[name],
                    color=cluster_colors[name], mec='none')
        plt.show()

        res = self.labels_to_original(y_pred, self.corpus)
        for i in range(len(res)):
            for j in range(len(res[i][0:5])):
                print(res[i][j])
            print("=======================")


if __name__ == '__main__':
    Kmeans = KmeansClustering(stopwords_path=cfg.static_path+'/baidu_stopwords.txt')
    result = Kmeans.kmeans(cfg.data_path+'/mblog.xlsx', n_clusters=3)
    # print(result)
