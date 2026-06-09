import os
import re

from app.config import BASE_DIR
from app.content.programs import ProgramStore
from app.content.domains import DomainStore


class ProgramHandlersMixin:

    def _list_programs(self):
        try:
            self._json_ok(ProgramStore.parse(BASE_DIR))
        except Exception as e:
            self._error(500, str(e))

    def _get_program(self):
        try:
            program_id = self.path.split("/program/", 1)[1].split("?")[0]
            programs = ProgramStore.parse(BASE_DIR)
            program = next((p for p in programs if p["id"] == program_id), None)
            if not program:
                self._error(404, f"Program {program_id!r} not found")
                return

            prog_dir = os.path.join(BASE_DIR, "content", program_id)
            domains = DomainStore.parse_index(os.path.join(prog_dir, "domains.md"))
            content_dir = os.path.join(BASE_DIR, "content")

            for domain in domains:
                domain["modules"] = DomainStore.parse_domain(
                    os.path.join(prog_dir, f"{domain['id']}.md")
                )
                domain["first_lesson_has_content"] = domain.pop("first_lesson_generated", False)
                for mod in domain["modules"]:
                    for lesson in mod["lessons"]:
                        lesson["has_content"] = os.path.exists(
                            os.path.join(content_dir, f"{lesson['key']}.md")
                        )

            result = dict(program)
            result["domains"] = domains
            self._json_ok(result)
        except Exception as e:
            import traceback; traceback.print_exc()
            self._error(500, str(e))

    def _create_program(self):
        try:
            body = self._read_body()
            name = body.get("name", "").strip()
            icon = body.get("icon", "🎯")
            color = body.get("color", "#7c3aed")
            if not name:
                self._error(400, "name required")
                return

            program_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            programs = ProgramStore.parse(BASE_DIR)
            orig_id, i = program_id, 2
            while any(p["id"] == program_id for p in programs):
                program_id = f"{orig_id}-{i}"
                i += 1

            description = f"Your {name} learning program"
            ProgramStore.append(BASE_DIR, name, icon, color, program_id, description)
            self._json_ok({
                "ok": True,
                "program": {
                    "id": program_id, "name": name, "description": description,
                    "icon": icon, "color": color,
                    "url": f"/program.html?id={program_id}", "total_lessons": 0,
                },
            })
        except Exception as e:
            self._error(500, str(e))
