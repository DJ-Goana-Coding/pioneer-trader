import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("encyclopedia/knowledge_base.json")

class KnowledgeBase:
    def __init__(self):
        if not DB_PATH.exists():
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            DB_PATH.write_text(json.dumps({"facts": []}), encoding="utf-8")

    def save_fact(self, content: str):
        data = json.loads(DB_PATH.read_text())
        data["facts"].append({"content": content, "ts": datetime.utcnow().isoformat()})
        DB_PATH.write_text(json.dumps(data, indent=2))
        return True

knowledge_base = KnowledgeBase()