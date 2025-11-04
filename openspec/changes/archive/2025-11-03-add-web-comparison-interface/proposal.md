# 党员花名册在线比对工具

## Why

当前项目仅提供单机脚本 (`比对单机.py`),需要手动修改文件路径、执行脚本且无法实时查看结果。为了提高易用性和便利性,需要提供一个在线 Web 工具,让用户可以通过浏览器上传文件、自动比对并查看结果。

## What Changes

- **新增 Web 应用框架**:使用 Flask 构建 Web 服务
- **新增文件上传功能**:支持上传两个 Excel 文件(单机库和全国库)
- **新增模板校验功能**:自动验证上传文件的表头是否符合标准模板
- **重构比对逻辑**:将 `比对单机.py` 的逻辑封装为可复用的模块
- **新增结果展示页面**:在网页上直接显示比对结果(多出人员、缺少人员、信息差异)
- **新增结果下载功能**:生成包含所有比对结果的 Excel 文件供用户下载

核心能力:
1. **web-ui**: Web 用户界面(文件上传表单、结果展示页面)
2. **file-upload**: 文件上传和临时存储
3. **template-validation**: 模板表头校验
4. **comparison-engine**: 党员数据比对核心逻辑
5. **result-export**: Excel 结果导出

## Impact

### 影响的规格
- **新增**: `web-ui`, `file-upload`, `template-validation`, `comparison-engine`, `result-export`

### 影响的代码
- **新增文件**:
  - `app.py`: Flask 应用主入口
  - `core/web/__init__.py`: Web 模块初始化
  - `core/web/routes.py`: 路由定义
  - `core/file_handler.py`: 文件上传处理
  - `core/validator.py`: 模板校验逻辑
  - `core/comparison.py`: 比对引擎(从 `比对单机.py` 重构而来)
  - `core/exporter.py`: 结果导出
  - `templates/index.html`: 主页面(上传表单)
  - `templates/result.html`: 结果展示页面
  - `static/style.css`: 样式文件
  - `static/script.js`: 前端交互脚本
  - `requirements.txt`: Python 依赖

- **修改文件**:
  - `比对单机.py`: 标记为 legacy,添加注释说明迁移到 Web 版本

### 用户影响
- 用户可以通过浏览器访问工具,无需手动运行 Python 脚本
- 实时反馈校验结果和比对进度
- 直观的网页表格展示比对结果
- 一键下载完整比对报告

### 技术约束
- 需要安装 Flask 及相关依赖
- 需要配置文件上传目录和临时文件清理策略
- 需要考虑文件上传大小限制(建议 10MB)
- 需要处理并发上传和会话隔离
