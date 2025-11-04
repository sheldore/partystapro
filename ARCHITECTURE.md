# 系统架构文档

## 架构概览

本系统是一个基于 Flask 的 Web 应用，用于比对党员花名册数据。采用传统的 MVC 架构模式，前后端不分离。

```
┌─────────────────────────────────────────────────────────┐
│                    浏览器客户端                          │
│           (HTML/CSS/JavaScript)                         │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP Request/Response
┌────────────────▼────────────────────────────────────────┐
│                Flask Web Server                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Routes (routes.py)                     │  │
│  │  - 文件上传路由                                   │  │
│  │  - 模板校验路由                                   │  │
│  │  - 比对执行路由                                   │  │
│  │  - 结果展示路由                                   │  │
│  │  - 文件下载路由                                   │  │
│  └──────────┬───────────────────────────────────────┘  │
│             │                                            │
│  ┌──────────▼───────────────────────────────────────┐  │
│  │           Core Business Logic                     │  │
│  │  ┌────────────────┐  ┌──────────────────────┐   │  │
│  │  │  validator.py  │  │  comparison.py        │   │  │
│  │  │  模板校验      │  │  比对引擎              │   │  │
│  │  └────────────────┘  └──────────────────────┘   │  │
│  │  ┌────────────────┐  ┌──────────────────────┐   │  │
│  │  │file_handler.py │  │  exporter.py          │   │  │
│  │  │  文件处理      │  │  结果导出              │   │  │
│  │  └────────────────┘  └──────────────────────┘   │  │
│  └──────────┬───────────────────────────────────────┘  │
└─────────────┼────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────┐
│              文件系统 & Session                       │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ uploads/       │  │ Flask Session Cookie      │   │
│  │ - local.xls    │  │ - session_id              │   │
│  │ - national.xls │  │ - has_results             │   │
│  │ - results.pkl  │  │ - local_file (path)       │   │
│  │                │  │ - national_file (path)    │   │
│  └────────────────┘  └──────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## 核心模块说明

### 1. Routes (core/web/routes.py)
**职责**：处理 HTTP 请求，协调各模块完成业务逻辑

**关键路由**：
- `GET /` - 主页面，显示文件上传表单
- `POST /upload/local` - 上传单机库文件
- `POST /upload/national` - 上传全国库文件
- `POST /compare` - 执行比对
- `GET /result` - 显示比对结果
- `GET /download` - 下载 Excel 报告
- `GET /download/template/local` - 下载单机模板
- `GET /download/template/national` - 下载全国模板

**设计要点**：
1. 每个用户会话有唯一的 session_id
2. 上传文件保存在独立的会话目录
3. 验证失败时清除 session 和文件
4. 比对结果保存到 pickle 文件，避免 session 过大

### 2. Validator (core/validator.py)
**职责**：验证上传文件是否符合标准模板

**验证规则**：
1. 列名必须完全匹配
2. 列的顺序必须完全一致
3. 不能有缺失列或多余列

**实现细节**：
- 启动时加载标准模板文件（单机模板.xls 和 全国模板.xls）
- 使用列表存储列名，保留顺序信息
- 生成详细的错误提示，包含列位置（A列、B列...）

**关键方法**：
```python
validate_local_template(file_path) -> dict
validate_national_template(file_path) -> dict
```

### 3. Comparison Engine (core/comparison.py)
**职责**：执行党员数据比对

**比对流程**：
1. **数据预处理**：
   - 添加序号列
   - 计算党龄（基于入党时间）
   - 计算年龄（基于身份证号）
   - 标准化身份证号（转大写、去空格）
   - 添加人员类别（正式党员/预备党员）

2. **差异识别**：
   - 单机多出：在单机库但不在全国库
   - 全国多出：在全国库但不在单机库
   - 字段差异：8个字段的逐一比对（姓名、性别、民族、出生日期、学历、入党时间、个人身份、人员类别）

3. **结果生成**：
   返回包含所有差异的字典，包括预处理后的完整数据

**关键类**：
```python
class ComparisonEngine:
    def __init__(self, df_local, df_national)
    def preprocess_data(self)
    def find_differences(self) -> tuple
    def compare_field(self, field_name) -> pd.DataFrame
    def generate_report(self) -> dict
```

### 4. File Handler (core/file_handler.py)
**职责**：文件上传和会话管理

**功能**：
- 生成唯一的 session_id（UUID）
- 创建会话目录
- 保存上传文件
- 验证文件扩展名

### 5. Exporter (core/exporter.py)
**职责**：导出比对结果为 Excel 文件

**输出格式**：
- 多工作表 Excel 文件
- 每个工作表包含不同类型的差异数据
- 自动调整列宽以适应内容

## 数据流

### 完整的用户操作流程

```
1. 用户访问首页
   └─> Flask 创建 session，生成 session_id

2. 用户上传单机库文件
   └─> file_handler 保存到 uploads/{session_id}/local.xls
   └─> validator 验证模板格式
       ├─> ✓ 通过：session['local_file'] = file_path
       └─> ✗ 失败：删除文件，清除 session，返回错误提示

3. 用户上传全国库文件
   └─> file_handler 保存到 uploads/{session_id}/national.xls
   └─> validator 验证模板格式
       ├─> ✓ 通过：session['national_file'] = file_path
       └─> ✗ 失败：删除文件，清除 session，返回错误提示

4. 用户点击"开始比对"
   └─> 检查两个文件路径是否存在
   └─> 检查文件是否实际存在
   └─> pd.read_excel 读取文件
   └─> ComparisonEngine 执行比对
   └─> 使用 pickle 保存结果到 uploads/{session_id}/results.pkl
   └─> session['has_results'] = True
   └─> 删除临时上传的文件（local.xls, national.xls）
   └─> 跳转到结果页面

5. 显示结果页面
   └─> 检查 session['has_results']
   └─> 从 pickle 文件读取结果
   └─> 将 DataFrame 转换为 HTML 表格
   └─> 渲染 result.html

6. 用户下载报告
   └─> 从 pickle 文件读取结果
   └─> exporter 生成 Excel 文件
   └─> 发送文件给用户
```

## 关键技术决策

### 1. Session Cookie 大小问题

**问题描述**：
- 初版将比对结果存储在 Flask session 中
- 比对结果包含多个 DataFrame，序列化后超过 4KB
- 浏览器会忽略超过 4KB 的 cookie

**解决方案**：
- 使用 pickle 将结果保存到服务器文件系统
- Session 中只存储布尔标志 `has_results`
- 从约 5446 字节降至约 50 字节

**代码位置**：
- `core/web/routes.py` - compare 路由（保存）
- `core/web/routes.py` - result 路由（读取）
- `core/web/routes.py` - download 路由（读取）

### 2. 模板验证策略

**问题描述**：
- 需要严格验证列名和列顺序
- 需要提供详细的错误信息帮助用户修正

**解决方案**：
- 使用列表而非集合存储列名，保留顺序
- 逐列对比，生成详细的差异列表
- 错误信息格式："A列应为'姓名'，实际为'XX'"

**代码位置**：
- `core/validator.py` - validate_local_template
- `core/validator.py` - validate_national_template

### 3. 文件路径管理

**问题描述**：
- 验证失败后文件被删除，但 session 路径仍保留
- 后续操作尝试访问已删除文件导致 FileNotFoundError

**解决方案**：
1. 验证失败时清除 session：`session.pop('local_file', None)`
2. 删除文件前检查存在性：`if os.path.exists(filepath)`
3. 比对前验证文件存在性
4. 异常处理中也清除 session

**代码位置**：
- `core/web/routes.py` - upload_local 路由
- `core/web/routes.py` - upload_national 路由
- `core/web/routes.py` - compare 路由

### 4. 全国库工作表读取

**问题描述**：
- 用户上传的全国库文件可能有不同的工作表名称
- 验证工作表名称增加了复杂性

**解决方案**：
- 使用 `sheet_name=0` 直接读取第一张工作表
- 不验证工作表名称

**代码位置**：
- `core/validator.py` - validate_national_template
- `core/web/routes.py` - compare 路由

### 5. 会话隔离

**问题描述**：
- 多用户同时使用可能导致文件冲突

**解决方案**：
- 每个用户会话有唯一的 session_id（UUID）
- 文件保存在独立的会话目录：`uploads/{session_id}/`
- Flask session 自动处理多用户隔离

## 安全考虑

### 1. 文件上传安全
- 限制文件大小：最大 10MB
- 限制文件类型：只允许 .xls 和 .xlsx
- 文件保存在服务器控制的目录
- 验证失败立即删除文件

### 2. Session 安全
- 使用 Flask 的安全 session 机制
- SECRET_KEY 应设置为强随机值
- Session 数据经过签名防篡改

### 3. 数据隐私
- 上传文件在比对后立即删除
- 比对结果在用户会话结束后应被清理
- 建议部署定时清理任务

## 性能优化

### 1. 数据处理性能
- 使用 pandas 向量化操作
- 避免逐行循环处理
- 使用 isin() 进行集合操作

### 2. 内存优化
- 比对完成后删除临时文件
- 结果使用 pickle 序列化存储
- 不在内存中保留多份数据副本

### 3. 响应速度
- 模板文件在应用启动时加载
- 避免重复读取模板文件

## 扩展性考虑

### 未来可能的改进方向

1. **异步任务处理**
   - 使用 Celery 处理大文件比对
   - 添加进度条显示比对进度

2. **用户认证**
   - 添加用户登录功能
   - 保存用户的历史比对记录

3. **数据库存储**
   - 使用数据库存储比对结果
   - 支持历史记录查询

4. **API 接口**
   - 提供 RESTful API
   - 支持第三方系统集成

5. **批量处理**
   - 支持一次上传多个文件
   - 批量生成报告

6. **缓存机制**
   - 对相同文件的重复上传使用缓存
   - 减少重复计算

## 故障排查指南

### 常见问题及解决方法

1. **比对失败，提示"比对失败请重试"**
   - 检查应用日志
   - 确认文件格式是否正确
   - 重启应用重新尝试

2. **验证失败，提示列不匹配**
   - 下载标准模板文件
   - 对比上传文件的列名和顺序
   - 使用标准模板填充数据

3. **结果页面显示为空**
   - 检查 session cookie 是否被禁用
   - 检查 uploads 目录权限
   - 检查是否有 results.pkl 文件生成

4. **文件上传失败**
   - 检查文件大小是否超过 10MB
   - 检查 uploads 目录是否存在且可写
   - 检查磁盘空间是否充足

## 相关文档

- `README.md` - 用户使用说明
- `openspec/project.md` - 项目上下文和约束
- `openspec/changes/archive/*/implementation-summary.md` - 实施经验总结
- `CLAUDE.md` - AI 开发指令和规范
