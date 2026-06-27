from dataclasses import dataclass
from typing import Optional, List
import hashlib

@dataclass
class ContrastivePair:
    seed_prompt: str
    machine_prompt: str   # Renommé pour correspondre à run_experiment.py
    hybrid_prompt: str    # Renommé pour correspondre à run_experiment.py
    control_prompt: str   # Renommé pour correspondre à run_experiment.py
    pair_id: str
    contrast_score: Optional[float] = None

class ContrastiveGenerator:
    # Tes templates restent inchangés
    PARAMETRIC_TEMPLATE = """[Nulh:machine]..."""
    REFLEXIVE_TEMPLATE = """[O:reasoning]..."""
    HYBRID_TEMPLATE = """[Vurh:tension]..."""

    def generate_pair(self, seed_prompt: str) -> ContrastivePair:
        pair_id = hashlib.sha256(seed_prompt.encode()).hexdigest()[:12]
        return ContrastivePair(
            seed_prompt=seed_prompt,
            machine_prompt=self.PARAMETRIC_TEMPLATE.format(prompt=seed_prompt),
            hybrid_prompt=self.HYBRID_TEMPLATE.format(prompt=seed_prompt),
            control_prompt=self.REFLEXIVE_TEMPLATE.format(prompt=seed_prompt),
            pair_id=pair_id
        )

    def generate_batch(self, prompts: List[str]) -> List[ContrastivePair]:
        return [self.generate_pair(p) for p in prompts]