import pandas as pd
import pandas_bokeh

### 文件路径D:/文件调用
# Path1 = 'D:/文件调用/01.原始数据/02.订单/KD订单导出数据.csv'
Path2 = 'D:/文件调用/01.原始数据/04.匹配信息用表/Kadehome商品总表.xlsx'
Path3 = 'D:/文件调用/01.原始数据/04.匹配信息用表/国家洲名称转换.xlsx'


def data_handle(Path1):
    df_order = pd.read_csv(Path1, encoding = 'utf-8')
    df_items = pd.read_excel(Path2)
    df_Statename = pd.read_excel(Path3)

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
    df_order['总销售额'] = df_order['销售数量']*df_order['商品单价']
    df_order.head(3)

    # 合并数据：供应商编码，供应商SKU，洲名称转换
    df_merge = pd.merge(df_order, df_items, on="平台SKU", how="left")
    df_merge.head(3)

    # 导出标准化Dataframe，用于后续数据分析
    df_use = df_merge[
        ['订单号', '订单时间', '订单状态','分类','平台SKU', '唯非SKU',
        '供应商SKU','供应商编码','商品单价','销售数量','总销售额', '目的地所属州']
        ] 
    df_useful = df_use.dropna(axis=0, how="any")
    return df_useful