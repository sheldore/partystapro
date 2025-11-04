"""
模板校验模块 - 验证上传文件是否符合标准模板格式
"""
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TemplateValidator:
    """模板校验器"""

    def __init__(self, templates_folder):
        """
        初始化模板校验器

        Args:
            templates_folder: 模板文件所在目录
        """
        self.templates_folder = templates_folder
        self.local_template_columns = None
        self.national_template_columns = None

        # 模板文件路径 - 使用标准模板
        self.local_template_path = os.path.join(
            templates_folder,
            '单机模板.xls'
        )
        self.national_template_path = os.path.join(
            templates_folder,
            '全国模板.xls'
        )

    def load_templates(self):
        """
        加载模板文件并提取表头列名（保留顺序）

        Raises:
            FileNotFoundError: 模板文件不存在
            Exception: 读取模板失败
        """
        try:
            # 加载单机库模板
            if not os.path.exists(self.local_template_path):
                raise FileNotFoundError(
                    f"单机库模板文件不存在: {self.local_template_path}"
                )

            df_local = pd.read_excel(self.local_template_path)
            self.local_template_columns = list(df_local.columns)
            logger.info(
                f"已加载单机库模板，包含 {len(self.local_template_columns)} 列"
            )

            # 加载全国库模板（读取第一张表）
            if not os.path.exists(self.national_template_path):
                raise FileNotFoundError(
                    f"全国库模板文件不存在: {self.national_template_path}"
                )

            df_national = pd.read_excel(
                self.national_template_path,
                sheet_name=0
            )
            self.national_template_columns = list(df_national.columns)
            logger.info(
                f"已加载全国库模板，包含 {len(self.national_template_columns)} 列"
            )

        except FileNotFoundError as e:
            logger.error(f"模板文件不存在: {e}")
            raise
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            raise

    def validate_local_template(self, file_path):
        """
        验证单机库文件是否符合模板（包括列数量和顺序）

        Args:
            file_path: 上传文件路径

        Returns:
            dict: {
                'valid': bool,
                'missing_columns': list,  # 缺失的列
                'extra_columns': list,    # 多余的列
                'order_mismatch': bool,   # 顺序是否不匹配
                'column_details': list,   # 列位置详细信息
                'error': str              # 错误信息（如果有）
            }
        """
        try:
            if self.local_template_columns is None:
                self.load_templates()

            # 读取上传文件
            df_uploaded = pd.read_excel(file_path)
            uploaded_columns = list(df_uploaded.columns)

            # 比对列名（使用集合检查缺失和多余）
            template_set = set(self.local_template_columns)
            uploaded_set = set(uploaded_columns)

            missing_columns = list(template_set - uploaded_set)
            extra_columns = list(uploaded_set - template_set)

            # 检查列顺序并生成详细信息
            order_mismatch = False
            column_details = []

            if len(missing_columns) == 0 and len(extra_columns) == 0:
                order_mismatch = uploaded_columns != self.local_template_columns

                if order_mismatch:
                    # 提供每列的详细对比信息
                    for i, (expected, actual) in enumerate(zip(self.local_template_columns, uploaded_columns)):
                        col_letter = chr(65 + i)  # A, B, C...
                        if expected != actual:
                            column_details.append({
                                'position': f'{col_letter}列',
                                'expected': expected,
                                'actual': actual
                            })
            else:
                # 如果有缺失或多余的列，提供位置信息
                max_len = max(len(self.local_template_columns), len(uploaded_columns))
                for i in range(max_len):
                    col_letter = chr(65 + i) if i < 26 else f'{chr(65 + i//26 - 1)}{chr(65 + i%26)}'
                    expected = self.local_template_columns[i] if i < len(self.local_template_columns) else '(无)'
                    actual = uploaded_columns[i] if i < len(uploaded_columns) else '(无)'
                    if expected != actual:
                        column_details.append({
                            'position': f'{col_letter}列',
                            'expected': expected,
                            'actual': actual
                        })

            is_valid = (len(missing_columns) == 0 and
                       len(extra_columns) == 0 and
                       not order_mismatch)

            result = {
                'valid': is_valid,
                'missing_columns': missing_columns,
                'extra_columns': extra_columns,
                'order_mismatch': order_mismatch,
                'column_details': column_details
            }

            if is_valid:
                logger.info(f"单机库文件校验通过: {file_path}")
            else:
                error_details = []
                if missing_columns:
                    error_details.append(f"缺失列: {missing_columns}")
                if extra_columns:
                    error_details.append(f"多余列: {extra_columns}")
                if order_mismatch:
                    error_details.append("列顺序不匹配")
                logger.warning(
                    f"单机库文件校验失败: {', '.join(error_details)}"
                )

            return result

        except Exception as e:
            logger.error(f"校验单机库文件失败: {e}")
            return {
                'valid': False,
                'error': str(e)
            }

    def validate_national_template(self, file_path):
        """
        验证全国库文件是否符合模板（包括列数量和顺序）

        Args:
            file_path: 上传文件路径

        Returns:
            dict: {
                'valid': bool,
                'missing_columns': list,
                'extra_columns': list,
                'order_mismatch': bool,
                'column_details': list,
                'error': str
            }
        """
        try:
            if self.national_template_columns is None:
                self.load_templates()

            # 读取上传文件的第一张表
            df_uploaded = pd.read_excel(file_path, sheet_name=0)

            uploaded_columns = list(df_uploaded.columns)

            # 比对列名（使用集合检查缺失和多余）
            template_set = set(self.national_template_columns)
            uploaded_set = set(uploaded_columns)

            missing_columns = list(template_set - uploaded_set)
            extra_columns = list(uploaded_set - template_set)

            # 检查列顺序并生成详细信息
            order_mismatch = False
            column_details = []

            if len(missing_columns) == 0 and len(extra_columns) == 0:
                order_mismatch = uploaded_columns != self.national_template_columns

                if order_mismatch:
                    # 提供每列的详细对比信息
                    for i, (expected, actual) in enumerate(zip(self.national_template_columns, uploaded_columns)):
                        col_letter = chr(65 + i)  # A, B, C...
                        if expected != actual:
                            column_details.append({
                                'position': f'{col_letter}列',
                                'expected': expected,
                                'actual': actual
                            })
            else:
                # 如果有缺失或多余的列，提供位置信息
                max_len = max(len(self.national_template_columns), len(uploaded_columns))
                for i in range(max_len):
                    col_letter = chr(65 + i) if i < 26 else f'{chr(65 + i//26 - 1)}{chr(65 + i%26)}'
                    expected = self.national_template_columns[i] if i < len(self.national_template_columns) else '(无)'
                    actual = uploaded_columns[i] if i < len(uploaded_columns) else '(无)'
                    if expected != actual:
                        column_details.append({
                            'position': f'{col_letter}列',
                            'expected': expected,
                            'actual': actual
                        })

            is_valid = (len(missing_columns) == 0 and
                       len(extra_columns) == 0 and
                       not order_mismatch)

            result = {
                'valid': is_valid,
                'missing_columns': missing_columns,
                'extra_columns': extra_columns,
                'order_mismatch': order_mismatch,
                'column_details': column_details
            }

            if is_valid:
                logger.info(f"全国库文件校验通过: {file_path}")
            else:
                error_details = []
                if missing_columns:
                    error_details.append(f"缺失列: {missing_columns}")
                if extra_columns:
                    error_details.append(f"多余列: {extra_columns}")
                if order_mismatch:
                    error_details.append("列顺序不匹配")
                logger.warning(
                    f"全国库文件校验失败: {', '.join(error_details)}"
                )

            return result

        except Exception as e:
            logger.error(f"校验全国库文件失败: {e}")
            return {
                'valid': False,
                'error': str(e)
            }


# 创建全局验证器实例（将在 app 启动时初始化）
validator = None


def init_validator(templates_folder):
    """
    初始化全局验证器实例

    Args:
        templates_folder: 模板文件所在目录
    """
    global validator
    validator = TemplateValidator(templates_folder)
    validator.load_templates()
    logger.info("模板校验器初始化完成")


def get_validator():
    """
    获取全局验证器实例

    Returns:
        TemplateValidator: 校验器实例
    """
    if validator is None:
        raise RuntimeError("模板校验器尚未初始化，请先调用 init_validator()")
    return validator
