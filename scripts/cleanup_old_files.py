"""
定时清理脚本 - 删除超时的临时文件
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import file_handler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """清理超过1小时的临时文件"""
    base_upload_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'uploads'
    )

    logger.info(f"开始清理临时文件: {base_upload_folder}")
    file_handler.cleanup_old_files(base_upload_folder, max_age_hours=1)
    logger.info("清理完成")


if __name__ == '__main__':
    main()
