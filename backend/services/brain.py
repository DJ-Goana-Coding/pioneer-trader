from backend.core.personas import PERSONA_REGISTRY, detect_persona
from backend.services.vortex import VortexEngine
from backend.services.knowledge import knowledge_base
class SkinWalkerBrain:
    def __init__(self):
        self.persona = PERSONA_REGISTRY["TIA"]
        self.vortex = VortexEngine()
    async def process(self, text: str):
        new_p = detect_persona(text)
        if new_p: self.persona = new_p
        if "learn" in text.lower():
            knowledge_base.save_fact(text)
            return {"msg": f"[{self.persona.name}] Learned.", "persona": self.persona.name}
        return {"msg": f"[{self.persona.name}] {text}", "persona": self.persona.name}
brain = SkinWalkerBrain()
