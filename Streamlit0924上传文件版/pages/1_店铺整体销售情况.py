import streamlit as st
import json
import datetime
import pandas as pd
from datahandle import data_handle
import plotly.express as px

file = open('D:/文件调用/美国洲分布json文件/features.geojson','r',encoding='utf-8') #### 绘制地图专用
counties = json.load(file)
df_Statename = pd.read_excel('D:/文件调用/01.原始数据/04.匹配信息用表/国家洲名称转换.xlsx')

# 设置侧边栏选项卡
with st.sidebar:
    uploaded_file = st.file_uploader('上传订单文件')
    if uploaded_file is not None:
        # Can be used wherever a "file-like" object is accepted:
        df_useful = data_handle(uploaded_file)
    else:
        st.info(
            f"""
                👆 上传原始订单文件
                """
        )

        st.stop()
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

# 整理页面所需数据
# 整理仪表盘所需数据
df_useful_panel = df_useful.query('订单状态 == @order_status and 订单时间 >= @start and 订单时间 <= @end')
total_sales = df_useful_panel['总销售额'].sum()
order_number = df_useful_panel['订单号'].count()
order_price = df_useful_panel['总销售额'].mean()

# 整理地图数据
df_State = df_useful_panel.目的地所属州.value_counts().rename_axis('目的地所属州').reset_index(name='counts')
df_State_useful = pd.merge(df_State, df_Statename, on="目的地所属州", how="left")
df_State_useful.head()
px.set_mapbox_access_token(token=st.secrets["token"])
fig = px.choropleth_mapbox(df_State_useful, geojson=counties, locations='statename', color='counts',
                           color_continuous_scale="Viridis",
                           range_color=(0, 200),
                           mapbox_style="streets",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# 整理折线图数据
df_line = df_line = df_useful_panel.groupby(['订单时间'],as_index=False)['总销售额'].sum()
fig_line = px.line(df_line, x='订单时间', y='总销售额')


# 整理表格数据
df_vendor = df_useful_panel.groupby(['供应商编码'],as_index=False)['总销售额'].sum().sort_values(by = '总销售额',ascending=False)
df_vendor = df_vendor.reset_index(drop=True)
df_item = df_useful_panel.groupby(['平台SKU'],as_index=False)['总销售额'].sum().sort_values(by = '总销售额',ascending=False)
df_item = df_item.reset_index(drop=True)

# 仪表盘网页布局
st.header('一、店铺整体销售情况')

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
st.plotly_chart(fig)

st.subheader('4.销售曲线')
st.plotly_chart(fig_line)

st.subheader('5.原始数据')
st.write(df_useful_panel)
