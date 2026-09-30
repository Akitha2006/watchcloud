from backend.utils import load_json_file
from backend.config import KNOWLEDGE_BASE_FILE

class RAGService:
    def __init__(self):
        self.knowledge_base = load_json_file(KNOWLEDGE_BASE_FILE, [])

    def reload_kb(self):
        self.knowledge_base = load_json_file(KNOWLEDGE_BASE_FILE, [])

    def retrieve_similar_incidents(self, incident_type: str) -> list:
        self.reload_kb()
        matches = [
            item for item in self.knowledge_base
            if item.get("incident_type", "").upper() == incident_type.upper()
        ]
        if not matches:
            return self.knowledge_base[:1]
        return matches

rag_service = RAGService()
