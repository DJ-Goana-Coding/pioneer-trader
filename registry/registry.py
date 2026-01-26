
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class StrategySpec(BaseModel):
    id: str
    name: str
    family: str
    enabled: bool = True
    ingredients: Dict[str, Any] = {}
    regimes: List[str] = []

class EngineSpec(BaseModel):
    id: str
    name: str

class OverlaySpec(BaseModel):
    id: str
    name: str

class Registry(BaseModel):
    strategies: Dict[str, StrategySpec]
    engines: List[EngineSpec]
    overlays: List[OverlaySpec]

    @classmethod
    def load(cls, path: str):
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        # Convert list of strategies to dict for easier lookup
        if isinstance(data.get('strategies'), list):
            strat_dict = {s['id']: s for s in data['strategies']}
            data['strategies'] = strat_dict
        return cls(**data)
