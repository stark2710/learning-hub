import os
import re


class DomainStore:

    @staticmethod
    def parse_index(path: str) -> list:
        """Parse domains.md → [{id, name, color, first_lesson_generated}]."""
        if not os.path.exists(path):
            return []
        with open(path) as f:
            text = f.read()
        domains = []
        for block in re.split(r"(?m)^---\n", text):
            block = block.strip()
            if not block:
                continue
            meta = {}
            for line in block.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
            if "id" in meta:
                domains.append({
                    "id": meta["id"],
                    "name": meta.get("name", meta["id"]),
                    "color": meta.get("color", "#7c3aed"),
                    "first_lesson_generated": meta.get("first_lesson_generated", "").lower() == "true",
                })
        return domains

    @staticmethod
    def parse_domain(path: str) -> list:
        """Parse {domain}.md → [{num, name, lessons:[{l, title, key}]}]."""
        if not os.path.exists(path):
            return []
        with open(path) as f:
            text = f.read()
        modules = []
        blocks = re.split(r"(?m)^---\n", text)
        i = 0
        while i < len(blocks):
            meta_block = blocks[i].strip()
            if not meta_block:
                i += 1
                continue
            meta = {}
            for line in meta_block.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
            if "module" not in meta:
                i += 1
                continue
            lessons_block = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
            i += 2
            lessons = []
            for line in lessons_block.splitlines():
                line = line.strip()
                if not line.startswith("- "):
                    continue
                parts = [p.strip() for p in line[2:].split("|")]
                if len(parts) >= 3:
                    l_num = int(re.sub(r"[^0-9]", "", parts[0]) or "0")
                    lessons.append({"l": l_num, "title": parts[1], "key": parts[2]})
            modules.append({
                "num": int(meta["module"]),
                "name": meta.get("name", f"Module {meta['module']}"),
                "lessons": lessons,
            })
        return modules

    @staticmethod
    def write_domain(path: str, modules: list) -> None:
        lines = []
        for mod in modules:
            lines.append(f"---\nmodule: {mod['num']}\nname: {mod['name']}\n---")
            for lesson in mod.get("lessons", []):
                title = lesson.get("name") or lesson.get("title", "")
                key = lesson.get("key") or lesson.get("slug", "")
                lines.append(f"- l{lesson['l']} | {title} | {key}")
            lines.append("")
        with open(path, "w") as f:
            f.write("\n".join(lines).strip() + "\n")

    @staticmethod
    def append_module(path: str, mod: dict) -> None:
        lines = [f"\n---\nmodule: {mod['num']}\nname: {mod['name']}\n---"]
        for lesson in mod.get("lessons", []):
            title = lesson.get("name") or lesson.get("title", "")
            key = lesson.get("key") or lesson.get("slug", "")
            lines.append(f"- l{lesson['l']} | {title} | {key}")
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n")

    @staticmethod
    def append_lesson(path: str, mod_num: int, lesson: dict) -> None:
        title = lesson.get("name") or lesson.get("title", "")
        key = lesson.get("key") or lesson.get("slug", "")
        new_line = f"- l{lesson['l']} | {title} | {key}\n"
        DomainStore._insert_lesson_line(path, mod_num, new_line)

    @staticmethod
    def _insert_lesson_line(path: str, mod_num: int, new_line: str) -> None:
        with open(path) as f:
            lines = f.readlines()
        in_target = False
        last_lesson_idx = -1
        for idx, line in enumerate(lines):
            if line.strip() == f"module: {mod_num}":
                in_target = True
            elif in_target and line.startswith("- l"):
                last_lesson_idx = idx
            elif in_target and line.strip() == "---":
                break
        if last_lesson_idx >= 0:
            lines.insert(last_lesson_idx + 1, new_line)
        else:
            lines.append(new_line)
        with open(path, "w") as f:
            f.writelines(lines)

    @staticmethod
    def set_first_lesson_generated(path: str, domain_id: str) -> None:
        with open(path) as f:
            lines = f.readlines()
        in_target = False
        flag_set = False
        insert_before = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "---":
                if in_target:
                    insert_before = i
                    break
                in_target = False
            elif in_target and stripped.startswith("first_lesson_generated:"):
                lines[i] = "first_lesson_generated: true\n"
                flag_set = True
                break
            elif stripped.startswith("id:") and stripped.split(":", 1)[1].strip() == domain_id:
                in_target = True
        if not flag_set:
            if insert_before >= 0:
                lines.insert(insert_before, "first_lesson_generated: true\n")
            else:
                lines.append("first_lesson_generated: true\n")
        with open(path, "w") as f:
            f.writelines(lines)
