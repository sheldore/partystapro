# File Upload Capability

## ADDED Requirements

### Requirement: 文件上传接口
系统 SHALL 提供 HTTP 端点接收用户上传的 Excel 文件。

#### Scenario: 成功上传文件
- **WHEN** 用户通过 POST 请求上传有效的 Excel 文件
- **THEN** 系统保存文件到临时目录 `uploads/<session_id>/`
- **AND** 返回 JSON 响应包含 `{"success": true, "file_id": "<uuid>"}`
- **AND** HTTP 状态码为 200

#### Scenario: 拒绝非 Excel 文件
- **WHEN** 用户上传非 `.xls` 或 `.xlsx` 文件
- **THEN** 系统拒绝上传并返回错误响应
- **AND** 响应包含 `{"success": false, "error": "仅支持 .xls 和 .xlsx 格式"}`
- **AND** HTTP 状态码为 400

#### Scenario: 拒绝超大文件
- **WHEN** 用户上传超过 10MB 的文件
- **THEN** 系统拒绝上传并返回错误响应
- **AND** 响应包含 `{"success": false, "error": "文件大小超过限制(最大 10MB)"}`
- **AND** HTTP 状态码为 413

### Requirement: 会话隔离
系统 SHALL 为每个用户会话创建独立的文件存储空间,防止不同用户的文件冲突。

#### Scenario: 新用户会话创建独立目录
- **WHEN** 用户首次访问应用
- **THEN** 系统生成唯一的会话 ID(UUID4 格式)
- **AND** 创建目录 `uploads/<session_id>/`
- **AND** 将会话 ID 存储在加密的 session cookie 中

#### Scenario: 同一会话的文件存储到相同目录
- **WHEN** 用户在同一会话中上传多个文件
- **THEN** 所有文件保存到同一个 `uploads/<session_id>/` 目录
- **AND** 文件名使用 `secure_filename()` 处理,防止路径遍历攻击

### Requirement: 临时文件清理
系统 SHALL 在比对完成后或超时后自动清理临时文件,防止磁盘空间耗尽。

#### Scenario: 比对完成后删除临时文件
- **WHEN** 比对结果生成并发送给用户后
- **THEN** 系统删除 `uploads/<session_id>/` 目录下的所有上传文件
- **AND** 保留会话 ID 用于结果下载

#### Scenario: 超时文件自动清理
- **WHEN** 定时任务检测到文件创建时间超过 1 小时
- **THEN** 系统删除该文件及其所在的会话目录
- **AND** 记录清理日志

### Requirement: 文件安全
系统 SHALL 对上传的文件进行安全检查,防止恶意文件上传。

#### Scenario: 验证文件扩展名
- **WHEN** 用户上传文件
- **THEN** 系统检查文件扩展名是否在允许列表中(`.xls`, `.xlsx`)
- **AND** 使用 `secure_filename()` 过滤文件名中的特殊字符

#### Scenario: 限制文件路径
- **WHEN** 系统保存上传文件
- **THEN** 文件仅保存到 `uploads/<session_id>/` 目录下
- **AND** 不允许 `..` 或绝对路径导致的路径遍历
