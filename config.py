"""
应用配置文件
"""
import os
import secrets


class Config:
    """基础配置"""
    # Flask 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # 文件上传配置
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    TEMPLATES_FOLDER = os.path.join(os.path.dirname(__file__), 'core', 'templates')

    # 会话配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1小时


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
