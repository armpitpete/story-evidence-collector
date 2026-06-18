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
    "../thisweekinsmoke/src/pages/sources/index.astro",
    "testdata/nutch_discovery_sample_v23.json",
    "candidate_sources_discovered_v23.json",
    "website_source_candidates_v25.json",
    "seed_urls_from_website_candidates_v26.json",
]

KNOWN_OUTPUTS = [
    "candidate_sources_discovered_v23.json",
    "candidate_sources_discovered_v23.md",
    "website_source_candidates_v25.json",
    "website_source_candidates_v25.md",
    "seed_urls_from_website_candidates_v26.json",
    "seed_urls_from_website_candidates_v26.md",
    "sources_raw_v27.json",
    "link_queue_v27.json",
    "source_report_v27.json",
    "subject_matches_v21.json",
    "subject_matches_v21.md",
]

SAFE_SCRIPTS = {
    "Run v2.3 Nutch output converter": "convert_nutch_output_v23.py",
    "Run v2.5 TWIS website source extractor": "extract_twis_website_sources_v25.py",
    "Run v2.6 seed URL builder from website candidates": "build_seed_urls_from_candidates_v26.py",
    "Run v2.7 targeted source fetch from seed file": "extract_source_records_from_seed_file_v27.py",
    "Run v2.1 subject matcher": "extract_subject_matches_v21.py",
}

SIMPLE_SOURCE_INPUT = "../thisweekinsmoke/src/pages/sources/index.astro"
SIMPLE_CANDIDATE_INPUT = "website_source_candidates_v25.json"
SIMPLE_SEED_INPUT = "seed_urls_from_website_candidates_v26.json"

SIMPLE_PIPELINE_STEPS = [
    {
        "label": "Find sources from TWIS",
        "script": "extract_twis_website_sources_v25.py",
        "args": ["--input", SIMPLE_SOURCE_INPUT],
        "inputs": [SIMPLE_SOURCE_INPUT],
        "outputs": ["website_source_candidates_v25.json", "website_source_candidates_v25.md"],
    },
    {
        "label": "Make the website check list",
        "script": "build_seed_urls_from_candidates_v26.py",
        "args": ["--input", SIMPLE_CANDIDATE_INPUT, "--roles", "url"],
        "inputs": [SIMPLE_CANDIDATE_INPUT],
        "outputs": ["seed_urls_from_website_candidates_v26.json", "seed_urls_from_website_candidates_v26.md"],
    },
    {
        "label": "Check five pages safely",
        "script": "extract_source_records_from_seed_file_v27.py",
        "args": ["--input", SIMPLE_SEED_INPUT, "--max-seeds", "5", "--delay-seconds", "1"],
        "inputs": [SIMPLE_SEED_INPUT],
        "outputs": ["sources_raw_v27.json", "link_queue_v27.json", "source_report_v27.json"],
    },
]

SIMPLE_OUTPUTS = [
    "source_report_v27.json",
    "sources_raw_v27.json",
    "link_queue_v27.json",
    "seed_urls_from_website_candidates_v26.md",
    "website_source_candidates_v25.md",
]


def repo_path(relative_path: str) -> Path:
    """Resolve a local path while allowing the sibling TWIS repo source file."""
    clean = relative_path.strip().replace("\\", "/")
    path = (ROOT / clean).resolve()

    allowed_extra = (ROOT.parent / "thisweekinsmoke" / "src" / "pages" / "sources" / "index.astro").resolve()

    if path == allowed_extra:
        return path

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


def safe_count(relative_path: str) -> int | None:
    if not path_exists(relative_path):
        return None
    try:
        return count_json_items(load_json(relative_path))
    except Exception:  # noqa: BLE001 - best-effort status only
        return None


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


def file_rows(paths: list[str]) -> list[dict[str, Any]]:
    return [{"file": path, "exists": path_exists(path)} for path in paths]


def missing_pipeline_files() -> list[str]:
    missing: list[str] = []
    for step in SIMPLE_PIPELINE_STEPS:
        if not path_exists(step["script"]):
            missing.append(step["script"])
    if not path_exists(SIMPLE_SOURCE_INPUT):
        missing.append(SIMPLE_SOURCE_INPUT)
    return missing


def render_run_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode == 0:
        st.success("Done. This part worked.")
    else:
        st.error(f"This part stopped with code {result.returncode}.")

    if result.stdout:
        st.code(result.stdout, language="text")
    if result.stderr:
        st.code(result.stderr, language="text")


def run_and_show(script_name: str, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        result = run_safe_script(script_name, args)
    except Exception as error:  # noqa: BLE001 - user-facing local runner
        st.error(str(error))
        return None

    render_run_result(result)
    return result


def render_simple_status_board() -> None:
    st.subheader("What I found")
    st.write("When this page opens, it checks the files already on this computer. It does not open websites by itself.")

    candidate_count = safe_count("website_source_candidates_v25.json")
    seed_count = safe_count("seed_urls_from_website_candidates_v26.json")
    fetched_count = safe_count("sources_raw_v27.json")
    queue_count = safe_count("link_queue_v27.json")

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("TWIS list", "Found" if path_exists(SIMPLE_SOURCE_INPUT) else "Missing")
    col_b.metric("Possible sources", str(candidate_count) if candidate_count is not None else "Missing")
    col_c.metric("Websites to check", str(seed_count) if seed_count is not None else "Missing")
    col_d.metric("Pages checked", str(fetched_count) if fetched_count is not None else "Missing")

    if queue_count is not None:
        st.caption(f"Links saved, not checked: {queue_count}. These are not opened automatically.")

    if path_exists("source_report_v27.json"):
        st.success("Review report is ready below.")
    else:
        st.info("No report yet. Press refresh when you want to run a safe web check.")


def render_simple_intro() -> None:
    st.subheader("What this means")
    st.write("This page helps TWIS check public source websites without asking you to understand the technical scripts.")

    st.markdown(
        """
| Plain name | Meaning |
|---|---|
| TWIS list | The page where TWIS lists source organisations. |
| Possible sources | Source organisations found on that page. |
| Websites to check | Main website addresses taken from the source list. |
| Pages checked | A small safe sample of public pages already checked. |
| Review report | A local file showing what worked and what failed. |
"""
    )


def render_pipeline_details() -> None:
    with st.expander("Show the hidden steps", expanded=False):
        st.markdown(
            """
| Order | Hidden step | Creates |
|---|---|---|
| 1 | Find sources from TWIS | Possible sources |
| 2 | Make the website check list | Websites to check |
| 3 | Check five pages safely | Review report and local page notes |
"""
        )
        st.warning("The web check follows robots.txt first. It does not open saved links.")

        all_files: list[str] = []
        for step in SIMPLE_PIPELINE_STEPS:
            all_files.extend([step["script"], *step["inputs"], *step["outputs"]])
        st.dataframe(file_rows(all_files), width="stretch", hide_index=True)


def render_simple_runner() -> None:
    st.subheader("Update the check")
    st.write("Press this only when you want to update the local review files.")

    missing = missing_pipeline_files()
    if missing:
        st.error("Refresh cannot run because a required file is missing.")
        with st.expander("Show missing files", expanded=True):
            for path in missing:
                st.write(f"- `{path}`")
        return

    st.success("Ready. Refresh will use the TWIS list, make the website check list, then check five safe pages.")

    if st.button("Refresh safe source check", type="primary", key="run-simple-pipeline"):
        for index, step in enumerate(SIMPLE_PIPELINE_STEPS, start=1):
            st.markdown(f"#### {index}. {step['label']}")
            result = run_and_show(step["script"], step["args"])
            if result is None or result.returncode != 0:
                st.error("Stopped here. Later parts were not run.")
                return
        st.success("Finished. Now read the review report below.")


def render_simple_review() -> None:
    st.subheader("Review report")
    st.write("This shows local files. Page-check files are for review, not automatic GitHub commits.")

    output_choice = st.selectbox(
        "Choose a report to view",
        options=SIMPLE_OUTPUTS,
        index=SIMPLE_OUTPUTS.index("source_report_v27.json"),
        key="simple-output-choice",
    )
    status_badge(output_choice)

    if path_exists(output_choice):
        if output_choice.endswith(".json"):
            show_json_preview(output_choice)
        elif output_choice.endswith(".md"):
            show_markdown_preview(output_choice)
        else:
            st.code(read_text(output_choice)[:8000], language="text")


def render_simple_mode() -> None:
    st.subheader("Simple mode")
    st.write("This page shows what it found first. Use refresh only when you want to update the check.")

    st.info("The page does not open websites when it loads. Websites are checked only when you press Refresh safe source check.")

    render_simple_status_board()
    render_simple_intro()
    render_simple_review()
    render_simple_runner()
    render_pipeline_details()


def render_advanced_mode() -> None:
    st.subheader("Advanced mode")
    st.warning("Advanced mode shows internal script names and paths. Use it only when you know which file you are changing.")

    with st.expander("Advanced controls", expanded=True):
        st.subheader("1. Load inputs")

        input_choice = st.selectbox(
            "Known input files",
            options=KNOWN_INPUTS,
            index=KNOWN_INPUTS.index("seed_urls_from_website_candidates_v26.json"),
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
        mode = st.radio(
            "Choose mode",
            options=["targeted", "discovery", "hybrid"],
            index=0,
            help="Modes are labels in v2.7. Only available local scripts can be run.",
        )
        st.info(f"Current mode: `{mode}`")

        if mode == "targeted":
            st.write("Use this for known URLs and selected seed files.")
        elif mode == "discovery":
            st.write("Use this for source discovery outputs, including Nutch-style candidates and TWIS website source-map candidates.")
        else:
            st.write("Use this later for discovery candidates passed into the evidence pipeline.")

        st.subheader("3. Run safe step")

        st.warning("Most steps are local-only. v2.7 fetches selected public seed URLs only after robots.txt checks.")

        selected_action = st.selectbox("Safe script", options=list(SAFE_SCRIPTS.keys()))
        selected_script = SAFE_SCRIPTS[selected_action]
        status_badge(selected_script)

        converter_input = st.text_input(
            "v2.3 converter input path",
            value="testdata/nutch_discovery_sample_v23.json",
            disabled=selected_script != "convert_nutch_output_v23.py",
        )

        website_sources_input = st.text_input(
            "v2.5 TWIS website sources input path",
            value="../thisweekinsmoke/src/pages/sources/index.astro",
            disabled=selected_script != "extract_twis_website_sources_v25.py",
        )

        seed_builder_input = st.text_input(
            "v2.6 website candidate input path",
            value="website_source_candidates_v25.json",
            disabled=selected_script != "build_seed_urls_from_candidates_v26.py",
        )

        seed_builder_roles = st.text_input(
            "v2.6 URL roles to include",
            value="url",
            disabled=selected_script != "build_seed_urls_from_candidates_v26.py",
            help="Default is url only. Optional: url,rssUrl,secondaryUrl",
        )

        source_fetch_input = st.text_input(
            "v2.7 seed URL input path",
            value="seed_urls_from_website_candidates_v26.json",
            disabled=selected_script != "extract_source_records_from_seed_file_v27.py",
        )

        source_fetch_max_seeds = st.number_input(
            "v2.7 max seeds to fetch",
            min_value=1,
            max_value=50,
            value=5,
            step=1,
            disabled=selected_script != "extract_source_records_from_seed_file_v27.py",
        )

        source_fetch_delay = st.number_input(
            "v2.7 delay seconds between seed fetches",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.5,
            disabled=selected_script != "extract_source_records_from_seed_file_v27.py",
        )

        if selected_script == "extract_source_records_from_seed_file_v27.py":
            st.error("This step fetches public pages. It checks robots.txt first and fetches seed URLs only. Queued links are not fetched.")

        if st.button("Run selected safe script", type="primary"):
            if selected_script == "convert_nutch_output_v23.py":
                args = ["--input", converter_input]
            elif selected_script == "extract_twis_website_sources_v25.py":
                args = ["--input", website_sources_input]
            elif selected_script == "build_seed_urls_from_candidates_v26.py":
                args = ["--input", seed_builder_input, "--roles", seed_builder_roles]
            elif selected_script == "extract_source_records_from_seed_file_v27.py":
                args = [
                    "--input", source_fetch_input,
                    "--max-seeds", str(source_fetch_max_seeds),
                    "--delay-seconds", str(source_fetch_delay),
                ]
            else:
                args = []

            run_and_show(selected_script, args)

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
    st.dataframe(checklist_rows, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="TWIS Source Engine",
        layout="wide",
    )

    st.title("TWIS Source Engine")
    st.caption("Local control panel. Safe scripts only. Simple mode is the normal path.")

    with st.sidebar:
        st.header("View")
        view = st.radio(
            "Choose view",
            options=["Simple", "Advanced"],
            index=0,
            help="Simple is the safe normal path. Advanced shows script names and paths.",
        )

        st.header("Safety lock")
        st.write("No live Nutch crawl")
        st.write("No queued-link fetch")
        st.write("No anti-bot behaviour")
        st.write("Local use only")

    if view == "Simple":
        render_simple_mode()
    else:
        render_advanced_mode()


if __name__ == "__main__":
    main()
