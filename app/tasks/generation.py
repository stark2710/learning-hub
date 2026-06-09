import json
import os
import re
import traceback

from app.config import PORT, BASE_DIR
from app.jobs import JobRegistry
from app.ai.client import AIClient
from app.ai.claude import ClaudeClient
from app.content.programs import ProgramStore
from app.content.domains import DomainStore


def strip_lesson_content(text: str) -> str:
    """Return clean lesson markdown: real frontmatter through end of lesson.

    Tolerates models that prepend a stray '---' / blank lines and wrap the whole
    lesson in a ```markdown ... ``` fence, then append trailing commentary
    (e.g. "## What to do next"). Drops everything outside the wrapper, then
    anchors on the real frontmatter.
    """
    lines = text.strip().splitlines()

    # 1) Detect an outer ```markdown / ```md / ``` wrapper, even when preceded by
    #    a stray '---' or blank lines. Only blank/'---' lines may precede it.
    open_idx = None
    for i, ln in enumerate(lines):
        sl = ln.strip()
        if sl.startswith("```"):
            if sl[3:].strip().lower() in ("", "markdown", "md"):
                open_idx = i
            break
        if sl and sl != "---":
            break  # real content begins — there is no outer wrapper
    if open_idx is not None:
        # Markdown fences don't nest, so depth-counting is unreliable. The
        # wrapper's close is an *unindented* bare ``` (the lesson's own fences
        # close the same way, but the model's trailing commentary fences are
        # indented inside list items). Cut from the last unindented ``` to EOF —
        # this drops the wrapper close plus any trailing commentary.
        close_idx = next((j for j in range(len(lines) - 1, open_idx, -1)
                          if lines[j] == "```"), None)
        lines = lines[open_idx + 1:close_idx] if close_idx is not None else lines[open_idx + 1:]

    # 2) Anchor on the real frontmatter: the first '---' whose next non-empty line
    #    is a 'key:' line. Fall back to the first '---', then the raw text.
    def _is_key(s):
        return bool(re.match(r"[A-Za-z_][\w-]*\s*:", s))
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            k = i + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            if k < len(lines) and _is_key(lines[k].strip()):
                return "\n".join(lines[i:]).strip()
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            return "\n".join(lines[i:]).strip()
    return "\n".join(lines).strip()


def generate_lesson_file(lesson_file_id: str, program_id: str, mod: dict, lesson: dict,
                          curriculum: dict, api_key: str, base: str,
                          provider: str = "claude", ollama_model: str = "",
                          claude_model: str = "") -> None:
    """Write a single lesson markdown file for a custom program."""
    cmd_path = os.path.join(base, ".claude", "commands", "new-lesson.md")
    with open(cmd_path) as f:
        lesson_format = f.read()

    content_dir = os.path.join(base, "content")
    existing = sorted(f for f in os.listdir(content_dir)
                      if f.startswith(f"{program_id}-") and f.endswith(".md"))
    prior_content = ""
    for fn in existing[-2:]:
        with open(os.path.join(content_dir, fn)) as f:
            prior_content += f"\n\n--- {fn} ---\n" + f.read(2000)

    user_msg = (
        f"Program: {curriculum['name']}\n"
        f"Curriculum overview:\n{json.dumps(curriculum, indent=2)}\n\n"
        f"Generate Module {mod['num']} ({mod['name']}), "
        f"Lesson {lesson['l']}: {lesson.get('name') or lesson.get('title', '')}\n"
        f"lesson_id must be exactly: {lesson_file_id}\n\n"
        f"Prior lessons in this program (for continuity):\n"
        f"{prior_content or '(first lesson in this program)'}\n\n"
        "Write a COMPREHENSIVE, detailed lesson. Include:\n"
        "- Multiple concept sections with in-depth explanations\n"
        "- Real-world examples and production context\n"
        "- At least 3-4 code examples with annotations\n"
        "- Practice exercises and quiz questions\n"
        "The lesson must be thorough — aim for 1500+ words of content.\n\n"
        "Start immediately with --- frontmatter."
    )

    markdown = strip_lesson_content(
        AIClient.complete(provider, api_key, ollama_model,
                          [{"role": "user", "content": user_msg}], lesson_format,
                          max_tokens=8192, claude_model=claude_model)
    )

    with open(os.path.join(content_dir, f"{lesson_file_id}.md"), "w") as f:
        f.write(markdown)


def run_generate_lesson(job_id: str, api_key: str, base: str,
                        provider: str = "claude", ollama_model: str = "",
                        claude_model: str = "") -> None:
    """Background task: generate next lesson from progress.json."""
    try:
        cmd_path = os.path.join(base, ".claude", "commands", "new-lesson.md")
        with open(cmd_path) as f:
            system_prompt = f.read()

        progress_path = os.path.join(base, "progress.json")
        with open(progress_path) as f:
            progress = json.load(f)

        cur_mod = progress.get("current_module", 1)
        cur_les = progress.get("current_lesson", 1)
        total = progress.get("modules", {}).get(str(cur_mod), {}).get("total_lessons", 0)
        next_mod, next_les = (cur_mod, cur_les + 1) if cur_les < total else (cur_mod + 1, 1)

        content_dir = os.path.join(base, "content")
        existing = [f for f in os.listdir(content_dir)
                    if re.match(rf"m{next_mod}-l{next_les}-", f)]
        if existing:
            slug = existing[0].replace(".md", "")
            JobRegistry.set(job_id, {
                "status": "done",
                "url": f"http://localhost:{PORT}/modules/lesson.html?c={slug}",
                "lesson_id": slug,
                "existed": True,
            })
            return

        content_files = sorted(f for f in os.listdir(content_dir) if f.endswith(".md"))
        prior_content = ""
        for fn in content_files[-3:]:
            with open(os.path.join(content_dir, fn)) as f:
                prior_content += f"\n\n--- {fn} ---\n" + f.read()

        qlog_path = os.path.join(base, "questions_log.json")
        questions_log = []
        if os.path.exists(qlog_path):
            with open(qlog_path) as f:
                questions_log = json.load(f)

        user_msg = (
            f"Current progress.json:\n{json.dumps(progress, indent=2)}\n\n"
            f"questions_log.json (last 10 entries):\n{json.dumps(questions_log[-10:], indent=2)}\n\n"
            f"Prior lesson content (skim for context — avoid repeating examples):\n{prior_content}\n\n"
            f"Generate the next lesson (m{next_mod}-l{next_les}) now. "
            "Write a COMPREHENSIVE, detailed lesson with multiple concept sections, "
            "real-world examples, at least 3-4 code examples, and practice exercises. "
            "Aim for 1500+ words of content. Follow the markdown format exactly as specified."
        )

        markdown = strip_lesson_content(
            AIClient.complete(provider, api_key, ollama_model,
                              [{"role": "user", "content": user_msg}], system_prompt,
                              max_tokens=8192, claude_model=claude_model)
        )

        lesson_id = None
        for line in markdown.splitlines():
            if line.startswith("lesson_id:"):
                lesson_id = line.split(":", 1)[1].strip().strip('"').strip("'")
                break

        if not lesson_id:
            JobRegistry.set(job_id, {"status": "error", "error": "Could not parse lesson_id"})
            return

        with open(os.path.join(content_dir, f"{lesson_id}.md"), "w") as f:
            f.write(markdown)

        m = re.match(r"m(\d+)-l(\d+)", lesson_id)
        if m:
            progress["current_module"] = int(m.group(1))
            progress["current_lesson"] = int(m.group(2))

        progress.setdefault("completed_lessons", {})[lesson_id] = {
            "file": "modules/lesson.html",
            "md": f"content/{lesson_id}.md",
            "completed": False,
        }

        with open(progress_path, "w") as f:
            json.dump(progress, f, indent=2)

        JobRegistry.set(job_id, {
            "status": "done",
            "url": f"http://localhost:{PORT}/modules/lesson.html?c={lesson_id}",
            "lesson_id": lesson_id,
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n[GENERATION ERROR] job={job_id}\n{tb}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e), "traceback": tb})


def run_generate_first_domain_lesson(job_id: str, program_id: str, domain_id: str,
                                     api_key: str, base: str,
                                     provider: str = "claude", ollama_model: str = "",
                                     claude_model: str = "") -> None:
    """Background task: generate content for the first lesson of a domain."""
    try:
        JobRegistry.set(job_id, {"status": "running"})
        prog_dir = os.path.join(base, "content", program_id)
        modules = DomainStore.parse_domain(os.path.join(prog_dir, f"{domain_id}.md"))
        if not modules or not modules[0]["lessons"]:
            JobRegistry.set(job_id, {"status": "error", "error": "No lessons found in domain"})
            return

        mod = modules[0]
        lesson = mod["lessons"][0]
        lesson_file_id = lesson["key"]

        content_dir = os.path.join(base, "content")
        if os.path.exists(os.path.join(content_dir, f"{lesson_file_id}.md")):
            JobRegistry.set(job_id, {"status": "done", "lesson_id": lesson_file_id, "existed": True})
            return

        programs = ProgramStore.parse(base)
        program = next((p for p in programs if p["id"] == program_id), {"name": program_id})
        domains = DomainStore.parse_index(os.path.join(prog_dir, "domains.md"))
        domain_meta = next((d for d in domains if d["id"] == domain_id), {"name": domain_id})
        fake_curriculum = {"name": program["name"], "domain": domain_meta["name"], "modules": modules}

        generate_lesson_file(lesson_file_id, program_id, mod, lesson, fake_curriculum,
                             api_key, base, provider, ollama_model, claude_model)
        DomainStore.set_first_lesson_generated(os.path.join(prog_dir, "domains.md"), domain_id)

        JobRegistry.set(job_id, {"status": "done", "lesson_id": lesson_file_id})
    except Exception as e:
        print(f"\n[GEN FIRST LESSON ERROR] {traceback.format_exc()}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e)})


def run_generate_next_domain_lesson(job_id: str, program_id: str, domain_id: str,
                                    current_lesson_key: str, api_key: str, base: str,
                                    provider: str = "claude", ollama_model: str = "",
                                    claude_model: str = "") -> None:
    """Background task: generate the next lesson after current_lesson_key in a domain."""
    try:
        JobRegistry.set(job_id, {"status": "running"})
        prog_dir = os.path.join(base, "content", program_id)
        modules = DomainStore.parse_domain(os.path.join(prog_dir, f"{domain_id}.md"))

        if not modules:
            JobRegistry.set(job_id, {"status": "error", "error": "No modules found in domain"})
            return

        # Flatten all lessons in order
        all_lessons = [(mod, lesson) for mod in modules for lesson in mod["lessons"]]

        current_idx = next(
            (i for i, (_, les) in enumerate(all_lessons) if les["key"] == current_lesson_key),
            None,
        )

        if current_idx is None:
            JobRegistry.set(job_id, {"status": "error",
                                     "error": f"Current lesson not found in domain: {current_lesson_key}"})
            return

        if current_idx + 1 >= len(all_lessons):
            JobRegistry.set(job_id, {"status": "error", "error": "No more lessons in this domain"})
            return

        next_mod, next_lesson = all_lessons[current_idx + 1]
        lesson_file_id = next_lesson["key"]

        content_dir = os.path.join(base, "content")
        if os.path.exists(os.path.join(content_dir, f"{lesson_file_id}.md")):
            JobRegistry.set(job_id, {
                "status": "done",
                "lesson_id": lesson_file_id,
                "url": f"http://localhost:{PORT}/modules/lesson.html?c={lesson_file_id}&p={program_id}",
                "existed": True,
            })
            return

        programs = ProgramStore.parse(base)
        program = next((p for p in programs if p["id"] == program_id), {"name": program_id})
        domains = DomainStore.parse_index(os.path.join(prog_dir, "domains.md"))
        domain_meta = next((d for d in domains if d["id"] == domain_id), {"name": domain_id})
        fake_curriculum = {"name": program["name"], "domain": domain_meta["name"], "modules": modules}

        generate_lesson_file(lesson_file_id, program_id, next_mod, next_lesson, fake_curriculum,
                             api_key, base, provider, ollama_model, claude_model)

        JobRegistry.set(job_id, {
            "status": "done",
            "lesson_id": lesson_file_id,
            "url": f"http://localhost:{PORT}/modules/lesson.html?c={lesson_file_id}&p={program_id}",
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(f"\n[GEN NEXT DOMAIN LESSON ERROR] {tb}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e), "traceback": tb})
