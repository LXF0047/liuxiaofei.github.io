from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "rxresu_export"
DEFAULT_INPUT = PROJECT_ROOT / "assets" / "resume-data-en.json"
DEFAULT_TEMPLATE = EXPORT_DIR / "resume-data-raw.json"
DEFAULT_OUTPUT = EXPORT_DIR / "resume-data-full.json"

CUSTOM_SECTION_TYPES = {
    "summary",
    "profiles",
    "experience",
    "education",
    "projects",
    "skills",
    "languages",
    "interests",
    "awards",
    "certifications",
    "publications",
    "volunteer",
    "references",
    "cover-letter",
}


def clean_str(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_template_data(template: dict[str, Any]) -> dict[str, Any]:
    data = template.get("data")
    if isinstance(data, dict):
        required = {"picture", "basics", "summary", "sections", "customSections", "metadata"}
        if required.issubset(data.keys()):
            return copy.deepcopy(data)
    return copy.deepcopy(template)


def normalize_website(website: Any) -> dict[str, str]:
    if not isinstance(website, dict):
        return {"url": "", "label": ""}
    url = clean_str(website.get("url"))
    label = clean_str(website.get("label"))
    if not url:
        return {"url": "", "label": ""}
    return {"url": url, "label": label or url}


def ensure_item_common(item: dict[str, Any]) -> dict[str, Any]:
    if not clean_str(item.get("id")):
        item["id"] = str(uuid4())
    if not isinstance(item.get("hidden"), bool):
        item["hidden"] = False
    options = item.get("options")
    if not isinstance(options, dict):
        item["options"] = {"showLinkInTitle": False}
    else:
        if not isinstance(options.get("showLinkInTitle"), bool):
            options["showLinkInTitle"] = False
        item["options"] = options
    return item


def fallback_item_for_type(section_type: str) -> dict[str, Any]:
    common = ensure_item_common({})
    if section_type == "profiles":
        common.update({"icon": "", "network": "", "username": "", "website": {"url": "", "label": ""}})
    elif section_type == "experience":
        common.update(
            {"company": "", "position": "", "location": "", "period": "", "website": {"url": "", "label": ""}, "description": ""}
        )
    elif section_type == "education":
        common.update(
            {
                "school": "",
                "degree": "",
                "area": "",
                "grade": "",
                "location": "",
                "period": "",
                "website": {"url": "", "label": ""},
                "description": "",
            }
        )
    elif section_type == "projects":
        common.update({"name": "", "period": "", "website": {"url": "", "label": ""}, "description": ""})
    elif section_type == "skills":
        common.update({"icon": "", "name": "", "proficiency": "", "level": 0, "keywords": []})
    elif section_type == "languages":
        common.update({"language": "", "fluency": "", "level": 0})
    elif section_type == "interests":
        common.update({"icon": "", "name": "", "keywords": []})
    elif section_type == "awards":
        common.update({"title": "", "awarder": "", "date": "", "website": {"url": "", "label": ""}, "description": ""})
    elif section_type == "certifications":
        common.update({"title": "", "issuer": "", "date": "", "website": {"url": "", "label": ""}, "description": ""})
    elif section_type == "publications":
        common.update({"title": "", "publisher": "", "date": "", "website": {"url": "", "label": ""}, "description": ""})
    elif section_type == "volunteer":
        common.update(
            {"organization": "", "location": "", "period": "", "website": {"url": "", "label": ""}, "description": ""}
        )
    elif section_type == "references":
        common.update({"name": "", "position": "", "website": {"url": "", "label": ""}, "phone": "", "description": ""})
    return common


def choose_base_item(template_items: Any, index: int, section_type: str) -> dict[str, Any]:
    if isinstance(template_items, list):
        if index < len(template_items) and isinstance(template_items[index], dict):
            return copy.deepcopy(template_items[index])
        if template_items and isinstance(template_items[0], dict):
            return copy.deepcopy(template_items[0])
    return fallback_item_for_type(section_type)


def map_experience_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    item["company"] = clean_str(source_item.get("company"))
    item["position"] = clean_str(source_item.get("role") or source_item.get("position"))
    item["location"] = clean_str(source_item.get("location"))
    item["period"] = clean_str(source_item.get("period"))
    item["website"] = normalize_website(source_item.get("website"))
    item["description"] = clean_str(source_item.get("description"))
    return item


def map_education_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    item["school"] = clean_str(source_item.get("school"))
    item["degree"] = clean_str(source_item.get("degree"))
    item["area"] = clean_str(source_item.get("area"))
    item["grade"] = clean_str(source_item.get("grade"))
    item["location"] = clean_str(source_item.get("location"))
    item["period"] = clean_str(source_item.get("period"))
    item["website"] = normalize_website(source_item.get("website"))
    item["description"] = clean_str(source_item.get("description"))
    return item


def map_project_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    item["name"] = clean_str(source_item.get("name"))
    item["period"] = clean_str(source_item.get("period"))
    item["website"] = normalize_website(source_item.get("website"))
    item["description"] = clean_str(source_item.get("description"))
    return item


def map_award_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    item["title"] = clean_str(source_item.get("title"))
    item["awarder"] = clean_str(source_item.get("issuer") or source_item.get("awarder"))
    item["date"] = clean_str(source_item.get("date"))
    item["website"] = normalize_website(source_item.get("website"))
    item["description"] = clean_str(source_item.get("description"))
    return item


def map_cert_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    item["title"] = clean_str(source_item.get("title"))
    item["issuer"] = clean_str(source_item.get("issuer"))
    item["date"] = clean_str(source_item.get("date"))
    item["website"] = normalize_website(source_item.get("website"))
    item["description"] = clean_str(source_item.get("description"))
    return item


def map_profiles_item(source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    item = ensure_item_common(base)
    if not isinstance(item.get("icon"), str):
        item["icon"] = ""
    label = clean_str(source_item.get("label"))
    link_type = clean_str(source_item.get("type")).lower()
    url = clean_str(source_item.get("url"))
    item["network"] = link_type or label or "link"
    item["username"] = label
    item["website"] = {"url": url, "label": label or url}
    return item


def map_item_by_type(section_type: str, source_item: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    if section_type == "experience":
        return map_experience_item(source_item, base)
    if section_type == "education":
        return map_education_item(source_item, base)
    if section_type == "projects":
        return map_project_item(source_item, base)
    if section_type == "awards":
        return map_award_item(source_item, base)
    if section_type == "certifications":
        return map_cert_item(source_item, base)
    if section_type == "profiles":
        return map_profiles_item(source_item, base)
    if section_type == "publications":
        item = ensure_item_common(base)
        item["title"] = clean_str(source_item.get("title"))
        item["publisher"] = clean_str(source_item.get("publisher"))
        item["date"] = clean_str(source_item.get("date"))
        item["website"] = normalize_website(source_item.get("website"))
        item["description"] = clean_str(source_item.get("description"))
        return item
    if section_type == "volunteer":
        item = ensure_item_common(base)
        item["organization"] = clean_str(source_item.get("organization"))
        item["location"] = clean_str(source_item.get("location"))
        item["period"] = clean_str(source_item.get("period"))
        item["website"] = normalize_website(source_item.get("website"))
        item["description"] = clean_str(source_item.get("description"))
        return item
    if section_type == "references":
        item = ensure_item_common(base)
        item["name"] = clean_str(source_item.get("name"))
        item["position"] = clean_str(source_item.get("position"))
        item["website"] = normalize_website(source_item.get("website"))
        item["phone"] = clean_str(source_item.get("phone"))
        item["description"] = clean_str(source_item.get("description"))
        return item
    if section_type == "skills":
        item = ensure_item_common(base)
        if not isinstance(item.get("icon"), str):
            item["icon"] = ""
        item["name"] = clean_str(source_item.get("name"))
        item["proficiency"] = clean_str(source_item.get("proficiency"))
        item["level"] = source_item.get("level") if isinstance(source_item.get("level"), (int, float)) else 0
        item["keywords"] = source_item.get("keywords") if isinstance(source_item.get("keywords"), list) else []
        return item
    if section_type == "languages":
        item = ensure_item_common(base)
        item["language"] = clean_str(source_item.get("language"))
        item["fluency"] = clean_str(source_item.get("fluency"))
        item["level"] = source_item.get("level") if isinstance(source_item.get("level"), (int, float)) else 0
        return item
    if section_type == "interests":
        item = ensure_item_common(base)
        if not isinstance(item.get("icon"), str):
            item["icon"] = ""
        item["name"] = clean_str(source_item.get("name"))
        item["keywords"] = source_item.get("keywords") if isinstance(source_item.get("keywords"), list) else []
        return item
    return ensure_item_common(base)


def replace_section_items(
    source: dict[str, Any],
    target_sections: dict[str, Any],
    source_key: str,
    section_type: str,
    mapper: Any,
) -> None:
    if source_key not in source:
        return

    section = target_sections.get(source_key)
    if not isinstance(section, dict):
        section = {"title": "", "columns": 1, "hidden": False, "items": []}
        target_sections[source_key] = section

    source_section = source.get(source_key)
    if source_section is None:
        section["items"] = []
        return
    if not isinstance(source_section, dict):
        return

    if "title" in source_section:
        section["title"] = clean_str(source_section.get("title"))

    source_items = source_section.get("items")
    if not isinstance(source_items, list):
        section["items"] = []
        return

    template_items = section.get("items")
    mapped_items: list[dict[str, Any]] = []
    for idx, item in enumerate(source_items):
        if not isinstance(item, dict):
            continue
        base = choose_base_item(template_items, idx, section_type)
        mapped_items.append(mapper(item, base))
    section["items"] = mapped_items


def map_profile_to_target(source_profile: dict[str, Any], target: dict[str, Any]) -> None:
    basics = target.get("basics")
    if not isinstance(basics, dict):
        basics = {}
        target["basics"] = basics

    picture = target.get("picture")
    if not isinstance(picture, dict):
        picture = {}
        target["picture"] = picture

    sections = target.get("sections")
    if not isinstance(sections, dict):
        sections = {}
        target["sections"] = sections

    profiles_section = sections.get("profiles")
    if not isinstance(profiles_section, dict):
        profiles_section = {"title": "", "columns": 1, "hidden": False, "items": []}
        sections["profiles"] = profiles_section

    picture["url"] = clean_str(source_profile.get("avatar"))
    basics["name"] = clean_str(source_profile.get("name"))
    basics["headline"] = clean_str(source_profile.get("headline"))
    basics["email"] = clean_str(source_profile.get("email"))
    basics["phone"] = clean_str(source_profile.get("phone"))
    basics["location"] = clean_str(source_profile.get("location"))

    if "links" not in source_profile:
        return

    links = source_profile.get("links")
    if not isinstance(links, list):
        links = []

    website = {"url": "", "label": ""}
    website_chosen = False

    template_custom_fields = basics.get("customFields")
    custom_fields: list[dict[str, Any]] = []

    template_profile_items = profiles_section.get("items")
    profile_items: list[dict[str, Any]] = []

    custom_idx = 0
    profile_idx = 0

    for link in links:
        if not isinstance(link, dict):
            continue
        url = clean_str(link.get("url"))
        label = clean_str(link.get("label"))
        link_type = clean_str(link.get("type")).lower()
        if not url or url.startswith("mailto:") or link_type == "email":
            continue

        if not website_chosen and (link_type == "website" or url.startswith("http://") or url.startswith("https://")):
            website = {"url": url, "label": label or url}
            website_chosen = True
            if link_type == "website":
                continue

        if link_type == "link":
            base_field: dict[str, Any] = {}
            if isinstance(template_custom_fields, list):
                if custom_idx < len(template_custom_fields) and isinstance(template_custom_fields[custom_idx], dict):
                    base_field = copy.deepcopy(template_custom_fields[custom_idx])
                elif template_custom_fields and isinstance(template_custom_fields[0], dict):
                    base_field = copy.deepcopy(template_custom_fields[0])
            if not clean_str(base_field.get("id")):
                base_field["id"] = str(uuid4())
            if not isinstance(base_field.get("icon"), str):
                base_field["icon"] = ""
            base_field["text"] = label or url
            base_field["link"] = url
            custom_fields.append(base_field)
            custom_idx += 1
            continue

        profile_base = choose_base_item(template_profile_items, profile_idx, "profiles")
        profile_items.append(map_profiles_item({"label": label, "type": link_type, "url": url}, profile_base))
        profile_idx += 1

    basics["website"] = website
    basics["customFields"] = custom_fields
    profiles_section["items"] = profile_items


def map_custom_sections(source: dict[str, Any], target: dict[str, Any]) -> None:
    if "customSections" not in source:
        return

    source_custom_sections = source.get("customSections")
    if not isinstance(source_custom_sections, list):
        return

    target_custom_sections = target.get("customSections")
    if not isinstance(target_custom_sections, list):
        target_custom_sections = []
        target["customSections"] = target_custom_sections

    id_to_index: dict[str, int] = {}
    for idx, section in enumerate(target_custom_sections):
        if not isinstance(section, dict):
            continue
        sid = clean_str(section.get("id"))
        if sid:
            id_to_index[sid] = idx

    for source_section in source_custom_sections:
        if not isinstance(source_section, dict):
            continue

        source_id = clean_str(source_section.get("id"))
        source_type = clean_str(source_section.get("type"))
        if source_type not in CUSTOM_SECTION_TYPES:
            source_type = "projects"

        target_idx = id_to_index.get(source_id, -1)
        if target_idx >= 0:
            base_section = copy.deepcopy(target_custom_sections[target_idx])
        else:
            base_section = {}
            for section in target_custom_sections:
                if isinstance(section, dict) and clean_str(section.get("type")) == source_type:
                    base_section = copy.deepcopy(section)
                    break

        if not isinstance(base_section.get("columns"), (int, float)):
            base_section["columns"] = 1
        if not isinstance(base_section.get("hidden"), bool):
            base_section["hidden"] = False

        base_section["id"] = source_id or clean_str(base_section.get("id")) or str(uuid4())
        base_section["type"] = source_type
        if "title" in source_section:
            base_section["title"] = clean_str(source_section.get("title"))

        source_items = source_section.get("items")
        if isinstance(source_items, list):
            template_items = base_section.get("items")
            mapped_items: list[dict[str, Any]] = []
            for idx, source_item in enumerate(source_items):
                if not isinstance(source_item, dict):
                    continue
                item_base = choose_base_item(template_items, idx, source_type)
                mapped_items.append(map_item_by_type(source_type, source_item, item_base))
            base_section["items"] = mapped_items

        if target_idx >= 0:
            target_custom_sections[target_idx] = base_section
        else:
            target_custom_sections.append(base_section)


def map_source_to_template(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    source_profile = source.get("profile")
    if isinstance(source_profile, dict):
        map_profile_to_target(source_profile, target)

    source_summary = source.get("summary")
    if "summary" in source:
        summary = target.get("summary")
        if not isinstance(summary, dict):
            summary = {"title": "", "columns": 1, "hidden": False, "content": ""}
            target["summary"] = summary

        if source_summary is None:
            summary["content"] = ""
        elif isinstance(source_summary, dict):
            if "title" in source_summary:
                summary["title"] = clean_str(source_summary.get("title"))
            if "content" in source_summary:
                summary["content"] = clean_str(source_summary.get("content"))

    target_sections = target.get("sections")
    if not isinstance(target_sections, dict):
        target_sections = {}
        target["sections"] = target_sections

    replace_section_items(source, target_sections, "experience", "experience", map_experience_item)
    replace_section_items(source, target_sections, "education", "education", map_education_item)
    replace_section_items(source, target_sections, "projects", "projects", map_project_item)
    replace_section_items(source, target_sections, "awards", "awards", map_award_item)
    replace_section_items(source, target_sections, "certifications", "certifications", map_cert_item)

    map_custom_sections(source, target)
    return target


def build_full_resume(*, source_path: Path, template_path: Path) -> dict[str, Any]:
    source = load_json(source_path)
    template = load_json(template_path)
    target = extract_template_data(template)
    if not isinstance(target, dict):
        raise ValueError("模板不是有效的简历 JSON 对象")
    return map_source_to_template(source, target)


def resolve_template_path(arg_template: str) -> Path:
    path = Path(arg_template)
    if path.exists():
        return path
    fallback = EXPORT_DIR / "resume-data-full.json"
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"模板文件不存在: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="将精简版简历 JSON 字段替换到模板简历 JSON 中")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="输入 JSON 文件（精简版）")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="模板 JSON 文件（支持 raw payload，会读取 data 字段）")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"输入文件不存在: {input_path}")

    try:
        template_path = resolve_template_path(args.template)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    full = build_full_resume(source_path=input_path, template_path=template_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已根据模板替换字段并生成 JSON: {output_path}")


if __name__ == "__main__":
    main()
