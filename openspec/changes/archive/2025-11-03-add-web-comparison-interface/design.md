# 设计文档: 党员花名册在线比对工具

## Context

当前项目是一个命令行脚本 (`比对单机.py`),仅适合技术人员使用。需要将其转换为 Web 应用以服务更广泛的用户群体。该变更涉及:
- 架构转型:从单脚本到 MVC 架构的 Web 应用
- 新增多个交互层:文件上传、实时校验、结果展示
- 数据安全:处理敏感的党员个人信息

**约束条件**:
- 必须保持现有比对逻辑的准确性
- 文件处理需要支持 `.xls` 和 `.xlsx` 格式
- 部署到公网服务器,需考虑安全性
- 遵循项目约定:简洁优先,避免过度工程化

## Goals / Non-Goals

### Goals
- 提供用户友好的 Web 界面用于文件上传和结果查看
- 自动校验上传文件的格式,避免错误输入
- 复用现有 `比对单机.py` 的核心比对逻辑
- 支持比对结果的在线展示和 Excel 下载
- 保证数据安全(临时文件自动清理、会话隔离)

### Non-Goals
- **不** 实现用户认证和权限管理(首版聚焦核心功能)
- **不** 支持历史记录和数据持久化(无数据库)
- **不** 实现批量比对或定时任务
- **不** 提供 RESTful API(仅 Web 页面交互)

## Decisions

### 1. Web 框架选择: Flask
**理由**:
- 轻量级,适合中小型应用
- 学习曲线平缓,团队容易上手
- 模板引擎 Jinja2 满足需求
- 部署简单(Gunicorn + Nginx)

**替代方案**:
- FastAPI:过度复杂,不需要异步处理和 API 文档
- Django:功能过重,不需要 ORM 和 Admin
- Streamlit:适合数据展示但定制化能力弱

### 2. 文件处理策略
**方案**:
- 使用 `werkzeug.FileStorage` 处理上传
- 临时文件存储到 `uploads/` 目录(基于会话 ID 隔离)
- 比对完成后立即删除临时文件
- 文件大小限制 10MB

**理由**:
- 避免磁盘空间占用
- 保护用户隐私(不保留敏感数据)
- 防止恶意上传耗尽存储

### 3. 模板校验方案
**方案**:
读取模板文件的第一行(表头),与上传文件的表头进行精确匹配:
- 单机库模板: `core/templates/党员列表(导出数据).xls`
- 全国库模板: `core/templates/中共晋能控股煤业集团燕子山矿委员会.xls` (Sheet `1`)

**校验逻辑**:
```python
def validate_template(uploaded_df, template_df):
    uploaded_cols = set(uploaded_df.columns)
    template_cols = set(template_df.columns)
    return uploaded_cols == template_cols
```

**错误反馈**:
- 如果不匹配,返回具体缺失或多余的列名
- 前端实时显示校验状态(✓ 通过 / ✗ 失败)

### 4. 比对引擎重构
**方案**:
将 `比对单机.py` 的逻辑提取到 `core/comparison.py` 模块:
```python
class ComparisonEngine:
    def __init__(self, df_local, df_national):
        self.df_local = df_local
        self.df_national = df_national

    def preprocess(self):
        """增加序号、计算党龄/年龄、标准化身份证号"""

    def find_differences(self):
        """返回多出和缺少的人员"""

    def find_field_differences(self):
        """返回字段差异列表"""

    def generate_report(self):
        """返回完整比对结果字典"""
```

**理由**:
- 将业务逻辑与展示层分离
- 便于单元测试
- 支持未来扩展(如 API 调用)

### 5. 前端架构
**方案**:
- 纯 HTML/CSS/JavaScript(无框架)
- 使用 Fetch API 进行 AJAX 请求
- 表格展示使用原生 `<table>` 元素

**页面流程**:
1. `index.html`: 上传表单
   - 两个文件上传框
   - 实时校验反馈
   - "开始比对"按钮(校验通过后启用)
2. `result.html`: 结果展示
   - 多个可折叠的表格区域(单机多、全国多、各字段差异)
   - 下载按钮

**理由**:
- 需求简单,无需 Vue/React 的复杂性
- 减少构建和部署复杂度
- 加载速度快

### 6. 会话管理
**方案**:
- 使用 Flask 的 `session` 存储临时文件路径
- 每个会话生成唯一 ID(`uuid4`)
- 文件存储到 `uploads/<session_id>/`

**安全措施**:
- 设置 `SECRET_KEY` 加密 session cookie
- 限制文件扩展名为 `.xls` 和 `.xlsx`
- 使用 `secure_filename()` 防止路径遍历攻击

### 7. 结果导出格式
**方案**:
使用 `pandas.ExcelWriter` 和 `xlsxwriter` 引擎生成多 Sheet Excel:
- Sheet 1: `单机多出人员`
- Sheet 2: `全国多出人员`
- Sheet 3-N: `{字段名}差异` (姓名、性别、民族等)

**文件命名**:
`比对结果_<timestamp>.xlsx`

## Risks / Trade-offs

### Risk 1: 并发上传冲突
**风险**: 多用户同时上传可能导致文件覆盖
**缓解**: 使用 UUID 会话 ID 隔离文件目录

### Risk 2: 大文件处理性能
**风险**: 单机/全国库文件过大(>5000行)可能导致处理超时
**缓解**:
- 设置 10MB 文件大小限制
- 前端显示加载动画
- 后端设置 60s 超时(未来可改为异步任务)

### Risk 3: 数据安全
**风险**: 党员信息泄露
**缓解**:
- 立即删除临时文件
- 使用 HTTPS 传输(部署阶段)
- 添加访问日志审计

### Trade-off: 简单性 vs 功能性
**选择**: 首版不实现用户认证、历史记录
**原因**: 遵循 CLAUDE.md 的 "简洁优先" 原则,先验证核心功能

## Migration Plan

### 阶段 1: 开发和测试(本地)
1. 搭建 Flask 应用骨架
2. 实现文件上传和模板校验
3. 重构比对逻辑到模块
4. 实现结果展示和下载
5. 单元测试和集成测试

### 阶段 2: 部署准备
1. 编写 `requirements.txt`
2. 配置 Gunicorn
3. 编写 Nginx 配置
4. 准备 HTTPS 证书
5. 编写部署文档

### 阶段 3: 上线和监控
1. 部署到公网服务器
2. 配置日志记录
3. 监控磁盘使用(uploads 目录)
4. 收集用户反馈

### Rollback 计划
- 保留 `比对单机.py` 作为 fallback
- 如有问题可回退到命令行版本

## Open Questions

1. **是否需要限制并发用户数?**
   - 建议: 首版不限制,根据服务器负载后续调整

2. **临时文件清理策略?**
   - 建议: 比对完成立即删除;额外设置定时任务清理超过 1 小时的文件

3. **是否需要错误日志邮件通知?**
   - 建议: 首版记录到文件,后续根据需要添加邮件通知

4. **部署服务器配置?**
   - 待确认: CPU、内存、带宽要求(建议 2C4G 起步)
