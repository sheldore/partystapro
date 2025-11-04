# Comparison Results Spec Deltas

## ADDED Requirements

### Requirement: Display Preprocessed Data Tables
The system SHALL display complete preprocessed data tables on the results page, including:
- Complete preprocessed local database data (with calculated 党龄, 年龄, etc.)
- Complete preprocessed national database data (with calculated 党龄, 年龄, etc.)

#### Scenario: Display local database preprocessed data
- **WHEN** 用户查看比对结果页面
- **THEN** 系统显示单机库的完整预处理数据表，包含所有计算字段

#### Scenario: Display national database preprocessed data
- **WHEN** 用户查看比对结果页面
- **THEN** 系统显示全国库的完整预处理数据表，包含所有计算字段

#### Scenario: Display calculated fields
- **WHEN** 显示预处理数据
- **THEN** 数据表必须包含：
  - 党龄（按 2024-12-31 计算）
  - 个人年龄（按 2024-12-31 计算）
  - 标准化的身份证号
  - 所有原始字段

### Requirement: Comparison Results Display
The system SHALL display both difference results and preprocessed data, ensuring users can comprehensively understand the comparison.

#### Scenario: Display both differences and full data
- **WHEN** 用户查看比对结果
- **THEN** 页面包含：
  - 差异统计摘要
  - 差异详细列表
  - 单机库预处理完整数据表
  - 全国库预处理完整数据表

#### Scenario: No differences found
- **WHEN** 两个数据库完全一致
- **THEN** 系统显示"未发现差异"消息，但仍显示预处理数据表

### Requirement: Data Table Navigation
When preprocessed data tables are large, the system SHALL provide a good browsing experience.

#### Scenario: Large dataset display
- **WHEN** 预处理数据包含大量记录
- **THEN** 表格应该：
  - 使用可折叠区域减少初始加载
  - 提供表头固定或滚动支持
  - 显示记录总数

#### Scenario: Empty dataset
- **WHEN** 某个数据库为空或无有效记录
- **THEN** 系统显示"无数据"提示，而不是空表格
