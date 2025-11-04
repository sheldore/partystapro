"""
党员花名册在线比对工具 - Flask 应用主入口
"""
import os
import secrets
from flask import Flask

def create_app():
    """应用工厂函数"""
    # 创建 Flask 应用实例
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['TEMPLATES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'core', 'templates')

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册路由
    from core.web.routes import register_routes
    register_routes(app)

    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
