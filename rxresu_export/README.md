# rxresu export

这里放和 rxresu 反向导入相关的工具与产物。

- `resume-data-raw.json`: 从 rxresu API 拉取的原始中文简历完整结构，作为模板使用。
- `format_resume_to_schema.py`: 把网页使用的精简 JSON 填回 rxresu 完整 schema。
- `resume-data-full.json`: 默认由 `assets/resume-data-en.json` 生成，可导入 rxresu 用来生成英文简历 PDF。

生成英文完整 JSON：

```bash
python3 rxresu_export/format_resume_to_schema.py
```
