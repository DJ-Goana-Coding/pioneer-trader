from typing import List, Optional
from pydantic import BaseModel

class Persona(BaseModel):
    id: str; name: str; role: str; style: str; triggers: List[str]

PERSONA_REGISTRY = {
    "TIA": Persona(id="TIA", name="T.I.A.", role="Captain", style="green", triggers=["status", "report", "tia", "system"]),
    "GOANNA": Persona(id="GOANNA", name="DJ Goanna", role="DJ", style="purple", triggers=["bass", "vibe", "play"]),
    "VOID": Persona(id="VOID", name="The Void", role="Oracle", style="red", triggers=["truth", "dark", "prediction"]),
    "HIPPY": Persona(id="HIPPY", name="Hippy", role="Guide", style="blue", triggers=["peace", "chill", "love"])
}
def detect_persona(text: str) -> Optional[Persona]:
    for _, p in PERSONA_REGISTRY.items():
        if any(t in text.lower() for t in p.triggers): return p
    return None
