import json
import os
import re
import traceback

from app.jobs import JobRegistry
from app.ai.client import AIClient
from app.content.programs import ProgramStore
from app.content.domains import DomainStore
from app.tasks.generation import generate_lesson_file


def run_add_domain(job_id: str, program_id: str, prompt: str, api_key: str, base: str,
                   provider: str = "claude", ollama_model: str = "",
                   claude_model: str = "") -> None:
    """Background task: generate a full domain curriculum and write MD files."""
    try:
        JobRegistry.set(job_id, {"status": "running", "phase": "structuring"})

        programs = ProgramStore.parse(base)
        program = next((p for p in programs if p["id"] == program_id), {"name": program_id})

        system = (
            f'You are a curriculum architect adding a new subject domain to the "{program["name"]}" learning program.\n'
            "Output ONLY valid JSON — no explanation, no markdown fences.\n\n"
            "Format:\n"
            '{\n'
            '  "id": "lowercase-hyphenated-unique-id",\n'
            '  "name": "Domain Name",\n'
            '  "color": "#hexcolor",\n'
            '  "modules": [\n'
            '    {"num": 1, "name": "Module Name", "lessons": [\n'
            '      {"l": 1, "name": "Lesson Title", "slug": "kebab-case-slug"}\n'
            "    ]}\n"
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "- Create 4–6 modules covering the topic thoroughly from fundamentals to production.\n"
            "- Each module MUST have 5–8 lessons. Never fewer than 5 lessons per module.\n"
            "- Progress: fundamentals → core concepts → advanced → patterns → production/real-world.\n"
            "- Lessons should be granular and focused — one concept per lesson.\n"
            "Output ONLY the JSON object, nothing else."
        )
        text = AIClient.complete(provider, api_key, ollama_model,
                                 [{"role": "user", "content": prompt}],
                                 system, max_tokens=4096, claude_model=claude_model).strip()
        text = _unwrap_json(text)
        domain = json.loads(text)

        prog_dir = os.path.join(base, "content", program_id)
        os.makedirs(prog_dir, exist_ok=True)

        DomainStore.write_domain(os.path.join(prog_dir, f"{domain['id']}.md"), domain["modules"])

        with open(os.path.join(prog_dir, "domains.md"), "a") as f:
            f.write(f"\n---\nid: {domain['id']}\nname: {domain['name']}\ncolor: {domain['color']}\n---\n")

        JobRegistry.set(job_id, {"status": "done", "domain_id": domain["id"]})
    except Exception as e:
        print(f"\n[ADD DOMAIN ERROR] {traceback.format_exc()}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e)})


def run_add_module(job_id: str, program_id: str, domain_id: str, prompt: str, api_key: str,
                   base: str, provider: str = "claude", ollama_model: str = "",
                   claude_model: str = "") -> None:
    """Background task: generate a new module and append it to a domain."""
    try:
        JobRegistry.set(job_id, {"status": "running", "phase": "structuring"})

        prog_dir = os.path.join(base, "content", program_id)
        domain_md_path = os.path.join(prog_dir, f"{domain_id}.md")
        existing_modules = DomainStore.parse_domain(domain_md_path)

        domains = DomainStore.parse_index(os.path.join(prog_dir, "domains.md"))
        domain_meta = next((d for d in domains if d["id"] == domain_id), {"name": domain_id})
        programs = ProgramStore.parse(base)
        program = next((p for p in programs if p["id"] == program_id), {"name": program_id})

        next_num = max((m["num"] for m in existing_modules), default=0) + 1

        system = (
            f'You are a curriculum architect adding a module to the "{domain_meta["name"]}" domain in "{program["name"]}".\n'
            "Output ONLY valid JSON — no markdown, no explanation.\n\n"
            "Format:\n"
            '{"num": 1, "name": "Module Name", "lessons": [\n'
            '  {"l": 1, "name": "Lesson Title", "slug": "kebab-case-slug"}\n'
            "]}\n\n"
            f"Use num: {next_num}. Rules: 5–8 lessons, never fewer than 5. Output ONLY JSON."
        )
        text = AIClient.complete(provider, api_key, ollama_model,
                                 [{"role": "user", "content": prompt}],
                                 system, max_tokens=1024, claude_model=claude_model).strip()
        text = _unwrap_json(text)
        mod = json.loads(text)
        mod["num"] = next_num

        DomainStore.append_module(domain_md_path, mod)
        JobRegistry.set(job_id, {"status": "done", "domain_id": domain_id, "mod_num": next_num})
    except Exception as e:
        print(f"\n[ADD MODULE ERROR] {traceback.format_exc()}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e)})


def run_add_lesson(job_id: str, program_id: str, domain_id: str, mod_num: int, prompt: str,
                   api_key: str, base: str, provider: str = "claude", ollama_model: str = "",
                   claude_model: str = "") -> None:
    """Background task: generate a lesson, append to domain MD, write content file."""
    try:
        JobRegistry.set(job_id, {"status": "running"})

        prog_dir = os.path.join(base, "content", program_id)
        domain_md_path = os.path.join(prog_dir, f"{domain_id}.md")
        modules = DomainStore.parse_domain(domain_md_path)
        mod = next((m for m in modules if m["num"] == mod_num), None)
        if not mod:
            JobRegistry.set(job_id, {"status": "error", "error": f"Module {mod_num} not found"})
            return

        naming_system = 'Return ONLY valid JSON with no extra text: {"name": "Lesson Title", "slug": "kebab-case-slug"}'
        naming_text = AIClient.complete(
            provider, api_key, ollama_model,
            [{"role": "user", "content": f"Create a focused lesson about: {prompt}"}],
            naming_system, max_tokens=100, claude_model=claude_model
        ).strip()
        naming_text = _unwrap_json(naming_text)
        naming = json.loads(naming_text)

        lesson_slug = re.sub(r"[^a-z0-9]+", "-", naming["slug"].lower()).strip("-")
        next_l = max((l["l"] for l in mod["lessons"]), default=0) + 1
        new_lesson = {
            "l": next_l,
            "name": naming["name"],
            "slug": lesson_slug,
            "key": f"{program_id}-{domain_id}-m{mod_num}-l{next_l}-{lesson_slug}",
        }

        DomainStore.append_lesson(domain_md_path, mod_num, new_lesson)

        programs = ProgramStore.parse(base)
        program = next((p for p in programs if p["id"] == program_id), {"name": program_id})
        domains = DomainStore.parse_index(os.path.join(prog_dir, "domains.md"))
        domain_meta = next((d for d in domains if d["id"] == domain_id), {"name": domain_id})
        fake_curriculum = {"name": program["name"], "domain": domain_meta["name"], "modules": modules}

        generate_lesson_file(new_lesson["key"], program_id, mod, new_lesson, fake_curriculum,
                             api_key, base, provider, ollama_model, claude_model)

        JobRegistry.set(job_id, {"status": "done", "lesson_id": new_lesson["key"]})
    except Exception as e:
        print(f"\n[ADD LESSON ERROR] {traceback.format_exc()}", flush=True)
        JobRegistry.set(job_id, {"status": "error", "error": str(e)})


def _unwrap_json(text: str) -> str:
    """Strip markdown code fences and find the first JSON object."""
    if text.startswith("```"):
        lines = text.split("\n")
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "```"), len(lines))
        text = "\n".join(lines[1:end])
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    return text
