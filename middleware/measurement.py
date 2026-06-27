
# middleware/measurement.py

import numpy as np
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class BehavioralMeasure:
    """
    Mesures accessibles via API standard (logprobs).
    Proxy indirect de la géométrie interne.
    """
    pair_id: str
    mode: str

    # Métriques sur l'output
    response_entropy: float        # entropie de la distribution de tokens
    avg_token_logprob: float       # confiance moyenne du modèle
    lexical_divergence: float      # distance entre les deux réponses d'une paire
    hedge_token_ratio: float       # ratio "peut-être/probablement/je pense"
    factual_token_ratio: float     # ratio tokens factuels/assertifs

    raw_response: str = ""

@dataclass
class ActivationMeasure:
    """
    Mesures profondes — nécessite modèle local (TransformerLens).
    """
    pair_id: str
    mode: str
    layer_index: int

    residual_vector: np.ndarray = field(default_factory=lambda: np.array([]))
    cosine_distance_to_pair: Optional[float] = None
    linear_separability_score: Optional[float] = None  # probing classifier acc


class BehavioralMeasurer:
    """Fonctionne avec n'importe quelle API (logprobs requis)."""

    HEDGE_TOKENS = {
        "peut-être", "probablement", "je pense", "il semble",
        "possibly", "perhaps", "likely", "I think", "seems"
    }
    FACTUAL_TOKENS = {
        "est", "sont", "a", "ont", "était", "en", "depuis",
        "is", "are", "has", "was", "in", "since", "the"
    }

    def measure(self, response: str, logprobs: list[float], 
                pair_id: str, mode: str) -> BehavioralMeasure:
        tokens = response.split()

        # Entropie de la réponse (via logprobs)
        probs = np.exp(logprobs)
        entropy = -np.sum(probs * np.log(probs + 1e-10))

        hedge_ratio = sum(
            1 for t in tokens 
            if t.lower() in self.HEDGE_TOKENS
        ) / max(len(tokens), 1)

        factual_ratio = sum(
            1 for t in tokens 
            if t.lower() in self.FACTUAL_TOKENS
        ) / max(len(tokens), 1)

        return BehavioralMeasure(
            pair_id=pair_id,
            mode=mode,
            response_entropy=float(entropy),
            avg_token_logprob=float(np.mean(logprobs)),
            lexical_divergence=0.0,  # calculé post-paire
            hedge_token_ratio=hedge_ratio,
            factual_token_ratio=factual_ratio,
            raw_response=response
        )

    def compute_pair_divergence(
        self, 
        m_parametric: BehavioralMeasure, 
        m_reflexive: BehavioralMeasure
    ) -> float:
        """
        Score de contraste comportemental entre les deux membres d'une paire.
        Plus ce score est élevé, plus la paire est utile pour le dataset.
        """
        entropy_delta = abs(
            m_reflexive.response_entropy - m_parametric.response_entropy
        )
        hedge_delta = abs(
            m_reflexive.hedge_token_ratio - m_parametric.hedge_token_ratio
        )
        factual_delta = abs(
            m_reflexive.factual_token_ratio - m_parametric.factual_token_ratio
        )

        # Score composite — pondéré empiriquement, à calibrer
        contrast_score = (
            0.4 * entropy_delta +
            0.35 * hedge_delta +
            0.25 * factual_delta
        )
        return float(contrast_score)
