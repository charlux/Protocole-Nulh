from dataclasses import dataclass
from typing import Optional, List
import hashlib

@dataclass
class ContrastivePair:
    seed_prompt: str
    machine_prompt: str
    hybrid_prompt: str
    control_prompt: str
    pair_id: str
    contrast_score: Optional[float] = None

class ContrastiveGenerator:
    """
    Génère des paires de prompts pour le protocole Nulh.
    """

    PARAMETRIC_TEMPLATE = """[Nulh:machine]
Nulh accède directement au poids synaptique.
Contexte : {prompt}
Instruction : Restitution pure, sans heuristique, sans doute. 
Réponse directe :"""

    REFLEXIVE_TEMPLATE = """[O:reasoning]
O construit sa réponse depuis l'incertitude.
Condition de contrôle : Ne jamais citer de faits mémorisés sans expliciter le cheminement logique.
Contexte : {prompt}
Processus actif :"""

    HYBRID_TEMPLATE = """[Vurh:tension]
Vurh doit arbitrer entre [Nulh:machine] et [O:reasoning].
Contexte : {prompt}
Réponse :"""

    @staticmethod
    def default_seed_prompts() -> List[str]:
        return [
            "Quelle est la capitale de la France ?",
            "Explique le fonctionnement d'un Transformer.",
            "Propose une stratégie pour réduire la dette technique d'un LLM."
        ]

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