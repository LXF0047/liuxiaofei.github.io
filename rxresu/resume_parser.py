from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESUME_NAME = "2025cv"
DEFAULT_API_KEY_PATH = PROJECT_ROOT / "apikeys" /"rxresu_api_key.txt"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "assets" / "resume-data.json"
DEFAULT_BACKGROUND = "assets/background.webp"
DEFAULT_BASE_URL = "https://rxresu.me/api/openapi"


class ReactiveResumeError(Exception):
    pass


def get_resume_json_by_name(
    api_key: str,
    resume_name: str,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any] | None:
    if not api_key:
        raise ValueError("api_key 不能为空")

    headers = {"x-api-key": api_key}

    try:
        resp = requests.get(f"{base_url}/resumes", headers=headers, timeout=10)
    except requests.RequestException as exc:
        raise ReactiveResumeError(f"网络错误: {exc}") from exc

    if resp.status_code in (401, 403):
        raise ReactiveResumeError("API Key 无效或已过期")
    if resp.status_code != 200:
        raise ReactiveResumeError(f"获取简历列表失败: {resp.status_code}")

    resumes = resp.json()
    resume_name_lower = resume_name.lower()
    matched = [r for r in resumes if r.get("name", "").lower() == resume_name_lower]
    if not matched:
        return None

    resume_id = matched[0]["id"]
    try:
        detail_resp = requests.get(f"{base_url}/resumes/{resume_id}", headers=headers, timeout=10)
    except requests.RequestException as exc:
        raise ReactiveResumeError(f"网络错误: {exc}") from exc

    if detail_resp.status_code in (401, 403):
        raise ReactiveResumeError("API Key 无效或已过期")
    if detail_resp.status_code != 200:
        raise ReactiveResumeError(f"获取简历详情失败: {detail_resp.status_code}")

    payload = detail_resp.json()
    if not payload:
        raise ReactiveResumeError("获取简历详情失败: 不存在当前简历名称")

    return payload


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(has_value(v) for v in value)
    if isinstance(value, dict):
        return any(
            has_value(v)
            for k, v in value.items()
            if k not in {"id", "hidden", "options", "columns", "type"}
        )
    return True


def clean_str(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def clean_website(website: Any) -> dict[str, str] | None:
    if not isinstance(website, dict):
        return None
    url = clean_str(website.get("url"))
    label = clean_str(website.get("label"))
    if not url:
        return None
    return {"url": url, "label": label or url}


def build_profile(data: dict[str, Any], background_image: str) -> dict[str, Any]:
    basics = data.get("basics", {})
    picture = data.get("picture", {})
    sections = data.get("sections", {})

    profile: dict[str, Any] = {
        "name": clean_str(basics.get("name")),
        "headline": clean_str(basics.get("headline")),
        "email": clean_str(basics.get("email")),
        "phone": clean_str(basics.get("phone")),
        "location": clean_str(basics.get("location")),
        "backgroundImage": background_image,
        "avatar": clean_str(picture.get("url")),
        "links": [],
    }

    if profile["email"]:
        profile["links"].append(
            {
                "label": "Email",
                "url": f"mailto:{profile['email']}",
                "type": "email",
            }
        )

    basics_website = clean_website(basics.get("website"))
    if basics_website:
        profile["links"].append(
            {
                "label": basics_website["label"],
                "url": basics_website["url"],
                "type": "website",
            }
        )

    profiles_section = sections.get("profiles", {})
    if not profiles_section.get("hidden"):
        for item in profiles_section.get("items", []):
            if item.get("hidden"):
                continue
            website = clean_website(item.get("website"))
            if not website:
                continue
            network = clean_str(item.get("network")) or clean_str(item.get("username"))
            profile["links"].append(
                {
                    "label": network or website["label"],
                    "url": website["url"],
                    "type": (network or "link").lower(),
                }
            )

    custom_fields = basics.get("customFields", [])
    for field in custom_fields:
        text = clean_str(field.get("text"))
        link = clean_str(field.get("link"))
        if not text:
            continue
        profile["links"].append(
            {
                "label": text,
                "url": link,
                "type": "link",
            }
        )

    dedup = set()
    links = []
    for link in profile["links"]:
        key = (link.get("label"), link.get("url"))
        if key in dedup:
            continue
        dedup.add(key)
        links.append(link)
    profile["links"] = links

    return profile


def build_summary(data: dict[str, Any]) -> dict[str, Any] | None:
    summary = data.get("summary", {})
    if summary.get("hidden"):
        return None
    content = clean_str(summary.get("content"))
    if not content:
        return None
    return {
        "title": clean_str(summary.get("title")) or "专业技能",
        "content": content,
    }


def parse_experience_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "company": clean_str(item.get("company")),
        "role": clean_str(item.get("position")),
        "location": clean_str(item.get("location")),
        "period": clean_str(item.get("period")),
        "description": clean_str(item.get("description")),
        "website": clean_website(item.get("website")),
    }


def parse_project_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": clean_str(item.get("name")),
        "period": clean_str(item.get("period")),
        "description": clean_str(item.get("description")),
        "website": clean_website(item.get("website")),
    }


def parse_education_item(item: dict[str, Any]) -> dict[str, Any]:
    degree = clean_str(item.get("degree"))
    area = clean_str(item.get("area"))
    degree_area = " · ".join(part for part in [degree, area] if part)
    return {
        "school": clean_str(item.get("school")),
        "degree": degree,
        "area": area,
        "degreeArea": degree_area,
        "location": clean_str(item.get("location")),
        "period": clean_str(item.get("period")),
        "description": clean_str(item.get("description")),
        "website": clean_website(item.get("website")),
    }


def parse_cert_item(item: dict[str, Any], is_award: bool = False) -> dict[str, Any]:
    return {
        "title": clean_str(item.get("title")),
        "issuer": clean_str(item.get("awarder" if is_award else "issuer")),
        "date": clean_str(item.get("date")),
        "description": clean_str(item.get("description")),
        "website": clean_website(item.get("website")),
    }


def parse_list_section(
    sections: dict[str, Any],
    section_id: str,
    default_title: str,
    parser: Any,
) -> dict[str, Any] | None:
    section = sections.get(section_id, {})
    if section.get("hidden"):
        return None

    items: list[dict[str, Any]] = []
    for item in section.get("items", []):
        if item.get("hidden"):
            continue
        normalized = parser(item)
        if has_value(normalized):
            items.append(normalized)

    if not items:
        return None

    return {
        "title": clean_str(section.get("title")) or default_title,
        "items": items,
    }


def parse_custom_sections(custom_sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []

    parser_map = {
        "experience": parse_experience_item,
        "projects": parse_project_item,
        "education": parse_education_item,
        "awards": lambda item: parse_cert_item(item, is_award=True),
        "certifications": parse_cert_item,
    }

    for section in custom_sections:
        if section.get("hidden"):
            continue

        section_type = clean_str(section.get("type"))
        item_parser = parser_map.get(section_type)
        if item_parser is None:
            continue

        items = []
        for item in section.get("items", []):
            if item.get("hidden"):
                continue
            normalized = item_parser(item)
            if has_value(normalized):
                items.append(normalized)

        if not items:
            continue

        parsed.append(
            {
                "id": clean_str(section.get("id")),
                "type": section_type,
                "title": clean_str(section.get("title")) or "补充经历",
                "items": items,
            }
        )

    return parsed


def build_footer(profile: dict[str, Any]) -> dict[str, str]:
    year = datetime.now().year
    name = profile.get("name") or "Resume"
    headline = profile.get("headline")
    quote = f"{headline}" if headline else ""
    return {
        "copy": f"© {year} {name}",
        "quote": quote,
    }


def parse_resume_payload(payload: dict[str, Any], resume_name: str, background_image: str) -> dict[str, Any]:
    data = payload.get("data", {})
    sections = data.get("sections", {})

    profile = build_profile(data, background_image)
    summary = build_summary(data)

    parsed = {
        "meta": {
            "resumeName": resume_name,
            "resumeId": clean_str(payload.get("id")),
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
        },
        "profile": profile,
        "summary": summary,
        "experience": parse_list_section(sections, "experience", "工作经历", parse_experience_item),
        "projects": parse_list_section(sections, "projects", "项目经历", parse_project_item),
        "education": parse_list_section(sections, "education", "教育经历", parse_education_item),
        "awards": parse_list_section(
            sections,
            "awards",
            "荣誉",
            lambda item: parse_cert_item(item, is_award=True),
        ),
        "certifications": parse_list_section(sections, "certifications", "证书与专利", parse_cert_item),
        "customSections": parse_custom_sections(data.get("customSections", [])),
    }

    parsed["footer"] = build_footer(profile)
    return parsed


def read_api_key(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"API key 文件不存在: {path}")
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="拉取并解析 Reactive Resume JSON")
    parser.add_argument("--resume-name", default=DEFAULT_RESUME_NAME, help="简历名称")
    parser.add_argument("--api-key", default="", help="OpenAPI key，可选")
    parser.add_argument("--api-key-file", default=str(DEFAULT_API_KEY_PATH), help="API key 文件路径")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="输出 JSON 路径")
    parser.add_argument("--background-image", default=DEFAULT_BACKGROUND, help="背景图路径（写入输出 JSON）")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Reactive Resume OpenAPI 地址")
    args = parser.parse_args()

    api_key = args.api_key or read_api_key(Path(args.api_key_file))

    try:
        payload = get_resume_json_by_name(
            api_key=api_key,
            resume_name=args.resume_name,
            base_url=args.base_url,
        )
    except ReactiveResumeError as exc:
        raise SystemExit(f"获取简历失败: {exc}") from exc

    if not payload:
        raise SystemExit(f"未找到名为 {args.resume_name} 的简历")

    parsed = parse_resume_payload(payload, args.resume_name, args.background_image)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已输出解析后的简历数据: {output_path}")


if __name__ == "__main__":
    main()
