"""
比对引擎模块 - 党员花名册比对核心逻辑
"""
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ComparisonEngine:
    """党员花名册比对引擎"""

    # 字段映射：单机库字段 -> 全国库字段
    FIELD_MAPPING = {
        '入党时间': '入党日期',
        '个人身份': '工作岗位'
    }

    # 需要比对的字段列表
    COMPARE_FIELDS = ['姓名', '性别', '民族', '出生日期', '学历', '入党时间', '个人身份', '人员类别']

    def __init__(self, df_local, df_national):
        """
        初始化比对引擎

        Args:
            df_local: 单机库 DataFrame
            df_national: 全国库 DataFrame
        """
        self.df_local = df_local.copy()
        self.df_national = df_national.copy()
        self.results = {}

    def preprocess(self):
        """预处理数据：增加序号、计算党龄/年龄、标准化身份证号"""
        try:
            # 处理单机库
            self.df_local['序号'] = range(1, len(self.df_local) + 1)

            # 计算党龄 - 使用异常处理避免日期格式错误
            try:
                self.df_local['党龄'] = (
                    pd.to_datetime('2025-12-31') -
                    pd.to_datetime(self.df_local['入党时间'], errors='coerce')
                ).dt.days // 365
            except Exception as e:
                logger.warning(f"计算单机库党龄时出错: {e}")
                self.df_local['党龄'] = pd.NA

            # 计算年龄 - 从身份证号提取出生日期
            try:
                self.df_local['年龄'] = (
                    pd.to_datetime('2025-12-31') -
                    pd.to_datetime(
                        self.df_local['身份证号'].astype(str).str[6:14],
                        format='%Y%m%d',
                        errors='coerce'
                    )
                ).dt.days // 365
            except Exception as e:
                logger.warning(f"计算单机库年龄时出错: {e}")
                self.df_local['年龄'] = pd.NA

            # 判断人员类别
            self.df_local['人员类别'] = self.df_local['入党时间'].apply(
                lambda x: '预备党员' if str(x).startswith('2025') else '正式党员'
            )

            # 标准化身份证号
            self.df_local['身份证号'] = (
                self.df_local['身份证号']
                .astype(str)
                .str.upper()
                .str.strip()
            )

            # 处理全国库
            self.df_national['序号'] = range(1, len(self.df_national) + 1)

            # 计算党龄
            try:
                self.df_national['党龄'] = (
                    pd.to_datetime('2025-12-31') -
                    pd.to_datetime(self.df_national['入党日期'], errors='coerce')
                ).dt.days // 365
            except Exception as e:
                logger.warning(f"计算全国库党龄时出错: {e}")
                self.df_national['党龄'] = pd.NA

            # 计算年龄
            try:
                self.df_national['年龄'] = (
                    pd.to_datetime('2025-12-31') -
                    pd.to_datetime(
                        self.df_national['身份证号码'].astype(str).str[6:14],
                        format='%Y%m%d',
                        errors='coerce'
                    )
                ).dt.days // 365
            except Exception as e:
                logger.warning(f"计算全国库年龄时出错: {e}")
                self.df_national['年龄'] = pd.NA

            # 标准化身份证号
            self.df_national['身份证号码'] = (
                self.df_national['身份证号码']
                .astype(str)
                .str.upper()
                .str.strip()
            )

            logger.info("数据预处理完成")

        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            raise

    def find_differences(self):
        """
        找出多出和缺少的人员（按照原始比对单机.py的逻辑）

        Returns:
            dict: {'local_extra': DataFrame, 'national_extra': DataFrame}
        """
        try:
            # 单机多出的人员（全国库中没有的）
            local_extra = self.df_local[
                ~self.df_local['身份证号'].isin(self.df_national['身份证号码'])
            ]

            # 全国多出的人员（单机库中没有的）
            national_extra = self.df_national[
                ~self.df_national['身份证号码'].isin(self.df_local['身份证号'])
            ]

            self.results['local_extra'] = local_extra
            self.results['national_extra'] = national_extra

            logger.info(f"找到单机多出人员: {len(local_extra)} 人")
            logger.info(f"找到全国多出人员: {len(national_extra)} 人")

            return {
                'local_extra': local_extra,
                'national_extra': national_extra
            }

        except Exception as e:
            logger.error(f"查找人员差异失败: {e}")
            raise

    def find_field_differences(self):
        """
        逐字段比对差异

        Returns:
            dict: {field_name: DataFrame, ...}
        """
        try:
            # 为比对添加后缀
            df_local_suffixed = self.df_local.add_suffix('_local')
            df_local_suffixed = df_local_suffixed.rename(
                columns={'身份证号_local': '身份证号'}
            )

            df_national_suffixed = self.df_national.add_suffix('_national')
            df_national_suffixed = df_national_suffixed.rename(
                columns={'身份证号码_national': '身份证号码'}
            )

            field_diffs = {}

            for field in self.COMPARE_FIELDS:
                # 获取全国库对应字段名
                national_field = self.FIELD_MAPPING.get(field, field)

                # 合并两个表
                merged = pd.merge(
                    df_local_suffixed,
                    df_national_suffixed,
                    left_on='身份证号',
                    right_on='身份证号码',
                    how='inner'
                )

                local_col = f'{field}_local'
                national_col = f'{national_field}_national'

                # 找出该字段不一致的记录
                if local_col in merged.columns and national_col in merged.columns:
                    diff_mask = merged[local_col] != merged[national_col]
                    diff_records = merged[diff_mask][[
                        '姓名_local',
                        '身份证号',
                        local_col,
                        national_col
                    ]]

                    # 重命名列
                    diff_records.columns = [
                        '姓名',
                        '身份证号',
                        '单机表信息',
                        '全国表信息'
                    ]

                    field_diffs[f'diff_{field}'] = diff_records

                    logger.info(f"字段 '{field}' 发现 {len(diff_records)} 条差异")
                else:
                    logger.warning(f"字段 '{field}' 在数据中不存在")
                    field_diffs[f'diff_{field}'] = pd.DataFrame()

            self.results.update(field_diffs)
            return field_diffs

        except Exception as e:
            logger.error(f"查找字段差异失败: {e}")
            raise

    def generate_report(self):
        """
        生成完整比对报告

        Returns:
            dict: 包含所有比对结果的字典，包括预处理后的完整数据
        """
        try:
            logger.info("开始生成比对报告")

            # 预处理数据
            self.preprocess()

            # 查找人员差异
            self.find_differences()

            # 查找字段差异
            self.find_field_differences()

            # 将预处理后的完整数据添加到结果中
            self.results['local_preprocessed'] = self.df_local
            self.results['national_preprocessed'] = self.df_national

            logger.info("比对报告生成完成")

            return self.results

        except Exception as e:
            logger.error(f"生成比对报告失败: {e}")
            raise
