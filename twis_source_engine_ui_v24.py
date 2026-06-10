#!/usr/bin/env python3
"""
Local Streamlit interface for the TWIS / Story Evidence Collector pipeline.

This is a local control panel only. It does not run a live Nutch crawl,
bypass robots.txt, deploy publicly, or change the evidence logic.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st


ROOT = Path(__file__).resolve().parent

KNOWN_INPUTS = [
    "seed_urls.json",
    "subject_query.json",
    "config/source_worlds.example.json",
    "testdata/nutch_discovery_sample_v23.json",
    "candidate_sources_discovered_v23.json",
]

KNOWN_OUTPUTS = [
    "candidate_sources_discovered_v23.json",
    "candidate_sources_discovered_v23.md",
    "subject_matches_v21.json",
    "subject_matches_v21.md",
]

SAFE_SCRIPTS = {
    "Run v2.3 Nutch output converter": "convert_nutch_output_v23.py",
    "Run v2.1 subject matcher": "extract_subject_matches_v21.py",
}


def repo_path(relative_path: str) -> Path:
    """Resolve a repo-relative path without allowing traversal outside the repo."""
    clean = relative_path.strip().replace("\\", "/")
    path = (ROOT / clean).resolve()

    if ROOT != path and ROOT not in path.parents:
        raise ValueError("Path is outside the repository")

    return path


def path_exists(relative_path: str) -> bool:
    try:
        return repo_path(relative_path).exists()
    except ValueError:
        return False


def read_text(relative_path: str) -> str:
    return repo_path(relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> Any:
    with repo_path(relative_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def count_json_items(data: Any) -> int | None:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ("records", "candidates", "documents", "urls", "items", "seed_urls", "source_worlds"):
            value = data.get(key)
            if isinstance(value, list):
                return len(value)
    return None


def run_safe_script(script_name: str, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    script_path = repo_path(script_name)
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_name}")

    command = [sys.executable, str(script_path)]
    if extra_args:
        command.extend(extra_args)

    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def status_badge(relative_path: str) -> None:
    if path_exists(relative_path):
        st.success(f"Exists: `{relative_path}`")
    else:
        st.warning(f"Missing: `{relative_path}`")


def show_json_preview(relative_path: str) -> None:
    try:
        data = load_json(relative_path)
    except Exception as error:  # noqa: BLE001 - user-facing local preview
        st.error(f"Could not read JSON: {error}")
        return

    item_count = count_json_items(data)
    if item_count is not None:
        st.caption(f"Detected item count: {item_count}")

    st.json(data, expanded=False)


def show_markdown_preview(relative_path: str) -> None:
    try:
        content = read_text(relative_path)
    except Exception as error:  # noqa: BLE001 - user-facing local preview
        st.error(f"Could not read Markdown: {error}")
        return

    st.markdown(content)


def main() -> None:
    st.set_page_config(
        page_title="TWIS Source Engine",
        layout="wide",
    )

    st.title("TWIS Source Engine")
    st.caption("Local control panel. Safe scripts only. No live Nutch crawl exposed in v2.4.")

    with st.sidebar:
        st.header("Mode")
        mode = st.radio(
            "Choose mode",
            options=["targeted", "discovery", "hybrid"],
            index=1,
            help="Modes are labels in v2.4. Only available local scripts can be run.",
        )

        st.header("Safety lock")
        st.write("No live crawl")
        st.write("No public fetch from this UI")
        st.write("No anti-bot behaviour")
        st.write("Local use only")

    st.subheader("1. Load inputs")

    input_choice = st.selectbox(
        "Known input files",
        options=KNOWN_INPUTS,
        index=KNOWN_INPUTS.index("testdata/nutch_discovery_sample_v23.json"),
    )

    custom_input = st.text_input(
        "Or enter repo-relative input path",
        value=input_choice,
    )

    col_a, col_b = st.columns([1, 2])
    with col_a:
        status_badge(custom_input)
    with col_b:
        if path_exists(custom_input):
            suffix = repo_path(custom_input).suffix.lower()
            if suffix == ".json":
                show_json_preview(custom_input)
            elif suffix in {".md", ".markdown"}:
                show_markdown_preview(custom_input)
            else:
                st.code(read_text(custom_input)[:4000])

    st.subheader("2. Selected mode")
    st.info(f"Current mode: `{mode}`")

    if mode == "targeted":
        st.write("Use this for known URLs and existing evidence-collector records.")
    elif mode == "discovery":
        st.write("Use this for Nutch-style candidate discovery outputs.")
    else:
        st.write("Use this later for discovery candidates passed into the evidence pipeline.")

    st.subheader("3. Run safe step")

    st.warning("v2.4 does not run a live Nutch crawl. It can only run known local scripts.")

    selected_action = st.selectbox("Safe script", options=list(SAFE_SCRIPTS.keys()))
    selected_script = SAFE_SCRIPTS[selected_action]
    status_badge(selected_script)

    converter_input = st.text_input(
        "v2.3 converter input path",
        value="testdata/nutch_discovery_sample_v23.json",
        disabled=selected_script != "convert_nutch_output_v23.py",
    )

    if st.button("Run selected safe script", type="primary"):
        if selected_script == "convert_nutch_output_v23.py":
            args = ["--input", converter_input]
        else:
            args = []

        try:
            result = run_safe_script(selected_script, args)
        except Exception as error:  # noqa: BLE001 - user-facing local runner
            st.error(str(error))
        else:
            if result.returncode == 0:
                st.success("Script finished successfully.")
            else:
                st.error(f"Script exited with code {result.returncode}.")

            if result.stdout:
                st.code(result.stdout, language="text")
            if result.stderr:
                st.code(result.stderr, language="text")

    st.subheader("4. View outputs")

    output_choice = st.selectbox("Output file", options=KNOWN_OUTPUTS)
    status_badge(output_choice)

    if path_exists(output_choice):
        if output_choice.endswith(".json"):
            show_json_preview(output_choice)
        elif output_choice.endswith(".md"):
            show_markdown_preview(output_choice)
        else:
            st.code(read_text(output_choice)[:8000], language="text")

    st.subheader("Current file checklist")
    checklist_rows = []
    for relative_path in [*KNOWN_INPUTS, *KNOWN_OUTPUTS, *SAFE_SCRIPTS.values()]:
        checklist_rows.append({
            "file": relative_path,
            "exists": path_exists(relative_path),
        })
    st.dataframe(checklist_rows, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
