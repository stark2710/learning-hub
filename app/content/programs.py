import os
import re


class ProgramStore:
    @staticmethod
    def parse(base: str) -> list:
        path = os.path.join(base, "programs.md")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            text = f.read()
        programs = []
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
            if "name" not in meta:
                i += 1
                continue
            description = ""
            if i + 1 < len(blocks):
                description = blocks[i + 1].strip()
                i += 2
            else:
                i += 1
            name = meta["name"]
            program_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            programs.append({
                "id": program_id,
                "name": name,
                "icon": meta.get("icon", "🎯"),
                "color": meta.get("color", "#7c3aed"),
                "url": meta.get("url", f"/program.html?id={program_id}"),
                "status": meta.get("status", "active"),
                "description": description,
                "total_lessons": int(meta.get("total_lessons", 0)),
            })
        return programs

    @staticmethod
    def append(base: str, name: str, icon: str, color: str, program_id: str,
               description: str = "", total_lessons: int = 0) -> None:
        path = os.path.join(base, "programs.md")
        block = (
            f"\n---\nname: {name}\nicon: {icon}\ncolor: {color}\n"
            f"url: /program.html?id={program_id}\nstatus: active\n"
            f"total_lessons: {total_lessons}\n---\n{description}\n"
        )
        with open(path, "a") as f:
            f.write(block)
