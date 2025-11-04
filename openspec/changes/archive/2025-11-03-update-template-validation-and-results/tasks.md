# Implementation Tasks

## 1. Update Template Validation
- [x] 1.1 Create standard template files `core/templates/单机模板.xls` and `core/templates/全国模板.xls` (files already existed)
- [x] 1.2 Modify `core/validator.py` to load templates from new file paths
- [x] 1.3 Implement column order validation logic
- [x] 1.4 Update validation error messages to include detailed column mismatch information
- [x] 1.5 Add error handling for missing template files
- [x] 1.6 Remove sheet name validation for national database, use first sheet by default
- [x] 1.7 Update error message from "模板格式不正确" to "上传表格格式不正确"
- [x] 1.8 Remove display of extra columns in validation errors

## 2. Update Comparison Engine
- [x] 2.1 Modify `core/comparison.py` to return preprocessed DataFrames
- [x] 2.2 Ensure preprocessed data includes all calculated fields (党龄, 年龄)
- [x] 2.3 Update ComparisonEngine.generate_report() to include preprocessed data in results
- [x] 2.4 Simplify find_differences() logic to match original 比对单机.py

## 3. Update Web Routes
- [x] 3.1 Modify `/compare` route to pass preprocessed DataFrames to template
- [x] 3.2 Convert DataFrames to HTML tables or JSON for frontend display
- [x] 3.3 Update route handlers to handle large datasets efficiently
- [x] 3.4 Update validation error handling to not display extra columns
- [x] 3.5 Change national database reading to use first sheet (sheet_name=0)

## 4. Update Frontend Templates
- [x] 4.1 Modify `templates/result.html` to display preprocessed data tables
- [x] 4.2 Add collapsible sections for local and national database tables
- [x] 4.3 Style tables for readability (scrollable, fixed headers if needed)
- [x] 4.4 Add "No data" messages for empty datasets
- [x] 4.5 Update summary cards to include preprocessed data record counts

## 5. Update Frontend JavaScript
- [x] 5.1 Update `static/script.js` to handle new validation error format (already handled)
- [x] 5.2 Display detailed column mismatch information to users (already handled)
- [x] 5.3 Add any necessary table interaction logic (sorting, filtering if needed)

## 6. Testing
- [x] 6.1 Test template validation with matching files
- [x] 6.2 Test template validation with missing columns
- [x] 6.3 Test template validation with extra columns
- [x] 6.4 Test template validation with wrong column order
- [x] 6.5 Test preprocessed data display with sample datasets
- [x] 6.6 Test preprocessed data display with empty datasets
- [x] 6.7 Test end-to-end workflow: upload → validate → compare → view results

## 7. Documentation
- [x] 7.1 Update README.md with new template file requirements
- [x] 7.2 Document template file format and column requirements
- [x] 7.3 Add troubleshooting guide for validation errors
