import streamlit as st
import pandas as pd
import datetime
import json
import plotly.express as px
from chart import get_chart

# 准备调用的文件
file = open('data/features.geojson','r',encoding='utf-8')                     #### 绘制地图专用
counties = json.load(file)
df_Statename = pd.read_excel('data/国家洲名称转换.xlsx')

# 设置侧边栏
with st.sidebar:
    uploaded_file1 = st.file_uploader('上传订单文件')
    if uploaded_file1 is not None:
        # Can be used wherever a "file-like" object is accepted:
        df_order = pd.read_csv(uploaded_file1)
    else:
        df_order = pd.read_csv('data/KD订单导出数据.xlsx')
#         st.info(
#             f"""
#                 👆 上传原始订单文件
#                 """
#         )

#         st.stop() 

    uploaded_file2 = st.file_uploader('上传匹配文件')
    if uploaded_file2 is not None:
        # Can be used wherever a "file-like" object is accepted:
        df_items = pd.read_excel(uploaded_file2) 
    else:
         df_items = pd.read_excel('data/Kadehome商品总表.xlsx') 
#         st.info(
#             f"""
#                 👆 上传匹配文件
#                 """
#         )

#         st.stop()
    
    # 处理上传的文件
    # 标准化原始订单的列名称 --- 用于处理Wayfair原始订单
    df_order = df_order.rename(
        columns={'PO Number':'订单号',
                'PO Date':'订单时间',
                'Order Status':'订单状态',
                'Item Number':'平台SKU',
                'Wholesale Price':'商品单价',
                'Quantity':'销售数量',
                'Ship To State':'目的地所属州'}
        )

    # 整理数据格式：去掉字符串多余符号，调整日期格式，计算总销售额 --- 用于处理Wayfair原始订单
    df_order.loc[:,'平台SKU'] = df_order['平台SKU'].str.replace('"','')
    df_order.loc[:,'平台SKU'] = df_order['平台SKU'].str.replace('=','')
    df_order.loc[:,'订单时间'] = pd.to_datetime(df_order['订单时间'], format="%m/%d/%Y")
    df_order.loc[:,'订单时间_月'] = df_order['订单时间'].dt.strftime('%Y-%m')
    df_order['总销售额'] = df_order['销售数量']*df_order['商品单价']
    df_order.head(3)

    # 合并数据：供应商编码，供应商SKU，洲名称转换
    df_merge = pd.merge(df_order, df_items, on="平台SKU", how="left")
    df_merge.head(3)

    # 导出标准化Dataframe，用于后续数据分析
    df_use = df_merge[
        ['订单号', '订单时间', '订单时间_月', '订单状态','分类','平台SKU', '唯非SKU',
        '供应商SKU','供应商编码','商品单价','销售数量','总销售额', '目的地所属州']
        ] 
    df_useful = df_use.dropna(axis=0, how="any")
    
    # 设置侧边栏的筛选条件
    start = st.date_input(
        "选择开始日期",
        datetime.date(2022, 1, 1))
    end = st.date_input(
        "选择结束日期",
        datetime.date(2022, 9, 1))
    order_status = st.multiselect(
    "选择订单状态", 
    options=df_useful['订单状态'].unique(),
    default='Shipped', 
    )

# 按照侧边栏筛选结果整理所需数据
df_useful_panel = df_useful.query('订单状态 == @order_status and 订单时间 >= @start and 订单时间 <= @end')

# 整理仪表盘数据
total_sales = df_useful_panel['总销售额'].sum()
order_number = df_useful_panel['订单号'].count()
order_price = df_useful_panel['总销售额'].mean()

# 整理表格数据
df_vendor = df_useful_panel.groupby(['供应商编码'],as_index=False)['总销售额'].sum().sort_values(by = '总销售额',ascending=False)
df_vendor = df_vendor.reset_index(drop=True)
df_item = df_useful_panel.groupby(['平台SKU'],as_index=False)['总销售额'].sum().sort_values(by = '总销售额',ascending=False)
df_item = df_item.reset_index(drop=True)

# 整理地图数据
df_State = df_useful_panel.目的地所属州.value_counts().rename_axis('目的地所属州').reset_index(name='counts')
df_State_useful = pd.merge(df_State, df_Statename, on="目的地所属州", how="left")
df_State_useful.head()
px.set_mapbox_access_token(token=st.secrets["token"])
fig = px.choropleth_mapbox(df_State_useful, geojson=counties, locations='statename', color='counts',
                           color_continuous_scale='RdBu',
                           # range_color=(0, 200),
                           mapbox_style="streets",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# 整理折线图数据
df_line = df_useful_panel.groupby(['订单时间'],as_index=False)['总销售额'].sum()
chart = get_chart(df_line)

# 整理条形图数据
df_bar = df_useful_panel.groupby(['订单时间_月','分类'],as_index=False)['总销售额'].sum()
fig_bar = px.bar(df_bar, x="订单时间_月", y="总销售额", color="分类", text='分类')

# 整理树形图数据
fig_tree = px.treemap(df_useful_panel, path=[px.Constant("总"), '分类', '供应商编码', '平台SKU'], 
                 values='总销售额',
                 maxdepth = 2)

# 网页布局
st.header('一、店铺整体销售情况')

with st.expander("查看原始数据处理结果"):
    st.write("原始数据处理结果")
    st.write(df_useful_panel)

st.subheader('1.销售金额、订单数据和客单价')
col1, col2, col3 = st.columns(3)
col1.metric("销售金额", '%.2f' %total_sales)
col2.metric("订单数量", order_number)
col3.metric("客单价", '%.2f' %order_price)

st.subheader('2.热销SKU、供应商')
col1, col2 = st.columns(2)
col1.dataframe(df_item,height=210)
col2.dataframe(df_vendor,height=210)

st.subheader('3.订单分布')
st.plotly_chart(fig, use_container_width=True)

st.subheader('4.销售曲线')
st.altair_chart(chart, use_container_width=True)

st.subheader('5.月销售分类占比')
st.plotly_chart(fig_bar, use_container_width=True)

st.header('二、商品销售分析')

st.subheader('1.商品销售占比分布')
st.plotly_chart(fig_tree, use_container_width=True)

# st.subheader('2.帕累托图')

st.subheader('2.商品对比分析')
vendor_number = st.multiselect(
    "选择供应商编码", 
    options=df_useful['供应商编码'].unique(),
)
df_2 = df_useful_panel.query('供应商编码 == @vendor_number')

sort = st.multiselect(
    "选择分类", 
    options=df_2['分类'].unique(),
    default=df_2['分类'].unique(), 
    )
df_3 = df_2.query('分类 == @sort')

# 供应商维度分析
df_vendor_line = df_3.groupby(['订单时间_月','分类','供应商编码'],as_index=False)['总销售额'].sum()
fig_vendor_bar = fig = px.bar(df_vendor_line, x="订单时间_月", y="总销售额",
                                  color='供应商编码', barmode='group')
st.plotly_chart(fig_vendor_bar)


# SKU维度分析
itemsku = st.multiselect(
    "选择SKU", 
    options=df_3['平台SKU'].unique()
    )
df_4 = df_3.query('平台SKU == @itemsku')
df_item_line = df_4.groupby(['订单时间_月','分类','供应商编码','平台SKU'],as_index=False)['总销售额'].sum()
fig_item_bar = fig = px.bar(df_item_line, x="订单时间_月", y="总销售额",
                                  color='平台SKU', barmode='group')

st.plotly_chart(fig_item_bar)
with st.expander("查看供应商筛选结果"):
    st.write(df_vendor_line)
    
with st.expander("查看商品筛选结果"):
    st.write(df_item_line)
