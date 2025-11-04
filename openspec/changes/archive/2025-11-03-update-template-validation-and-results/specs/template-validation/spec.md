# Template Validation Spec Deltas

## ADDED Requirements

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
