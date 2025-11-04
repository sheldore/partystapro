# 快速开始指南（为 AI 助手准备）

本指南帮助新对话快速理解项目并继续开发。

## 一、5分钟了解项目

### 项目是什么？
一个基于 Flask 的 Web 应用，用于比对两个 Excel 文件（单机党员花名册 vs 全国党员花名册），识别差异并生成报告。

### 核心功能
1. 文件上传和模板验证
2. 数据比对（找出多出/缺少的人员，逐字段对比差异）
3. 结果展示（Web页面）和导出（Excel）

### 技术栈
- **后端**：Flask 3.0, pandas 2.1
- **前端**：原生 HTML/CSS/JavaScript
- **存储**：文件系统 + pickle

## 二、项目结构速查

```
核心模块（按重要性排序）：
├── core/web/routes.py          ★★★ 路由和业务流程控制
├── core/comparison.py          ★★★ 比对引擎核心逻辑
├── core/validator.py           ★★☆ 模板校验
├── core/file_handler.py        ★☆☆ 文件处理工具
├── core/exporter.py            ★☆☆ Excel 导出
└── templates/result.html       ★★☆ 结果展示页面

配置和入口：
├── app.py                      Flask 应用入口
├── requirements.txt            依赖列表
└── README.md                   用户文档

文档（必读）：
├── ARCHITECTURE.md             系统架构详解（本文档的补充）
├── openspec/project.md         项目上下文和约束
└── openspec/changes/archive/   历史变更和实施经验
    └── */implementation-summary.md  ← 重要！包含所有坑和解决方案
```

## 三、关键概念和约束

### 1. Session 管理（重要！）
```python
# Session 中只存储轻量级数据
session['session_id']      # 会话 ID
session['local_file']      # 单机库文件路径
session['national_file']   # 全国库文件路径
session['has_results']     # 是否有比对结果（布尔值）

# 比对结果存储在文件系统
uploads/{session_id}/results.pkl  # 使用 pickle 存储
```

**为什么？** Flask session 基于 cookie，大小限制 4KB。比对结果太大（5000+ 字节），必须存服务器端。

### 2. 文件路径处理（必须遵守！）
```python
# 三个必须遵守的规则：
1. 验证失败时清除 session：
   session.pop('local_file', None)

2. 删除文件前检查存在性：
   if os.path.exists(filepath):
       os.remove(filepath)

3. 比对前验证文件存在性：
   if not os.path.exists(local_file):
       return error
```

**为什么？** 防止 FileNotFoundError。历史bug：验证失败删除文件但未清理session，导致后续操作失败。

### 3. 模板验证规则
```python
# 三个验证项：
1. 列名必须完全匹配
2. 列的顺序必须完全一致  ← 注意：顺序也要验证！
3. 不能有缺失列或多余列

# 错误提示格式：
"A列应为'姓名'，实际为'XX'；B列应为'所在党支部'，实际为'YY'"
```

### 4. 全国库特殊处理
```python
# 使用第一张工作表，不验证工作表名称
pd.read_excel(file_path, sheet_name=0)  # ← 必须是 0 不是 '1'
```

## 四、常见开发任务

### 任务1：添加新的比对字段
1. 修改 `core/comparison.py` 的 `generate_report()` 方法
2. 在 `diff_fields` 列表中添加新字段名
3. 调用 `self.compare_field(新字段名)`
4. 更新 `templates/result.html` 添加新字段的显示

### 任务2：修改验证逻辑
1. 修改 `core/validator.py`
2. 注意保持列顺序验证
3. 更新错误提示信息
4. 同时更新 `upload_local` 和 `upload_national` 路由的错误处理

### 任务3：优化性能
1. 数据处理：使用 pandas 向量化操作，避免循环
2. 大文件处理：考虑使用 Celery 异步任务
3. 缓存：使用 Redis 缓存重复文件的比对结果

### 任务4：添加新路由
1. 在 `core/web/routes.py` 中定义路由函数
2. 使用 `@app.route()` 装饰器
3. 返回 JSON 或渲染模板
4. 添加错误处理和日志记录

## 五、历史问题和解决方案（必读！）

所有历史问题详见：
- `openspec/changes/archive/2025-11-03-update-template-validation-and-results/implementation-summary.md`

**最重要的7个问题**：
1. ✅ Session cookie 过大 → 使用 pickle 存文件
2. ✅ 文件路径管理混乱 → 添加清理和检查机制
3. ✅ 验证错误提示不清楚 → 添加详细的列位置信息
4. ✅ 全国库工作表名称问题 → 使用 sheet_name=0
5. ✅ DataFrame JSON序列化 → 改用 pickle
6. ✅ 中文引号语法错误 → 使用英文引号
7. ✅ 比对逻辑复杂 → 简化为 isin() 操作

## 六、开发工作流

### 使用 OpenSpec 管理变更
```bash
# 1. 创建变更提案
/openspec:proposal

# 2. 实施变更（会自动创建任务列表）
/openspec:apply <change-id>

# 3. 完成后归档
/openspec:archive <change-id>
```

### 调试应用
```bash
# 启动开发服务器
python app.py

# 查看日志
# 日志会输出到控制台，级别为 INFO

# 检查上传目录
ls uploads/

# 清理测试数据
python scripts/cleanup_old_files.py
```

## 七、快速测试检查清单

在提交代码前，确保：

- [ ] 文件上传功能正常
- [ ] 模板验证能正确识别错误
- [ ] 比对功能不报错
- [ ] 结果页面能正常显示
- [ ] Excel 下载功能正常
- [ ] Session 清理正常（验证失败后重新上传）
- [ ] 没有 FileNotFoundError
- [ ] 日志中没有错误信息

## 八、重要文档链接

**必读文档（按优先级）**：
1. `ARCHITECTURE.md` - 系统架构详解
2. `openspec/project.md` - 项目上下文
3. `openspec/changes/archive/*/implementation-summary.md` - 实施经验
4. `README.md` - 用户使用说明
5. `CLAUDE.md` - AI 开发规范

**OpenSpec 文档**：
- `openspec/AGENTS.md` - OpenSpec 工作流说明
- `openspec/specs/` - 功能规范定义

## 九、代码片段速查

### 读取上传文件
```python
df = pd.read_excel(file_path)  # 单机库
df = pd.read_excel(file_path, sheet_name=0)  # 全国库
```

### Session 操作
```python
# 获取
session_id = session.get('session_id')
local_file = session.get('local_file')

# 设置
session['key'] = value
session.modified = True

# 清除
session.pop('key', None)
```

### 文件操作
```python
# 保存比对结果
with open(results_file, 'wb') as f:
    pickle.dump(results, f)

# 读取比对结果
with open(results_file, 'rb') as f:
    results = pickle.load(f)

# 删除文件（安全）
if os.path.exists(filepath):
    os.remove(filepath)
```

### 错误处理
```python
try:
    # 业务逻辑
    pass
except Exception as e:
    logger.error(f"操作失败: {e}")
    session.pop('file_key', None)  # 清理 session
    return jsonify({'success': False, 'error': str(e)}), 500
```

## 十、联系和支持

- 遇到问题先查阅 `implementation-summary.md`
- 查看归档的变更了解历史决策
- 遵循 `CLAUDE.md` 中的开发规范
- 使用 OpenSpec 管理新功能开发

---

**最后提醒**：
1. 所有文件路径操作前都要检查文件是否存在
2. Session 中不要存储大对象
3. 验证失败必须清理 session
4. 参考已归档的变更了解最佳实践
