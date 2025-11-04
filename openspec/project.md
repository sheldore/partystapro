# Project Context

## Purpose
党员信息管理和数据比对工具，用于：
- 比对单机库和全国库中的党员数据
- 识别两个数据源之间的差异（多余记录、缺失记录）
- 自动计算党龄、年龄等衍生字段
- 生成详细的差异报告，包括各字段的不一致情况
- 支持多种党员管理表格模板

## Tech Stack
- **Python 3.7+**：主要编程语言
- **Flask 3.0**：Web 框架
- **pandas 2.1**：数据处理和分析核心库
- **xlsxwriter**：Excel 文件写入引擎
- **openpyxl**：Excel 文件读取引擎
- **pickle**：比对结果序列化存储
- **原生 HTML/CSS/JavaScript**：前端界面

## Project Conventions

### Code Style
- 使用中文变量名和函数名（符合业务场景）
- 文件路径使用相对路径引用 `core/templates/` 目录
- 日期计算统一使用 `pd.to_datetime()` 和 `.dt` 访问器
- 身份证号统一转换为大写字符串格式处理
- 日志使用标准 logging 模块，级别为 INFO

### Architecture Patterns
- **Web 应用架构**：基于 Flask 的 MVC 模式
- **模块化设计**：
  - `core/web/routes.py`：路由和视图逻辑
  - `core/comparison.py`：比对引擎
  - `core/validator.py`：模板校验
  - `core/file_handler.py`：文件处理
  - `core/exporter.py`：结果导出
- **数据流处理**：
  1. 文件上传和会话管理
  2. 模板校验（列名和顺序验证）
  3. 数据预处理（增加序号、计算党龄/年龄、标准化身份证号）
  4. 数据比对（基于身份证号）
  5. 结果存储（pickle 文件）
  6. 结果展示（HTML）和导出（Excel）
- **Session 管理**：
  - 使用 Flask session 存储会话 ID 和标志位
  - 比对结果存储在服务器端 pickle 文件，避免 session cookie 过大
  - 每个用户会话有独立的上传目录
- **列名映射**：处理不同数据源的字段名差异（如 `入党时间` vs `入党日期`）

### Testing Strategy
- 遵循 CLAUDE.md 中的测试要求
- 每个功能必须有对应测试
- 测试需详细且真实反映使用场景
- 禁止使用 mock 服务
- 测试需要详细输出以便调试

### Git Workflow
- 使用 OpenSpec 工作流管理变更
- 重大变更需要先创建提案（使用 `/openspec:proposal`）
- 参考 `openspec/AGENTS.md` 了解完整工作流

## Domain Context

### 党员数据字段
- **基础信息**：姓名、性别、民族、出生日期、身份证号
- **党务信息**：入党时间/入党日期、党龄、人员类别（正式党员/预备党员）
- **其他信息**：学历、个人身份/工作岗位

### 业务规则
- **党龄计算**：截止日期为每年 12-31，从入党日期计算的完整年数
- **年龄计算**：截止日期为每年 12-31，从身份证号提取出生日期计算
- **预备党员判定**：入党时间在当年（2024）视为预备党员，否则为正式党员
- **身份证号**：核心唯一标识，用于跨表关联

### 数据源
- **单机库**：本地党员管理系统导出的数据
- **全国库**：上级党组织系统的数据
- 两者字段名可能不完全一致，需要映射处理

### 输出报告结构
生成的 Excel 文件包含以下工作表：
- `单机`：处理后的单机库完整数据
- `1`：处理后的全国库完整数据
- `单机多`：仅在单机库存在的党员记录
- `单机少`：仅在全国库存在的党员记录
- `{字段}差异`：身份证号相同但该字段值不同的记录

## Important Constraints
- **数据敏感性**：处理的是真实党员个人信息，需注意数据安全
- **日期一致性**：所有年龄、党龄计算统一截止到当年 12 月 31 日
- **编码兼容性**：需支持中文字段名和中文内容
- **Excel 格式兼容性**：需同时支持 `.xls` 和 `.xlsx` 格式

## External Dependencies
- **pandas**：数据处理核心依赖
- **xlsxwriter**：Excel 写入引擎
- **openpyxl**：Excel 读取引擎（pandas 的后端依赖）

## File Structure
```
c4.5/
├── app.py                      # Flask 应用入口
├── requirements.txt            # Python 依赖
├── gunicorn_config.py          # Gunicorn 配置
├── .gitignore                  # Git 忽略文件
├── README.md                   # 项目说明文档
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── comparison.py           # 比对引擎（重构自 比对单机.py）
│   ├── file_handler.py         # 文件上传处理
│   ├── validator.py            # 模板校验逻辑
│   ├── exporter.py             # Excel 结果导出
│   ├── templates/              # 标准模板文件
│   │   ├── 单机模板.xls
│   │   └── 全国模板.xls
│   └── web/                    # Web 模块
│       ├── __init__.py
│       └── routes.py           # 路由定义
├── templates/                  # HTML 模板
│   ├── index.html              # 主页面（文件上传）
│   ├── result.html             # 结果展示页面
│   └── 404.html                # 404 错误页面
├── static/                     # 静态资源
│   ├── style.css               # 样式文件
│   └── script.js               # 前端交互脚本
├── scripts/                    # 工具脚本
│   └── cleanup_old_files.py    # 清理过期临时文件
├── uploads/                    # 临时上传目录（运行时自动创建）
│   └── {session_id}/           # 每个会话的独立目录
│       ├── local.xls           # 临时上传的单机库文件
│       ├── national.xls        # 临时上传的全国库文件
│       └── results.pkl         # 比对结果 pickle 文件
├── openspec/                   # OpenSpec 工作流
│   ├── AGENTS.md               # OpenSpec 使用说明
│   ├── project.md              # 本文件（项目上下文）
│   ├── changes/                # 活动变更
│   │   └── archive/            # 已归档变更
│   │       ├── 2025-11-03-add-web-comparison-interface/
│   │       └── 2025-11-03-update-template-validation-and-results/
│   │           └── implementation-summary.md  # 实施经验总结
│   └── specs/                  # 功能规范
│       ├── comparison-engine/
│       ├── comparison-results/
│       ├── file-upload/
│       ├── result-export/
│       ├── template-validation/
│       └── web-ui/
├── CLAUDE.md                   # 项目级 AI 指令（使用规范）
├── 比对单机.py                 # 旧版单文件脚本（已废弃）
└── 对比单机.py                 # 参考脚本（保留作为逻辑参考）
```

## Key Implementation Details

### Session Cookie Size Issue (已解决)
- **问题**：比对结果存储在 Flask session 中导致 cookie 超过 4KB 限制
- **解决方案**：使用 pickle 将结果保存到服务器文件，session 中只存储布尔标志 `has_results`
- **相关文件**：`core/web/routes.py` (compare, result, download 路由)

### Template Validation (已实现)
- **验证规则**：
  1. 列名必须与标准模板完全一致
  2. 列的顺序必须与标准模板完全一致
  3. 不能有缺失列或多余列
- **错误提示**：提供详细的列位置信息（如 "A列应为'姓名'，实际为'XX'"）
- **相关文件**：`core/validator.py`

### File Path Handling (重要约束)
- 验证失败时必须清除 session 路径：`session.pop('local_file', None)`
- 删除文件前检查存在性：`if os.path.exists(filepath)`
- 比对前验证文件存在性，避免 FileNotFoundError
- **相关文件**：`core/web/routes.py`

### National Database Sheet Reading
- 使用 `sheet_name=0` 读取第一张工作表，不验证工作表名称
- **相关文件**：`core/validator.py`, `core/web/routes.py`
