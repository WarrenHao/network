import pandas as pd
import numpy as np
import networkx as nx
from pyecharts.charts import Graph
from pyecharts import options as opts



def drawer(data:pd.DataFrame, name):
    G = nx.DiGraph()

    for _, row in data.iterrows():
        G.add_node(row['user_id'], label=row['nick_name'], size=row['followers_count'])
        if pd.notna(row['source_user_id']):
            G.add_node(row['source_user_id'], label=row['source_nick_name'], size=row['source_followers_count'])
            G.add_edge(row['source_user_id'], row['user_id'])

    # 假设 G 是已经创建的 networkx 图对象
    degree_centrality = nx.degree_centrality(G)

    # 为了突出显示中心性较高的节点，可以设置一个阈值
    # 这里假设我们把度中心性高于平均值的节点视为中心节点
    import numpy as np
    threshold = np.quantile(list(degree_centrality.values()), 0.8)

    low_fans_threshold = np.percentile([G.nodes[node]['size'] for node in G.nodes], 33)
    high_fans_threshold = np.percentile([G.nodes[node]['size'] for node in G.nodes], 66)

    nodes = []
    for node in G.nodes:
        fans = G.nodes[node]['size']
        centrality = degree_centrality[node]
        if centrality > threshold:
            color = 'rgba(237,25,65, 0.95)'  # 红色，中心性高
        elif fans < low_fans_threshold:
            color = 'rgba(0, 0, 255, 0.8)'  # 蓝色，粉丝数较低
        elif fans > high_fans_threshold:
            color = 'rgba(243,112,75, 0.7)'  # 淡红色，粉丝数较高
        else:
            color = 'rgba(119,172,152,0.8)'  # 绿色，粉丝数中等

        nodes.append({
            'name': G.nodes[node]['label'],
            'symbolSize': G.nodes[node]['size'] / 1000000 if G.nodes[node]['size'] > 1000000 else G.nodes[node]['size'] / 15000,
            'itemStyle': {'color': color}
        })

    links = [{'source': G.nodes[u]['label'], 'target': G.nodes[v]['label'], 
            'lineStyle': {"normal": {"color": '#afb0b2', "curveness": 0.5}}}
            for u, v in G.edges]

    c = (
        Graph()
        .add(

            "",
            nodes,
            links,
            edge_symbol=['circle', 'arrow'],
            edge_symbol_size=5,  # 调整为更合适的大小
            repulsion=150,
            linestyle_opts=opts.LineStyleOpts(curve=0.2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            # title_opts=opts.TitleOpts(title=f"{INPUT_TASK['KEYWORDS'][0]}微博转发关系图"),            
        )
    )

    # 工具箱功能增强
    c.set_global_opts(
        title_opts=opts.TitleOpts(title=f"{name}微博转发关系图"),
        toolbox_opts=opts.ToolboxOpts(is_show=True, feature=opts.ToolBoxFeatureOpts(
            save_as_image={"show": True, "title": "Save Image"},
            restore={"show": True, "title": "Restore"},
            data_zoom={"show": True, "title": "Zoom In/Out"},
            magic_type={"show": True, "type": ["line", "bar"]})
        )
    )

    return c
