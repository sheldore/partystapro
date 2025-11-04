# template-validation Specification

## Purpose
TBD - created by archiving change update-template-validation-and-results. Update Purpose after archive.
## Requirements
### Requirement: Standard Template Validation
The system SHALL use standard template files to validate user-uploaded files:
- Local database files SHALL be validated against `core/templates/单机模板.xls`
- National database files SHALL be validated against `core/templates/全国模板.xls`

#### Scenario: Valid local database file
- **WHEN** 用户上传符合单机模板的文件
- **THEN** 系统返回验证成功消息

#### Scenario: Valid national database file
- **WHEN** 用户上传符合全国模板的文件
- **THEN** 系统返回验证成功消息

### Requirement: Column Count and Order Validation
The system SHALL validate that uploaded files have columns matching the template exactly in both count and order.

#### Scenario: Columns match exactly
- **WHEN** 上传文件的列数量和顺序与模板完全一致
- **THEN** 系统返回验证成功

#### Scenario: Missing columns detected
- **WHEN** 上传文件缺少某些列
- **THEN** 系统返回错误提示，明确列出缺少的列名称

#### Scenario: Extra columns detected
- **WHEN** 上传文件包含额外的列
- **THEN** 系统返回错误提示，明确列出多出的列名称

#### Scenario: Column order mismatch
- **WHEN** 上传文件的列顺序与模板不一致
- **THEN** 系统返回错误提示，指出顺序不匹配

### Requirement: Detailed Validation Error Messages
When validation fails, the system SHALL provide detailed error information including:
- Missing columns (listed by name)
- Extra columns (listed by name)
- Specific explanation of order mismatches

#### Scenario: Multiple validation errors
- **WHEN** 上传文件同时存在缺少列和多出列的问题
- **THEN** 系统在单个响应中列出所有问题

#### Scenario: Template file not found
- **WHEN** 标准模板文件不存在或无法读取
- **THEN** 系统返回内部错误，提示管理员检查模板文件配置

### Requirement: 单机库模板校验
系统 SHALL 验证上传的单机党员花名册是否符合标准模板格式。

#### Scenario: 单机库模板匹配成功
- **WHEN** 用户上传的单机库文件表头与 `core/templates/党员列表(导出数据).xls` 一致
- **THEN** 系统返回校验成功响应 `{"valid": true}`
- **AND** 前端显示 ✓ 通过标记

#### Scenario: 单机库模板缺少列
- **WHEN** 用户上传的单机库文件缺少必需的列(如"入党时间")
- **THEN** 系统返回校验失败响应
- **AND** 响应包含 `{"valid": false, "missing_columns": ["入党时间"]}`
- **AND** 前端显示错误:"缺少以下列: 入党时间"

#### Scenario: 单机库模板包含多余列
- **WHEN** 用户上传的单机库文件包含模板中没有的列
- **THEN** 系统返回校验失败响应
- **AND** 响应包含 `{"valid": false, "extra_columns": ["备注"]}`
- **AND** 前端显示错误:"包含多余列: 备注"

### Requirement: 全国库模板校验
系统 SHALL 验证上传的全国党员花名册是否符合标准模板格式。

#### Scenario: 全国库模板匹配成功
- **WHEN** 用户上传的全国库文件 Sheet '1' 的表头与 `core/templates/中共晋能控股煤业集团燕子山矿委员会.xls` 一致
- **THEN** 系统返回校验成功响应 `{"valid": true}`
- **AND** 前端显示 ✓ 通过标记

#### Scenario: 全国库缺少 Sheet '1'
- **WHEN** 用户上传的全国库文件不包含名为 '1' 的 Sheet
- **THEN** 系统返回校验失败响应
- **AND** 响应包含 `{"valid": false, "error": "缺少工作表 '1'"}`

#### Scenario: 全国库模板列不匹配
- **WHEN** 用户上传的全国库文件表头与模板不一致
- **THEN** 系统返回详细的差异信息
- **AND** 列出缺失和多余的列名

### Requirement: 实时校验反馈
系统 SHALL 在文件上传后立即执行校验,并通过 AJAX 响应返回结果。

#### Scenario: 上传后自动触发校验
- **WHEN** 用户通过上传框选择文件
- **THEN** 系统自动发送 AJAX 请求到校验端点
- **AND** 在 2 秒内返回校验结果
- **AND** 前端更新校验状态显示

### Requirement: 模板加载
系统 SHALL 在启动时加载标准模板文件,用于后续校验。

#### Scenario: 应用启动时加载模板
- **WHEN** Flask 应用启动
- **THEN** 系统读取 `core/templates/党员列表(导出数据).xls`
- **AND** 读取 `core/templates/中共晋能控股煤业集团燕子山矿委员会.xls` 的 Sheet '1'
- **AND** 提取表头列名并存储在内存中供校验使用

#### Scenario: 模板文件缺失时报错
- **WHEN** 应用启动但找不到模板文件
- **THEN** 系统记录错误日志并抛出异常
- **AND** 应用启动失败并显示明确的错误信息

