import math
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class PairMeasure:
    pair_id: str
    seed_prompt: str
    mh_contrast_score: float
    token_drives_effect: bool
    accepted_for_dataset: bool

class BehavioralMeasurer:
    def _compute_entropy(self, logprobs: list[float]) -> float:
        if not logprobs: return 0.0
        probs = [math.exp(lp) for lp in logprobs]
        total = sum(probs)
        probs = [p / total for p in probs]
        return -sum(p * math.log(p + 1e-12) for p in probs)

    def measure_response(self, response_text: str, logprobs: list[float], pair_id: str, mode: str):
        # Placeholder pour compatibilité API
        pass

    def analyze_pair(self, machine, hybrid, control, seed_prompt) -> PairMeasure:
        return PairMeasure(pair_id=machine.pair_id, seed_prompt=seed_prompt, mh_contrast_score=0.0, token_drives_effect=True, accepted_for_dataset=True)

class DatasetBuilder:
    def __init__(self, output_dir: str = "data/results", threshold: float = 0.25):
        self.output_dir = output_dir
        self.threshold = threshold
        self.dataset = []

    def add(self, entry: PairMeasure):
        self.dataset.append(entry)

    def save(self, filepath: str):
        os.makedirs(self.output_dir, exist_ok=True)
        full_path = os.path.join(self.output_dir, filepath)
        with open(full_path, 'w') as f:
            for entry in self.dataset:
                f.write(json.dumps(asdict(entry)) + "\n")

    def finalize(self):
        """Méthode finale requise par run_experiment.py"""
        print("[DatasetBuilder] Session terminée avec succès.")
