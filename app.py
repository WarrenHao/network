# import streamlit as st
# import networkx as nx
# import matplotlib.pyplot as plt
# import numpy as np



import streamlit as st
import pandas as pd
import networkx as nx
import EoN
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from pyecharts.charts import Line
from pyecharts import options as opts
from streamlit_echarts import st_echarts
import matplotlib.pyplot as plt
from pyecharts.charts import Graph
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import numpy as np
import streamlit_echarts
from WeiboSpider.weibospider.config import INPUT_TASK

import pandas as pd
import glob
import DataLoader
from drawer import drawer


dl = DataLoader.Dataloader()


tweets_keyword_df = dl.load_newest_file('tweet_spider_by_keyword')
tweets_id_df = dl.load_newest_file('tweet_spider_by_tweet_id')

user_info = dl.load_newest_file('user_spider')

tweets_info = pd.concat([tweets_keyword_df, tweets_id_df], axis=0)
tweets_info['user_id'] = tweets_info['user'].apply(lambda x: x['_id']).astype(str)


source_tweets = tweets_info.copy()
source_tweets = source_tweets[['_id', 'user_id', 'content', 'created_at', 'ip_location', 'reposts_count', 'comments_count', 'attitudes_count']]
source_tweets = source_tweets.rename(columns={'_id': 'source_id', 
                                              'user_id': 'source_user_id', 
                                              'content': 'source_content', 
                                              'created_at': 'source_created_at', 
                                              'ip_location': 'source_ip_location',
                                              'reposts_count': 'source_reposts_count',
                                              'comments_count': 'source_comments_count',
                                              'attitudes_count': 'source_attitudes_count'})
tweets_with_source_link = pd.merge(tweets_info, source_tweets, left_on='retweet_id', right_on='source_id', how='left')

tweets_with_source_link = tweets_with_source_link[['user_id', 'source_user_id', 'created_at', 'ip_location', 'reposts_count', 'comments_count', 'attitudes_count',
                                                    'source_created_at', 'source_ip_location', 'source_reposts_count', 'source_comments_count', 'source_attitudes_count']]

# 增加user_info
user_info = user_info.rename(columns={'_id': 'user_id'})
user_info['user_id'] = user_info['user_id'].astype(str)
source_user_info = user_info.copy()
source_user_info = source_user_info[['user_id', 'followers_count', 'friends_count', 'statuses_count', 'nick_name']]
source_user_info = source_user_info.rename(columns={'user_id': 'source_user_id', 
                                                    'followers_count': 'source_followers_count', 
                                                    'friends_count': 'source_friends_count', 
                                                    'statuses_count': 'source_statuses_count',
                                                    'nick_name': 'source_nick_name'})
user_info = user_info[['user_id', 'followers_count', 'friends_count', 'statuses_count', 'nick_name']]


tweets_with_source_link_user_info = pd.merge(tweets_with_source_link, user_info, on='user_id', how='left')

# 增加user_info
tweets_with_source_link_source_user_info = pd.merge(tweets_with_source_link_user_info, source_user_info, on='source_user_id', how='left')
tweets_with_source_link_source_user_info['created_at'] = tweets_with_source_link_source_user_info['created_at'].str[0:10]
tweets_with_source_link_source_user_info['created_at'] = pd.to_datetime(tweets_with_source_link_source_user_info['created_at'])


'''
### 一、关系网络搭建
1. 用户关系网络的搭建基于事件中帖子的转发关系，如果一篇帖子被另一个人转发，则转发的用户与源帖子的拥有用户构成一次转发关系
2. 构建的关系网络中，节点为用户，用户之间依靠转发关系构建联系
3. 网络节点存在影响力大小，此处主要提供三大指标
    - 用户在该事件中所有帖子的转发量总和
    - 用户在该事件中所有帖子的点赞量总和
    - 用户的粉丝基数
影响力最终由这三个指标加权得到，作为节点的大小
4. 网络节点的重要性指标计算
    - 节点的度中心性
    - 节点的介数中心性
    - 节点的紧密中心性

中心性越高，说明节点的重要性越高
'''
if st.button('绘制事件传播网络图'):
    c = drawer(tweets_with_source_link_source_user_info, INPUT_TASK['KEYWORDS'][0])
    
    # 把网络图对象渲染到 Streamlit
    streamlit_echarts.st_pyecharts(
        c,
        width=1000,
        height=500,
        renderer='svg'
    )


''''
### 二、S-I-R传播模型

#### introduction
SIR模型是最早的传染病传播模型之一，它是一个基于微分方程的传染病传播模型，由三个状态方程组成，分别是易感者(S)，感染者(I)和康复者(R)。SIR模型是一个典型的动力学模型，它描述了传染病在人群中的传播过程。
在信息传播领域，SIR模型也被广泛应用于舆情传播、情感传播等研究中。此时，SIR模型中的易感者、感染者和康复者分别对应了信息传播中的未接触者、接触者和传播者。
SIR模型的基本假设是：人群中的每个个体都是同质的，即每个个体的易感性、感染性和康复性都是相同的。此外，SIR模型还假设人群是封闭的，即人群中的个体不会因为外部因素而增加或减少。
具体的传播形式如下：
S(t+1) = S(t) - β * S(t) * I(t)
I(t+1) = I(t) + β * S(t) * I(t) - γ * I(t)
R(t+1) = R(t) + γ * I(t)

##### 参数说明
S(t)：健康人数
I(t)：感染人数
R(t)：康复人数
β：感染率
γ：康复率
'''

'''
### references

[1] 郑志蕴, 郭芳, 王振飞, 等. 基于行为分析的微博传播模型研究[J]. 计算机科学, 2016, 43(12): 41-45.\n
[2] 魏静, 黄阳, 江豪, 等. 基于改进 SIR 模型的微博网络舆情传播研究[J]. 情报科学, 2019, 37(6): 16-22.\n
[3] 徐沛东, 马力, 李培. 基于 SIR 模型的情感网络传播分析[J]. 计算机与数字工程, 2018, 46(4): 659-662.

'''




st.title('动态SIR模型可视化')

# 设置模型参数
beta = st.slider('传播率 beta', min_value=0.01, max_value=1.0, value=0.3)
gamma = st.slider('恢复率 gamma', min_value=0.01, max_value=1.0, value=0.01)
tmax = st.slider('模拟时间 tmax', min_value=10, max_value=400, value=10)

# 执行模拟
if st.button('运行模拟'):
    G = nx.DiGraph()
    for index, row in tweets_with_source_link_source_user_info.iterrows():
        if pd.notna(row['source_nick_name']):
            G.add_edge(row['source_nick_name'], row['nick_name'], time=row['created_at'])

    # 生成传播网络，最早时间最先感染
    tweets_with_source_link_source_user_info_not_na = tweets_with_source_link_source_user_info.dropna(subset=['source_nick_name'])
    tweets_with_source_link_source_user_info_not_na.sort_values(by='created_at', inplace=True)
    initial_infecteds = tweets_with_source_link_source_user_info_not_na.head(40)['nick_name'].to_list()
    # initial_infecteds = [node for node in G.nodes if G.degree(node) >= 0.5]
    status = {node: 'Susceptible' for node in G.nodes()}  # 初始化状态为易感
    for node in initial_infecteds:
        status[node] = 'Infected'  # 更新初始感染者状态
    sim_fl = EoN.fast_SIR(G, tau=beta, gamma=gamma, initial_infecteds=initial_infecteds, tmax=tmax, return_full_data=True)
    sim = EoN.fast_SIR(G, tau=beta, gamma=gamma, initial_infecteds=initial_infecteds, tmax=tmax)
    # 更新每个节点的最终状态
    
    for t, node, stu in sim_fl.transmissions():
        if stu == 'I':
            status[node] = 'Infected'
        elif stu == 'R':
            status[node] = 'Recovered'

    # 节点颜色映射
    colors = {'Susceptible': 'blue', 'Infected': 'green', 'Recovered': 'orange'}

    # 创建图表
    nodes = [{'name': str(node), 'symbolSize': 10, 'itemStyle': {'color': colors[status[node]]}} for node in G.nodes()]
    links = [{'source': str(source), 'target': str(target)} for source, target in G.edges()]
    graph = Graph()
    graph.add("", nodes, links, repulsion=5000)
    graph.set_global_opts(title_opts=opts.TitleOpts(title="Dynamic SIR Model on Network"))
    graph.set_series_opts(label_opts=opts.LabelOpts(is_show=False))


    streamlit_echarts.st_pyecharts(graph, height=500, width=1000)


    # 获取结果
    times, S, I, R = sim

    # 为未来趋势绘图
    line_chart = Line()
    line_chart.add_xaxis(times.tolist())
    line_chart.add_yaxis("Susceptible", S.tolist())
    line_chart.add_yaxis("Infected", I.tolist())
    line_chart.add_yaxis("Recovered", R.tolist())
    line_chart.set_global_opts(title_opts=opts.TitleOpts(title="SIR Model Future Trend Prediction"),
                            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"))

    line_chart.set_global_opts(title_opts=opts.TitleOpts(title="SIR Model Future Trend Prediction"),
                               datazoom_opts=opts.DataZoomOpts())  # 启用数据缩放功能)
    # 增加缩放功能

    streamlit_echarts.st_pyecharts(line_chart, height=500, width=1000)
