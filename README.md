# liuxiaofei.github.io

个人简历 GitHub Pages。中文简历内容从 rxresu 拉取，英文简历由 DeepSeek 翻译生成。

## 本地配置

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
- 生成 `assets/resume-data-raw.json`，保存原始 rxresu 返回数据。
- 生成 `assets/resume-data.json`，供中文页面使用。
- 调用 DeepSeek 翻译并生成 `assets/resume-data-en.json`，供英文页面使用。


## 更新 GitHub Pages

确认生成结果无误后push项目github page即可同步更新

GitHub Pages 会使用 `main` 分支里的静态文件更新站点。推送后稍等一会儿，再打开线上页面检查中英文切换是否正常。
