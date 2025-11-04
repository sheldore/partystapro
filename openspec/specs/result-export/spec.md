# result-export Specification

## Purpose
TBD - created by archiving change add-web-comparison-interface. Update Purpose after archive.
## Requirements
### Requirement: Excel 多 Sheet 导出
系统 SHALL 生成包含所有比对结果的 Excel 文件,每个结果部分占用独立的 Sheet。

#### Scenario: 生成完整比对结果 Excel
- **WHEN** 用户请求下载比对结果
- **THEN** 系统使用 `pandas.ExcelWriter` 和 `xlsxwriter` 引擎创建 Excel 文件
- **AND** 包含以下 Sheet(如果对应结果非空):
  - "单机多出人员"
  - "全国多出人员"
  - "姓名差异"
  - "性别差异"
  - "民族差异"
  - "出生日期差异"
  - "学历差异"
  - "入党时间差异"
  - "个人身份差异"
  - "人员类别差异"

#### Scenario: 跳过空结果 Sheet
- **WHEN** 某个比对结果为空(如"姓名差异"没有记录)
- **THEN** 系统仍然创建该 Sheet
- **AND** Sheet 中仅包含表头,无数据行

#### Scenario: Excel 文件命名
- **WHEN** 系统生成 Excel 文件
- **THEN** 文件名格式为 `比对结果_YYYYMMDDHHmmss.xlsx`
- **AND** 时间戳使用服务器本地时间

### Requirement: 文件下载响应
系统 SHALL 提供 HTTP 端点,允许用户下载生成的 Excel 文件。

#### Scenario: 下载比对结果文件
- **WHEN** 用户点击"下载比对结果"按钮
- **THEN** 浏览器发送 GET 请求到 `/download` 端点
- **AND** 服务器返回 Excel 文件,Content-Type 为 `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **AND** 响应头包含 `Content-Disposition: attachment; filename="比对结果_<timestamp>.xlsx"`
- **AND** HTTP 状态码为 200

#### Scenario: 下载不存在的结果
- **WHEN** 用户尝试下载但会话中没有比对结果
- **THEN** 系统返回 404 错误
- **AND** 响应包含 `{"error": "未找到比对结果,请先执行比对"}`

### Requirement: 临时文件管理
系统 SHALL 在生成下载文件后自动清理临时 Excel 文件。

#### Scenario: 下载完成后删除临时文件
- **WHEN** Excel 文件发送给用户后
- **THEN** 系统立即删除临时 Excel 文件
- **AND** 保留比对结果数据在会话中,允许用户再次下载

### Requirement: 数据格式化
系统 SHALL 在导出 Excel 时保持数据的可读性和格式一致性。

#### Scenario: 保留列顺序
- **WHEN** 导出"单机多出人员" Sheet
- **THEN** 列的顺序与原始单机库文件一致
- **AND** 序号列排在第一位

#### Scenario: 格式化日期列
- **WHEN** 导出包含日期的列(如"入党时间")
- **THEN** 日期格式为 `YYYY-MM-DD`
- **AND** 空值显示为空单元格(不是 "NaN" 或 "NaT")

#### Scenario: 差异表格列名清晰
- **WHEN** 导出字段差异 Sheet(如"姓名差异")
- **THEN** 列名为:姓名、身份证号、单机表信息、全国表信息
- **AND** 表头使用加粗格式

