# liuxiaofei.github.io

个人简历 GitHub Pages。中文简历内容从 rxresu 拉取，英文简历由 DeepSeek 翻译生成。

项目里有两条流程：

- 网页展示流程：生成 `assets/resume-data.json` 和 `assets/resume-data-en.json`，供 GitHub Pages 中英文切换使用。
- rxresu 反向导入流程：把英文网页 JSON 重新填回 rxresu 完整 schema，生成可导入 rxresu 的英文简历 JSON，再在 rxresu 网站里导出英文 PDF。

## 本地配置

不要把 API key 提交到 Git。首次使用时在项目根目录创建 `.env`：

```env
RXRESU_API_KEY=your_rxresu_key
DEEPSEEK_API_KEY=your_deepseek_key
```

当前脚本默认从 rxresu 拉取名为 `2025cv` 的简历；如果 rxresu 里的简历名称变了，修改 `parse_resume.py` 里的 `RESUME_NAME`。

## 生成或更新简历数据

在 rxresu 中改好中文简历后，回到本仓库根目录执行：

```bash
python3 parse_resume.py
```

这个命令会：

- 从 rxresu 拉取中文简历。
- 生成 `rxresu_export/resume-data-raw.json`，保存原始 rxresu 返回数据，作为反向导入模板。
- 生成 `assets/resume-data.json`，供中文页面使用。
- 调用 DeepSeek 翻译并生成 `assets/resume-data-en.json`，供英文页面使用。

如果只想单独拉取中文数据：

```bash
python3 rxresu/resume_parser.py
```

如果只想基于已有中文 JSON 重新生成英文数据：

```bash
python3 rxresu/translate_resume.py
```

## 生成可导入 rxresu 的英文完整 JSON

如果你想在 rxresu 网站里生成英文 PDF，需要先把本项目生成的英文网页 JSON 反向转换成 rxresu 完整格式：

```bash
python3 rxresu_export/format_resume_to_schema.py
```

默认输入和输出：

- 输入：`assets/resume-data-en.json`
- 模板：`rxresu_export/resume-data-raw.json`
- 输出：`rxresu_export/resume-data-full.json`

生成后的 `rxresu_export/resume-data-full.json` 可以导入 rxresu 网站，再用 rxresu 的导出功能生成英文简历 PDF。

如果要生成中文完整 JSON，可以显式指定中文输入：

```bash
python3 rxresu_export/format_resume_to_schema.py \
  --input assets/resume-data.json \
  --output rxresu_export/resume-data-full-zh.json
```

## 本地预览和下载 PDF

启动本地静态服务器：

```bash
python3 -m http.server 8000
```

浏览器打开：

```text
http://127.0.0.1:8000/
```

页面右上角按钮可在中文和英文之间切换。

下载 PDF 有两种方式：

- GitHub Pages 网页版 PDF：在本地或线上页面用浏览器打印保存，中英文各保存一次。
- rxresu 标准模板 PDF：把 `rxresu_export/resume-data-full.json` 导入 rxresu 网站，然后在 rxresu 里导出 PDF。

## 更新 GitHub Pages

确认生成结果无误后 push 项目到 GitHub 即可同步更新：

```bash
git status
git add assets/resume-data.json assets/resume-data-en.json rxresu_export README.md
git commit -m "Update resume"
git push origin main
```

GitHub Pages 会使用 `main` 分支里的静态文件更新站点。推送后稍等一会儿，再打开线上页面检查中英文切换是否正常。

## 目录说明

- `assets/resume-data.json`: 网页中文简历数据。
- `assets/resume-data-en.json`: 网页英文简历数据。
- `rxresu_export/resume-data-raw.json`: rxresu 原始完整 JSON，用作反向导入模板。
- `rxresu_export/resume-data-full.json`: 反向生成的 rxresu 完整英文 JSON，可导入 rxresu 生成英文 PDF。
- `rxresu_export/format_resume_to_schema.py`: 反向转换脚本。
- `.env`: 本地 API key，只保存在本机，不提交。
