#!/usr/bin/env python3
"""Generate the Week 8 Day 1 LangChat mental-model notebook."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Week8-Day1-LangChat-用户意图.md"
OUTPUT = ROOT / "第8周-Day1-LangChat用户意图.ipynb"


def markdown_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code_cell(code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code.splitlines(keepends=True),
    }


def main() -> None:
    content = SOURCE.read_text(encoding="utf-8")
    sections = [section.strip() for section in content.split("\n## ") if section.strip()]
    cells = [markdown_cell(section if index == 0 else "## " + section) for index, section in enumerate(sections)]
    cells.append(
        code_cell(
            "from pathlib import Path\n"
            "\n"
            "references = [\n"
            "    Path('/root/langchat/apps/backend/langchat/skill_release/routes.py'),\n"
            "    Path('/root/langchat/apps/backend/langchat/server/auth/six_dim_middleware.py'),\n"
            "    Path('/root/langchat/apps/backend/langchat/skill_release/descriptor.py'),\n"
            "]\n"
            "for path in references:\n"
            "    print(f'{path.name}: {path.exists()}')\n"
        )
    )
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(cells)} cells")


if __name__ == "__main__":
    main()
