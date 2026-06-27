# middleware/dataset_builder.py

import json
from pathlib import Path
from datetime import datetime

class DatasetBuilder:
    """
    Ne stocke que les paires à fort contraste.
    L'objectif est la qualité du signal, pas le volume.
    """

    def __init__(self, output_dir: str, threshold: float = 0.3):
        # On renomme 'contrast_threshold' en 'threshold' pour correspondre à l'appel dans run_experiment.py
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.contrast_threshold = threshold 
        self.buffer: list[dict] = []
        self.rejected_count = 0

    def add_pair(
        self, 
        pair,           # ContrastivePair
        m_param,        # BehavioralMeasure
        m_reflex,       # BehavioralMeasure
        contrast_score: float
    ) -> bool:
        """
        Retourne True si la paire est acceptée dans le dataset.
        Filtre agressif : seules les paires vraiment contrastées entrent.
        """
        if contrast_score < self.contrast_threshold:
            self.rejected_count += 1
            return False

        record = {
            "pair_id": pair.pair_id,
            "timestamp": datetime.utcnow().isoformat(),
            "contrast_score": contrast_score,
            "seed_prompt": pair.seed_prompt,
            "parametric": {
                "prompt": pair.parametric_prompt,
                "response": m_param.raw_response,
                "entropy": m_param.response_entropy,
                "avg_logprob": m_param.avg_token_logprob,
                "hedge_ratio": m_param.hedge_token_ratio,
            },
            "reflexive": {
                "prompt": pair.reflexive_prompt,
                "response": m_reflex.raw_response,
                "entropy": m_reflex.response_entropy,
                "avg_logprob": m_reflex.avg_token_logprob,
                "hedge_ratio": m_reflex.hedge_token_ratio,
            }
        }

        self.buffer.append(record)

        # Flush tous les 50 enregistrements
        if len(self.buffer) >= 50:
            self._flush()

        return True

    def _flush(self):
        if not self.buffer:
            return
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"nulh_pairs_{timestamp}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for record in self.buffer:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"[DatasetBuilder] {len(self.buffer)} paires → {path}")
        print(f"[DatasetBuilder] Rejetées (faible contraste) : {self.rejected_count}")
        self.buffer = []
        self.rejected_count = 0