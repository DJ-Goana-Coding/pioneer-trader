from typing import List, Optional
from pydantic import BaseModel

class Persona(BaseModel):
    id: str
    name: str
    role: str
    style: str
    triggers: List[str]

PERSONA_REGISTRY = {
    "TIA": Persona(
        id="TIA", name="T.I.A. (The Captain)", role="Tactical Ops", style="green",
        triggers=["status", "report", "tia", "system", "update"]),
    "GOANNA": Persona(
        id="GOANNA", name="DJ Goanna", role="Frequency Master", style="purple",
        triggers=["bass", "vibe", "play", "music", "rave"]),
    "VOID": Persona(
        id="VOID", name="The Void", role="Oracle", style="red",
        triggers=["truth", "dark", "prediction", "hidden", "doom"]),
    "HIPPY": Persona(
        id="HIPPY", name="Hippy O'Neill", role="Guide", style="blue",
        triggers=["peace", "chill", "love", "learn", "nature"])
}

def detect_persona(text: str) -> Optional[Persona]:
    text = text.lower()
    for _, p in PERSONA_REGISTRY.items():
        if any(t in text for t in p.triggers):
            return p
    return None