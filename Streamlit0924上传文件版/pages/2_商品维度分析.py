import streamlit as st
import pandas as pd
import datahandle
import datetime
from datahandle import Data_Handle


# 设置侧边栏选项卡
with st.sidebar:
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
    df_useful_panel = df_useful.query('订单状态 == @order_status and 订单时间 >= @start and 订单时间 <= @end')
    vendor_number = st.multiselect(
    "选择供应商编码", 
    options=df_useful['供应商编码'].unique(),
    default='A0001', 
)
    df_2 = df_useful_panel.query('供应商编码 == @vendor_number')
    sort = st.multiselect(
        "选择分类", 
        options=df_2['分类'].unique(),
        default=df_2['分类'].unique(), 
    )
    df_3 = df_2.query('分类 == @sort')
    itemsku = st.multiselect(
        "选择SKU", 
        options=df_3['平台SKU'].unique()
    )

# 整理仪表盘所需数据
total_sales = df_useful_panel['总销售额'].sum()
order_number = df_useful_panel['订单号'].count()
order_price = df_useful_panel['总销售额'].mean()

# 仪表盘网页布局
col1, col2, col3 = st.columns(3)
col1.metric("销售金额", '%.2f' %total_sales)
col2.metric("订单数量", order_number)
col3.metric("客单价", '%.2f' %order_price)
