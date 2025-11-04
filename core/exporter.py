"""
结果导出模块 - 生成Excel格式的比对结果
"""
import pandas as pd
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


def export_to_excel(results, output_folder):
    """
    将比对结果导出为 Excel 文件

    Args:
        results: 比对结果字典 (来自 ComparisonEngine.generate_report())
        output_folder: 输出目录路径

    Returns:
        str: 生成的文件路径

    Raises:
        Exception: 导出失败
    """
    try:
        # 生成文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'比对结果_{timestamp}.xlsx'
        filepath = os.path.join(output_folder, filename)

        # 使用 xlsxwriter 引擎创建 Excel
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            # 写入单机多出人员
            if 'local_extra' in results and not results['local_extra'].empty:
                results['local_extra'].to_excel(
                    writer,
                    sheet_name='单机多出人员',
                    index=False
                )
                logger.info(f"已写入 '单机多出人员' Sheet, "
                          f"{len(results['local_extra'])} 条记录")
            else:
                # 空结果也创建 Sheet (仅表头)
                pd.DataFrame(columns=['无数据']).to_excel(
                    writer,
                    sheet_name='单机多出人员',
                    index=False
                )

            # 写入全国多出人员
            if 'national_extra' in results and not results['national_extra'].empty:
                results['national_extra'].to_excel(
                    writer,
                    sheet_name='全国多出人员',
                    index=False
                )
                logger.info(f"已写入 '全国多出人员' Sheet, "
                          f"{len(results['national_extra'])} 条记录")
            else:
                pd.DataFrame(columns=['无数据']).to_excel(
                    writer,
                    sheet_name='全国多出人员',
                    index=False
                )

            # 写入各字段差异
            diff_fields = [
                '姓名', '性别', '民族', '出生日期',
                '学历', '入党时间', '个人身份', '人员类别'
            ]

            for field in diff_fields:
                diff_key = f'diff_{field}'
                sheet_name = f'{field}差异'

                if diff_key in results and not results[diff_key].empty:
                    results[diff_key].to_excel(
                        writer,
                        sheet_name=sheet_name,
                        index=False
                    )
                    logger.info(f"已写入 '{sheet_name}' Sheet, "
                              f"{len(results[diff_key])} 条记录")
                else:
                    # 空差异也创建 Sheet
                    pd.DataFrame(columns=[
                        '姓名', '身份证号', '单机表信息', '全国表信息'
                    ]).to_excel(
                        writer,
                        sheet_name=sheet_name,
                        index=False
                    )

            # 获取 workbook 以设置格式
            workbook = writer.book

            # 定义表头格式（加粗）
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#D9E1F2'
            })

            # 应用表头格式到所有工作表
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # 设置表头格式
                for col_num, value in enumerate(
                    results.get('local_extra', pd.DataFrame()).columns
                ):
                    worksheet.write(0, col_num, value, header_format)

                # 自动调整列宽
                worksheet.set_column(0, 10, 15)

        logger.info(f"比对结果已导出: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"导出 Excel 失败: {e}")
        raise


def format_date_columns(df, date_columns):
    """
    格式化 DataFrame 中的日期列

    Args:
        df: DataFrame
        date_columns: 日期列名列表

    Returns:
        DataFrame: 格式化后的 DataFrame
    """
    df_copy = df.copy()

    for col in date_columns:
        if col in df_copy.columns:
            try:
                df_copy[col] = pd.to_datetime(
                    df_copy[col],
                    errors='coerce'
                ).dt.strftime('%Y-%m-%d')

                # 将 NaT 转换为空字符串
                df_copy[col] = df_copy[col].fillna('')
            except Exception as e:
                logger.warning(f"格式化日期列 '{col}' 失败: {e}")

    return df_copy
