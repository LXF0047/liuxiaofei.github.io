from __future__ import annotations

import json
from pathlib import Path

from rxresu.resume_parser import (
    DEFAULT_RAW_OUTPUT_PATH,
    ReactiveResumeError,
    get_resume_json_by_name,
    parse_resume_payload,
    read_api_key,
    save_raw_payload,
)
from rxresu.translate_resume import DeepSeekTranslateError, translate_resume_json

PROJECT_ROOT = Path(__file__).resolve().parent
RESUME_NAME = "2025cv"
BACKGROUND_IMAGE = "assets/background.webp"

ZH_OUTPUT = PROJECT_ROOT / "assets" / "resume-data.json"
EN_OUTPUT = PROJECT_ROOT / "assets" / "resume-data-en.json"
RAW_OUTPUT = DEFAULT_RAW_OUTPUT_PATH


def generate_chinese_resume() -> Path:
    api_key = read_api_key()
    payload = get_resume_json_by_name(api_key=api_key, resume_name=RESUME_NAME)

    if not payload:
        raise RuntimeError(f"未找到名为 {RESUME_NAME} 的简历")

    save_raw_payload(payload, RAW_OUTPUT)
    parsed = parse_resume_payload(payload, resume_name=RESUME_NAME, background_image=BACKGROUND_IMAGE)
    ZH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ZH_OUTPUT.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    return ZH_OUTPUT


def generate_bilingual_resume() -> tuple[Path, Path]:
    zh_path = generate_chinese_resume()
    print(f"原始简历 JSON 已生成: {RAW_OUTPUT}")
    print(f"中文简历 JSON 已生成: {zh_path}")

    en_path = translate_resume_json(
        input_path=zh_path,
        output_path=EN_OUTPUT,
        verbose=True,
    )
    print(f"英文简历 JSON 已生成: {en_path}")
    return zh_path, en_path


def main() -> None:
    try:
        generate_bilingual_resume()
    except (ReactiveResumeError, DeepSeekTranslateError, RuntimeError, FileNotFoundError) as exc:
        raise SystemExit(f"执行失败: {exc}") from exc


if __name__ == "__main__":
    main()
