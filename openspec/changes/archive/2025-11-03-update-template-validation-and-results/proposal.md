# Update Template Validation and Results Display

## Why
当前的模板验证使用导出的数据文件作为模板，而不是标准模板文件。同时，用户只能看到差异结果，无法查看完整的预处理后的对比数据（包含计算出的党龄、年龄等字段）。这降低了验证的准确性和结果的透明度。

## What Changes
- 更改模板验证以使用标准模板文件：`core/templates/单机模板.xls` 和 `core/templates/全国模板.xls`
- 添加严格的列顺序验证（不仅检查列是否存在，还要验证顺序是否一致）
- 在结果页面上显示预处理后的完整数据表（不仅显示差异）
- 改进验证错误提示，明确指出缺少或多出的列及其位置

## Impact
- Affected specs:
  - `template-validation` (modified)
  - `comparison-results` (modified)
- Affected code:
  - `core/validator.py` - 更改模板文件路径，添加列顺序验证
  - `core/web/routes.py` - 传递完整预处理数据到结果页面
  - `templates/result.html` - 添加预处理数据表显示
  - `core/comparison.py` - 可能需要返回完整预处理数据
