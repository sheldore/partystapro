# Comparison Engine Capability

## ADDED Requirements

### Requirement: 数据预处理
系统 SHALL 在比对前对两个数据源进行标准化预处理。

#### Scenario: 单机库数据预处理
- **WHEN** 系统接收到单机库 DataFrame
- **THEN** 增加"序号"列,值为从 1 开始的连续整数
- **AND** 计算"党龄"列,公式为 `(2024-12-31 - 入党时间) / 365` 的整数部分
- **AND** 计算"年龄"列,从身份证号的第 7-14 位提取出生日期,计算到 2024-12-31 的完整年数
- **AND** 增加"人员类别"列,入党时间在 2024 年的为"预备党员",否则为"正式党员"
- **AND** 将"身份证号"列转换为大写字符串格式

#### Scenario: 全国库数据预处理
- **WHEN** 系统接收到全国库 DataFrame
- **THEN** 增加"序号"列,值为从 1 开始的连续整数
- **AND** 计算"党龄"列,公式为 `(2024-12-31 - 入党日期) / 365` 的整数部分
- **AND** 计算"年龄"列,从身份证号码的第 7-14 位提取出生日期,计算到 2024-12-31 的完整年数
- **AND** 将"身份证号码"列转换为大写字符串格式

### Requirement: 人员差异比对
系统 SHALL 基于身份证号识别两个数据源中多出或缺少的人员。

#### Scenario: 识别单机库多出的人员
- **WHEN** 系统执行比对
- **THEN** 找出所有身份证号存在于单机库但不存在于全国库的记录
- **AND** 返回完整的 DataFrame 包含这些人员的所有字段

#### Scenario: 识别全国库多出的人员
- **WHEN** 系统执行比对
- **THEN** 找出所有身份证号码存在于全国库但不存在于单机库的记录
- **AND** 返回完整的 DataFrame 包含这些人员的所有字段

#### Scenario: 两个库完全一致
- **WHEN** 单机库和全国库的身份证号完全相同
- **THEN** "单机多出人员"和"全国多出人员"结果均为空 DataFrame

### Requirement: 字段差异比对
系统 SHALL 对于身份证号相同的人员,逐字段比对其信息差异。

#### Scenario: 识别姓名差异
- **WHEN** 系统比对"姓名"字段
- **THEN** 通过身份证号关联两表,找出姓名不一致的记录
- **AND** 返回 DataFrame 包含:姓名、身份证号、单机表姓名、全国表姓名

#### Scenario: 比对多个字段
- **WHEN** 系统执行完整比对
- **THEN** 依次比对以下字段:姓名、性别、民族、出生日期、学历、入党时间、个人身份、人员类别
- **AND** 对于"入党时间"字段,单机库使用"入党时间",全国库使用"入党日期"
- **AND** 对于"个人身份"字段,单机库使用"个人身份",全国库使用"工作岗位"

#### Scenario: 某字段无差异
- **WHEN** 系统比对"性别"字段
- **AND** 所有身份证号相同的记录性别值均相同
- **THEN** 返回空 DataFrame

### Requirement: 比对结果汇总
系统 SHALL 将所有比对结果汇总为结构化数据,供展示和导出使用。

#### Scenario: 生成完整比对报告
- **WHEN** 比对完成
- **THEN** 返回字典格式的结果:
```python
{
  "local_extra": DataFrame,      # 单机多出人员
  "national_extra": DataFrame,   # 全国多出人员
  "diff_姓名": DataFrame,
  "diff_性别": DataFrame,
  "diff_民族": DataFrame,
  "diff_出生日期": DataFrame,
  "diff_学历": DataFrame,
  "diff_入党时间": DataFrame,
  "diff_个人身份": DataFrame,
  "diff_人员类别": DataFrame
}
```

### Requirement: 错误处理
系统 SHALL 处理数据异常情况,防止比对失败。

#### Scenario: 处理缺失的身份证号
- **WHEN** 数据中存在身份证号为空或 NaN 的记录
- **THEN** 系统跳过该记录并记录警告日志
- **AND** 继续处理其他有效记录

#### Scenario: 处理日期格式错误
- **WHEN** 入党时间字段包含无效日期(如 "未知")
- **THEN** 系统将党龄设为 NaN
- **AND** 记录警告日志但不中断比对流程
