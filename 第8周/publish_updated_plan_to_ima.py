#!/usr/bin/env python3
"""Publish the updated Week 8 Day 1 lesson and Week 8-13 plan to IMA."""

import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path("/root/learning-notebooks")
CLIENT_ID = Path("/root/.config/ima/client_id").read_text().strip()
API_KEY = Path("/root/.config/ima/api_key").read_text().strip()
KNOWLEDGE_BASE_ID = "HNElfvrjmpN_CjiNyuTbG8fGaPUJgFPf6ElylvVelys="
HEADERS = {
    "ima-openapi-clientid": CLIENT_ID,
    "ima-openapi-apikey": API_KEY,
    "Content-Type": "application/json",
}


def post(path: str, payload: dict) -> dict:
    response = requests.post(f"https://ima.qq.com/{path}", headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()
    if body.get("code") != 0:
        raise RuntimeError(json.dumps(body, ensure_ascii=False))
    return body


def publish(title: str, content: str) -> str:
    imported = post("openapi/wiki/v1/import_doc", {"title": title, "content": content})
    doc_id = imported["data"]["doc_id"]
    time.sleep(1)
    try:
        post(
            "openapi/wiki/v1/add_knowledge",
            {
                "media_type": 11,
                "note_info": {"content_id": doc_id},
                "title": title,
                "knowledge_base_id": KNOWLEDGE_BASE_ID,
            },
        )
    except RuntimeError as error:
        message = str(error)
        if "重复" not in message and "duplicate" not in message.lower():
            raise
    return doc_id


def main() -> None:
    docs = [
        (
            "Week8-Day1｜LangChat：谁在调用能力平台？",
            (ROOT / "第8周/Week8-Day1-LangChat-用户意图.md").read_text(encoding="utf-8"),
        ),
        (
            "AI产品学习计划｜Week8-13：LangChat到Vision Intelligence",
            (ROOT / "Week8-13-AI-Product-Learning-Plan.md").read_text(encoding="utf-8"),
        ),
    ]
    results = {}
    for title, content in docs:
        if len(content.encode("utf-8")) < 3000:
            raise ValueError(f"IMA content unexpectedly short: {title}")
        results[title] = publish(title, content)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"IMA publish failed: {error}", file=sys.stderr)
        raise
