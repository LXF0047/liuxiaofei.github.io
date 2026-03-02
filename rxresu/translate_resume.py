from __future__ import annotations

import copy
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "assets" / "resume-data.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "assets" / "resume-data-en.json"
DEFAULT_API_KEY_FILE = PROJECT_ROOT / "apikeys" / "deepseek_api_key.txt"
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

SKIP_KEYS = {
    "id",
    "resumeId",
    "resumeName",
    "generatedAt",
    "backgroundImage",
    "avatar",
    "url",
    "email",
    "phone",
    "type",
}

URL_RE = re.compile(r"^(?:https?://|mailto:)", re.IGNORECASE)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_OR_NUMBER_RE = re.compile(r"^[0-9.\-:/\s]+$")
HAS_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


@dataclass
class FieldItem:
    path: list[Any]
    key_path: str
    value: str


class DeepSeekTranslateError(Exception):
    pass


def should_translate(key: str, value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if key in SKIP_KEYS:
        return False
    if URL_RE.match(text):
        return False
    if EMAIL_RE.match(text):
        return False
    if DATE_OR_NUMBER_RE.match(text):
        return False
    if not HAS_CJK_RE.search(text):
        return False
    return True


def path_to_string(path: list[Any]) -> str:
    parts: list[str] = []
    for p in path:
        if isinstance(p, int):
            parts.append(f"[{p}]")
        else:
            if parts:
                parts.append(f".{p}")
            else:
                parts.append(str(p))
    return "".join(parts)


def set_value_by_path(data: Any, path: list[Any], value: str) -> None:
    target = data
    for p in path[:-1]:
        target = target[p]
    target[path[-1]] = value


def collect_translatable_fields(data: Any, path: list[Any] | None = None) -> list[FieldItem]:
    if path is None:
        path = []

    items: list[FieldItem] = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = [*path, key]
            if isinstance(value, str):
                if should_translate(key, value):
                    items.append(
                        FieldItem(
                            path=current_path,
                            key_path=path_to_string(current_path),
                            value=value,
                        )
                    )
            elif isinstance(value, (dict, list)):
                items.extend(collect_translatable_fields(value, current_path))
        return items

    if isinstance(data, list):
        for index, value in enumerate(data):
            current_path = [*path, index]
            if isinstance(value, str):
                parent_key = str(path[-1]) if path else ""
                if should_translate(parent_key, value):
                    items.append(
                        FieldItem(
                            path=current_path,
                            key_path=path_to_string(current_path),
                            value=value,
                        )
                    )
            elif isinstance(value, (dict, list)):
                items.extend(collect_translatable_fields(value, current_path))
        return items

    return items


def extract_json_object(text: str) -> dict[str, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise DeepSeekTranslateError(f"无法解析 DeepSeek 返回内容: {text[:200]}...")
        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, dict):
        raise DeepSeekTranslateError("DeepSeek 返回不是 JSON 对象")

    return {str(k): str(v) for k, v in parsed.items()}


def read_api_key(api_key: str = "", api_key_file: Path = DEFAULT_API_KEY_FILE) -> str:
    if api_key:
        return api_key.strip()

    env_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if env_key:
        return env_key

    if api_key_file.exists():
        file_key = api_key_file.read_text(encoding="utf-8").strip()
        if file_key:
            return file_key

    raise DeepSeekTranslateError(f"未提供 DeepSeek API Key: {api_key_file}")


def translate_simplified_map(
    *,
    api_key: str,
    base_url: str,
    model: str,
    simplified_map: dict[str, str],
    timeout: int,
) -> dict[str, str]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional resume translator. Translate Chinese to concise, natural English. "
                    "Keep original meaning, and keep HTML tags and structure unchanged if present. "
                    "Return only one valid JSON object with exactly the same keys as input. "
                    "Do not add or remove keys."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Translate all values in this simplified resume JSON to English and keep keys unchanged:\n"
                    f"{json.dumps(simplified_map, ensure_ascii=False)}"
                ),
            },
        ],
        "temperature": 0.2,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise DeepSeekTranslateError(f"网络请求失败: {exc}") from exc

    if resp.status_code != 200:
        raise DeepSeekTranslateError(f"API 调用失败: {resp.status_code} {resp.text}")

    result = resp.json()
    try:
        content = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise DeepSeekTranslateError(f"API 返回格式异常: {json.dumps(result, ensure_ascii=False)}") from exc

    return extract_json_object(content)


def translate_resume_json(
    *,
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    api_key: str = "",
    api_key_file: Path = DEFAULT_API_KEY_FILE,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    timeout: int = 120,
    verbose: bool = True,
) -> Path:
    if not input_path.exists():
        raise DeepSeekTranslateError(f"输入文件不存在: {input_path}")

    source = json.loads(input_path.read_text(encoding="utf-8"))
    translated = copy.deepcopy(source)

    items = collect_translatable_fields(source)
    if verbose:
        print(f"提取到可翻译字段数量: {len(items)}")

    if not items:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(translated, ensure_ascii=False, indent=2), encoding="utf-8")
        if verbose:
            print(f"无可翻译字段，已直接输出: {output_path}")
        return output_path

    simplified_map = {item.key_path: item.value for item in items}

    key = read_api_key(api_key=api_key, api_key_file=api_key_file)
    translated_map = translate_simplified_map(
        api_key=key,
        base_url=base_url,
        model=model,
        simplified_map=simplified_map,
        timeout=timeout,
    )

    translated_count = 0
    for item in items:
        value = translated_map.get(item.key_path, "").strip()
        if value:
            set_value_by_path(translated, item.path, value)
            translated_count += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(translated, ensure_ascii=False, indent=2), encoding="utf-8")

    if verbose:
        print(f"按 key 回填翻译数量: {translated_count}/{len(items)}")
        print(f"已输出英文简历 JSON: {output_path}")

    return output_path


if __name__ == "__main__":
    translate_resume_json()
