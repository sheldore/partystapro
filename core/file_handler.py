"""
文件处理模块 - 文件上传、会话管理和临时文件清理
"""
import os
import uuid
import shutil
import logging
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'.xls', '.xlsx'}


def allowed_file(filename):
    """
    检查文件扩展名是否允许

    Args:
        filename: 文件名

    Returns:
        bool: 是否允许
    """
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


def get_session_id():
    """
    生成唯一的会话 ID

    Returns:
        str: UUID4 格式的会话 ID
    """
    return str(uuid.uuid4())


def create_session_directory(base_upload_folder, session_id):
    """
    为会话创建独立的上传目录

    Args:
        base_upload_folder: 基础上传目录路径
        session_id: 会话 ID

    Returns:
        str: 会话上传目录路径
    """
    session_dir = os.path.join(base_upload_folder, session_id)
    os.makedirs(session_dir, exist_ok=True)
    logger.info(f"创建会话目录: {session_dir}")
    return session_dir


def save_uploaded_file(file, upload_folder, original_filename=None):
    """
    保存上传的文件

    Args:
        file: werkzeug.FileStorage 对象
        upload_folder: 上传目录路径
        original_filename: 可选的原始文件名

    Returns:
        str: 保存后的文件路径

    Raises:
        ValueError: 文件类型不允许
    """
    if not file:
        raise ValueError("未提供文件")

    filename = original_filename or file.filename
    if not allowed_file(filename):
        raise ValueError(f"文件类型不允许，仅支持 {', '.join(ALLOWED_EXTENSIONS)}")

    # 使用 secure_filename 防止路径遍历攻击
    safe_filename = secure_filename(filename)

    # 如果文件名被清理为空，使用默认名称
    if not safe_filename:
        ext = os.path.splitext(filename)[1].lower()
        safe_filename = f"upload{ext}"

    filepath = os.path.join(upload_folder, safe_filename)

    # 保存文件
    file.save(filepath)
    logger.info(f"文件已保存: {filepath}")

    return filepath


def cleanup_session_files(session_folder):
    """
    清理会话的所有临时文件

    Args:
        session_folder: 会话目录路径
    """
    try:
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
            logger.info(f"已清理会话目录: {session_folder}")
    except Exception as e:
        logger.error(f"清理会话目录失败 {session_folder}: {e}")


def cleanup_old_files(base_upload_folder, max_age_hours=1):
    """
    清理超时的临时文件

    Args:
        base_upload_folder: 基础上传目录路径
        max_age_hours: 最大保留时间（小时）
    """
    try:
        if not os.path.exists(base_upload_folder):
            return

        now = datetime.now()
        threshold = now - timedelta(hours=max_age_hours)

        for session_dir in os.listdir(base_upload_folder):
            session_path = os.path.join(base_upload_folder, session_dir)

            if not os.path.isdir(session_path):
                continue

            # 获取目录创建时间
            creation_time = datetime.fromtimestamp(os.path.getctime(session_path))

            if creation_time < threshold:
                shutil.rmtree(session_path)
                logger.info(f"清理过期会话目录: {session_path}")

    except Exception as e:
        logger.error(f"清理过期文件失败: {e}")


def check_file_size(file, max_size_mb=10):
    """
    检查文件大小是否超过限制

    Args:
        file: werkzeug.FileStorage 对象
        max_size_mb: 最大文件大小（MB）

    Returns:
        bool: 是否在限制内

    Note:
        此函数实际上由 Flask 的 MAX_CONTENT_LENGTH 配置自动处理
        这里提供作为额外的检查点
    """
    try:
        file.seek(0, 2)  # 移动到文件末尾
        size = file.tell()  # 获取当前位置（文件大小）
        file.seek(0)  # 重置到文件开头

        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes
    except Exception as e:
        logger.error(f"检查文件大小失败: {e}")
        return False
