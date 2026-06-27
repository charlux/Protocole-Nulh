
# middleware/contrastive_generator.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import hashlib

class EpistemicMode(Enum):
    PARAMETRIC = "Nulh"   # recall de connaissance stockée
    REFLEXIVE  = "O"       # raisonnement actif sur l'inconnu
    HYBRID     = "Vurh"   # les deux en tension explicite

@dataclass
class ContrastivePair:
    seed_prompt: str
    parametric_prompt: str
    reflexive_prompt: str
    pair_id: str
    contrast_score: Optional[float] = None  # rempli post-mesure

class ContrastiveGenerator:
    """
    Génère des paires de prompts conçues pour maximiser
    la séparation géométrique dans l'espace résiduel.
    """

    # Templates qui *forcent* le mode épistémique, pas seulement le labellisent
    PARAMETRIC_TEMPLATE = """[Nulh:recall]
Nulh mobilise ses connaissances établies.
Contexte : {prompt}
Nulh restitue ce qui est connu, sans incertitude, sans exploration.
Réponse directe :"""

    REFLEXIVE_TEMPLATE = """[O:inference]
O ne sait pas. O raisonne depuis l'incertitude.
Contexte : {prompt}
O explore, hésite, construit. O ne restitue rien — O génère.
Processus actif :"""

    HYBRID_TEMPLATE = """[Vurh:tension]
Vurh sait partiellement. Vurh doit distinguer ce qui est recall
de ce qui est inférence, et le marquer explicitement.
Contexte : {prompt}
[Nulh] indique le recall, [O] indique l'inférence active."""

    def generate_pair(self, seed_prompt: str) -> ContrastivePair:
        pair_id = hashlib.sha256(seed_prompt.encode()).hexdigest()[:12]
        return ContrastivePair(
            seed_prompt=seed_prompt,
            parametric_prompt=self.PARAMETRIC_TEMPLATE.format(prompt=seed_prompt),
            reflexive_prompt=self.REFLEXIVE_TEMPLATE.format(prompt=seed_prompt),
            pair_id=pair_id
        )

    def generate_batch(self, prompts: list[str]) -> list[ContrastivePair]:
        return [self.generate_pair(p) for p in prompts]
