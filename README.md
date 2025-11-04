# 党员花名册在线比对工具

一个基于 Flask 的 Web 应用，用于比对单机党员花名册和全国党员花名册的差异。

## 功能特性

- **文件上传**：支持上传两个 Excel 文件（.xls 和 .xlsx 格式）
- **模板校验**：
  - 自动验证上传文件的表头是否符合标准模板
  - 检查列的数量和顺序是否完全一致
  - 详细提示缺少、多出的列和顺序错误
- **智能比对**：
  - 识别两个库中多出或缺少的人员
  - 逐字段比对差异（姓名、性别、民族等8个字段）
  - 自动计算党龄和年龄
- **结果展示**：
  - 在线查看比对结果，可折叠展开
  - 显示预处理后的完整数据（包含计算的党龄、年龄等字段）
  - 显示差异统计和详细对比
- **Excel 导出**：下载包含所有比对结果的多 Sheet Excel 文件
- **会话隔离**：多用户同时使用互不干扰
- **自动清理**：临时文件自动清理，保护数据安全

## 系统要求

- Python 3.7+
- 支持的浏览器：Chrome、Firefox、Edge、Safari

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd c4.5
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量（可选）

```bash
# Windows
set SECRET_KEY=your-secret-key-here

# Linux/Mac
export SECRET_KEY=your-secret-key-here
```

如不设置，系统会自动生成随机密钥。

## 运行方式

### 开发模式

```bash
python app.py
```

应用将在 http://localhost:5000 启动。

### 生产模式

使用 Gunicorn（Linux/Mac）：

```bash
gunicorn -c gunicorn_config.py app:app
```

使用 Waitress（Windows）：

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

## 使用说明

1. 访问应用首页
2. 上传**单机党员花名册**文件
3. 上传**全国党员花名册**文件
4. 等待两个文件校验通过（显示绿色✓）
5. 点击"开始比对"按钮
6. 查看比对结果，可展开/折叠各个区域
7. 点击"下载完整报告"获取 Excel 文件

## 项目结构

```
c4.5/
├── app.py                      # Flask 应用入口
├── requirements.txt            # Python 依赖
├── .gitignore                  # Git 忽略文件
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── comparison.py           # 比对引擎
│   ├── file_handler.py         # 文件处理
│   ├── validator.py            # 模板校验
│   ├── exporter.py             # 结果导出
│   ├── templates/              # 模板文件目录
│   └── web/                    # Web 模块
│       ├── __init__.py
│       └── routes.py           # 路由定义
├── templates/                  # HTML 模板
│   ├── index.html              # 主页面
│   ├── result.html             # 结果页面
│   └── 404.html                # 错误页面
├── static/                     # 静态资源
│   ├── style.css               # 样式文件
│   └── script.js               # JavaScript
├── scripts/                    # 脚本
│   └── cleanup_old_files.py    # 清理脚本
└── uploads/                    # 临时上传目录（自动创建）
```

## 定时任务配置

建议配置定时任务自动清理超时的临时文件。

### Linux/Mac (Cron)

编辑 crontab：

```bash
crontab -e
```

添加以下行（每小时执行一次）：

```
0 * * * * cd /path/to/c4.5 && python scripts/cleanup_old_files.py >> logs/cleanup.log 2>&1
```

### Windows (任务计划程序)

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每小时
4. 操作：启动程序
   - 程序：`python.exe`
   - 参数：`scripts/cleanup_old_files.py`
   - 起始于：`C:\path\to\c4.5`

## 安全注意事项

- 设置强随机的 `SECRET_KEY` 环境变量
- 部署到生产环境时使用 HTTPS
- 定期检查 `uploads/` 目录大小
- 考虑添加访问控制和用户认证

## 故障排除

### 模板文件找不到

确保 `core/templates/` 目录包含以下标准模板文件：
- `单机模板.xls` - 单机党员花名册标准模板
- `全国模板.xls` - 全国党员花名册标准模板

**注意**：上传的文件必须严格按照这些标准模板的列名和列顺序。

### 模板校验失败

如果提示模板格式不正确，请检查：
1. **缺少列**：上传文件缺少某些必需的列
2. **多余列**：上传文件包含模板中没有的列
3. **列顺序不匹配**：即使列名正确，但顺序与模板不一致也会校验失败

解决方法：使用标准模板文件作为基础，填入数据后再上传。

### 文件上传失败

- 检查文件大小是否超过 10MB
- 确认文件格式为 .xls 或 .xlsx
- 检查服务器磁盘空间是否充足

### 比对结果不正确

- 确认上传的文件格式符合模板要求
- 检查身份证号字段是否为空或格式错误
- 查看应用日志获取详细错误信息

## 技术栈

- **后端**：Flask 3.0
- **数据处理**：pandas 2.1
- **Excel 处理**：xlsxwriter, openpyxl
- **前端**：原生 HTML/CSS/JavaScript

## License

© 2024 党员花名册在线比对工具

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

## 开发者文档

如果你是开发者或 AI 助手，需要继续开发此项目，请查阅以下文档：

### 快速开始
- **[QUICKSTART.md](QUICKSTART.md)** - 5分钟快速了解项目，包含关键概念、常见任务和代码片段

### 深入理解
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构详解，包含设计决策和数据流
- **[openspec/project.md](openspec/project.md)** - 项目上下文、技术栈和约束
- **[CLAUDE.md](CLAUDE.md)** - AI 开发规范和最佳实践

### 历史记录
- **[openspec/changes/archive/](openspec/changes/archive/)** - 已完成的变更记录
  - `2025-11-03-add-web-comparison-interface/` - Web 界面实现
  - `2025-11-03-update-template-validation-and-results/` - 模板验证和结果展示优化
    - `implementation-summary.md` - 实施过程中遇到的所有问题和解决方案（重要！）

### OpenSpec 工作流
- **[openspec/AGENTS.md](openspec/AGENTS.md)** - 如何使用 OpenSpec 管理变更
- **[openspec/specs/](openspec/specs/)** - 功能规范定义
