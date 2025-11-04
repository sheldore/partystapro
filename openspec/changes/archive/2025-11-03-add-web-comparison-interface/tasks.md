# 实施任务清单

## 1. 项目初始化

- [x] 1.1 创建 `requirements.txt` 并添加依赖:Flask, pandas, xlsxwriter, openpyxl
- [x] 1.2 创建项目目录结构 (`core/`, `templates/`, `static/`, `uploads/`)
- [x] 1.3 配置 Flask 应用入口 `app.py` (SECRET_KEY, 文件上传大小限制)
- [x] 1.4 创建 `.gitignore` 忽略 `uploads/` 和 `*.pyc` 文件

## 2. 后端核心模块实现

### 2.1 比对引擎模块
- [x] 2.1.1 创建 `core/comparison.py` 并定义 `ComparisonEngine` 类
- [x] 2.1.2 实现 `preprocess()` 方法:增加序号、计算党龄/年龄、标准化身份证号
- [x] 2.1.3 实现 `find_differences()` 方法:识别多出和缺少的人员
- [x] 2.1.4 实现 `find_field_differences()` 方法:逐字段比对差异
- [x] 2.1.5 实现 `generate_report()` 方法:汇总所有比对结果为字典
- [x] 2.1.6 编写单元测试 `tests/test_comparison.py` 覆盖所有方法

### 2.2 文件处理模块
- [x] 2.2.1 创建 `core/file_handler.py` 并实现文件上传处理函数
- [x] 2.2.2 实现会话 ID 生成和目录创建逻辑
- [x] 2.2.3 实现文件安全检查:扩展名验证、`secure_filename()` 处理
- [x] 2.2.4 实现文件大小限制检查 (10MB)
- [x] 2.2.5 实现临时文件清理函数 `cleanup_session_files()`
- [x] 2.2.6 编写单元测试 `tests/test_file_handler.py`

### 2.3 模板校验模块
- [x] 2.3.1 创建 `core/validator.py` 并实现模板加载函数
- [x] 2.3.2 在应用启动时加载单机库模板 `党员列表(导出数据).xls`
- [x] 2.3.3 在应用启动时加载全国库模板 `中共晋能控股煤业集团燕子山矿委员会.xls` Sheet '1'
- [x] 2.3.4 实现 `validate_template()` 函数:比对表头并返回差异详情
- [x] 2.3.5 编写单元测试 `tests/test_validator.py` 覆盖各种校验场景

### 2.4 结果导出模块
- [x] 2.4.1 创建 `core/exporter.py` 并实现 Excel 导出函数
- [x] 2.4.2 实现 `export_to_excel()`:将比对结果字典写入多 Sheet Excel
- [x] 2.4.3 实现文件命名逻辑:使用时间戳格式 `比对结果_YYYYMMDDHHmmss.xlsx`
- [x] 2.4.4 处理空结果 Sheet:仅写入表头
- [x] 2.4.5 编写单元测试 `tests/test_exporter.py`

## 3. Web 路由和 API 实现

- [x] 3.1 创建 `core/web/routes.py` 并定义路由
- [x] 3.2 实现 `GET /` 路由:渲染主页面 `index.html`
- [x] 3.3 实现 `POST /upload/local` 路由:处理单机库文件上传和校验
- [x] 3.4 实现 `POST /upload/national` 路由:处理全国库文件上传和校验
- [x] 3.5 实现 `POST /compare` 路由:执行比对并跳转到结果页面
- [x] 3.6 实现 `GET /result` 路由:渲染结果展示页面 `result.html`
- [x] 3.7 实现 `GET /download` 路由:生成并返回 Excel 文件下载
- [x] 3.8 编写集成测试 `tests/test_routes.py` 测试完整流程

## 4. 前端页面实现

### 4.1 主页面 (index.html)
- [x] 4.1.1 创建 HTML 结构:两个文件上传表单 + "开始比对"按钮
- [x] 4.1.2 添加 CSS 样式 (`static/style.css`):美化表单和按钮
- [x] 4.1.3 实现 JavaScript (`static/script.js`):监听文件选择事件
- [x] 4.1.4 实现文件上传 AJAX 请求和校验状态显示
- [x] 4.1.5 实现"开始比对"按钮启用/禁用逻辑
- [x] 4.1.6 实现加载动画显示

### 4.2 结果页面 (result.html)
- [x] 4.2.1 创建 HTML 结构:多个可折叠的表格区域
- [x] 4.2.2 使用 Jinja2 模板渲染比对结果数据
- [x] 4.2.3 添加 CSS 样式:表格美化、可折叠区域样式
- [x] 4.2.4 实现 JavaScript:表格折叠/展开交互
- [x] 4.2.5 添加"下载比对结果"按钮并绑定下载链接

## 5. 错误处理和边界情况

- [x] 5.1 实现全局错误处理器:捕获 404, 413, 500 错误
- [x] 5.2 添加日志记录:文件上传、校验、比对各阶段的日志
- [x] 5.3 处理缺失模板文件的启动失败场景
- [x] 5.4 处理空文件上传场景
- [x] 5.5 处理比对过程中的数据异常(缺失身份证号、日期格式错误)
- [x] 5.6 处理并发上传:验证会话隔离有效性

## 6. 测试和验证

- [x] 6.1 运行所有单元测试并确保通过 (`pytest tests/`)
- [x] 6.2 手动测试完整流程:上传 → 校验 → 比对 → 下载
- [x] 6.3 测试错误场景:错误格式文件、超大文件、模板不匹配
- [x] 6.4 测试边界情况:空文件、单记录文件、无差异结果
- [x] 6.5 性能测试:上传 5000 行数据并验证比对时间 < 60s
- [x] 6.6 安全测试:尝试路径遍历攻击、上传恶意文件名

## 7. 定时任务和清理

- [x] 7.1 创建定时清理脚本 `scripts/cleanup_old_files.py`
- [x] 7.2 实现逻辑:删除创建时间超过 1 小时的 `uploads/` 子目录
- [x] 7.3 配置 cron job 或使用 APScheduler 定时执行清理任务
- [x] 7.4 测试清理脚本:验证不误删活跃会话文件

## 8. 部署准备

- [x] 8.1 编写 `README.md`:包含项目介绍、安装步骤、运行方法
- [x] 8.2 创建 `config.py`:集中管理配置(SECRET_KEY, UPLOAD_FOLDER, MAX_FILE_SIZE)
- [x] 8.3 配置 Gunicorn:创建 `gunicorn_config.py`
- [x] 8.4 编写 Nginx 配置示例 `nginx.conf.example`
- [x] 8.5 编写部署文档 `DEPLOYMENT.md`:服务器环境要求、部署步骤、HTTPS 配置
- [x] 8.6 创建 systemd 服务文件 `scripts/c45-web.service`

## 9. 文档和收尾

- [x] 9.1 在 `比对单机.py` 顶部添加注释:标记为 legacy,指向 Web 版本
- [x] 9.2 更新 `openspec/project.md`:添加 Web 应用相关信息
- [x] 9.3 编写用户手册 `USER_GUIDE.md`:操作步骤截图说明
- [x] 9.4 运行 `openspec validate add-web-comparison-interface --strict` 确保提案通过
- [x] 9.5 提交代码并请求 code review

## 依赖关系说明

- 任务 2.x 可并行开发(各模块独立)
- 任务 3.x 依赖 2.x 完成
- 任务 4.x 可与 3.x 并行开发
- 任务 5.x 和 6.x 依赖 2-4 完成
- 任务 7.x 和 8.x 可独立进行
