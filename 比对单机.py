import pandas as pd
单机库 = '表格/党员列表(导出数据)20251108215654.xls'
全国库 = '表格/中共晋能控股煤业集团燕子山矿委员会.xls'
# 读取两个Excel文件
df_dangyuan = pd.read_excel(单机库)
df_yanzishan = pd.read_excel(全国库, sheet_name='1')

# 处理“单机”表
df_dangyuan['序号'] = range(1, len(df_dangyuan) + 1)  # 增加序号列
df_dangyuan['党龄'] = (pd.to_datetime('2025-12-31') - pd.to_datetime(df_dangyuan['入党时间'])).dt.days // 365  # 计算党龄
df_dangyuan['年龄'] = (pd.to_datetime('2025-12-31') - pd.to_datetime(df_dangyuan['身份证号'].str[6:14],
                                                                     format='%Y%m%d')).dt.days // 365  # 计算年龄
df_dangyuan['人员类别'] = df_dangyuan['入党时间'].apply(
    lambda x: '预备党员' if str(x).startswith('2025') else '正式党员')  # 判断人员类别

# 处理“1”表
df_yanzishan['序号'] = range(1, len(df_yanzishan) + 1)  # 增加序号列
df_yanzishan['党龄'] = (pd.to_datetime('2025-12-31') - pd.to_datetime(df_yanzishan['入党日期'])).dt.days // 365  # 计算党龄
df_yanzishan['年龄'] = (pd.to_datetime('2025-12-31') - pd.to_datetime(df_yanzishan['身份证号码'].str[6:14],
                                                                      format='%Y%m%d')).dt.days // 365  # 计算年龄

# 身份证号处理
df_dangyuan['身份证号'] = df_dangyuan['身份证号'].str.upper().astype(str)
df_yanzishan['身份证号码'] = df_yanzishan['身份证号码'].str.upper().astype(str)

# 对比两表中的身份证号，找出不同的条目
df_dangyuan_extra = df_dangyuan[~df_dangyuan['身份证号'].isin(df_yanzishan['身份证号码'])]
df_yanzishan_extra = df_yanzishan[~df_yanzishan['身份证号码'].isin(df_dangyuan['身份证号'])]

# 创建新的工作表并保存结果
with pd.ExcelWriter(全国库, engine='xlsxwriter') as writer:
    df_dangyuan.to_excel(writer, sheet_name='单机', index=False)
    df_yanzishan.to_excel(writer, sheet_name='1', index=False)
    df_dangyuan_extra.to_excel(writer, sheet_name='单机多', index=False)
    df_yanzishan_extra.to_excel(writer, sheet_name='单机少', index=False)

    df_dangyuan = df_dangyuan.add_suffix('_dangyuan')
    df_dangyuan = df_dangyuan.rename(columns={'身份证号_dangyuan': '身份证号'})
    df_yanzishan = df_yanzishan.add_suffix('_yanzishan')
    df_yanzishan = df_yanzishan.rename(columns={'身份证号码_yanzishan': '身份证号码'})

    # 找出身份证号相同但其他信息不同的记录
    for column in ['姓名', '性别', '民族', '出生日期', '学历', '入党时间', '个人身份', '人员类别']:
        if column == '入党时间':
            column_1 = '入党日期'
        elif column == '个人身份':
            column_1 = '工作岗位'
        else:
            column_1 = column
        df_diff = pd.merge(df_dangyuan, df_yanzishan, left_on='身份证号', right_on='身份证号码')
        df_diff = df_diff[df_diff[f'{column}_dangyuan'] != df_diff[f'{column_1}_yanzishan']][
            ['姓名_dangyuan', '身份证号', f'{column}_dangyuan', f'{column_1}_yanzishan']]
        df_diff.columns = ['姓名', '身份证号', '单机表信息', '1表信息']
        df_diff.to_excel(writer, sheet_name=f'{column}差异', index=False)


print("处理完成")