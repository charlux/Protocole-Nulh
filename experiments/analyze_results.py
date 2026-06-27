"""
Nulh Protocol — Results Analyzer
==================================
Lit les fichiers JSONL produits par run_experiment.py
et génère les figures et statistiques pour le papier arXiv.

Usage :
  python experiments/analyze_results.py --input data/results/
  python experiments/analyze_results.py --input data/results/ --save figures/
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np


def load_results(input_dir: str) -> list[dict]:
    """Charge tous les fichiers JSONL du répertoire."""
    records = []
    for path in sorted(Path(input_dir).glob("nulh_pairs_*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def compute_summary_stats(records: list[dict]) -> dict:
    """Statistiques descriptives globales."""
    n_total    = len(records)
    n_accepted = sum(1 for r in records if r.get("token_drives_effect"))
    n_rejected = n_total - n_accepted

    contrast_scores = [r["mh_contrast_score"] for r in records]
    token_drive_rate = n_accepted / max(n_total, 1)

    # Entropie par mode (si disponible)
    entropy_machine, entropy_hybrid, entropy_control = [], [], []
    hedge_machine, hedge_hybrid = [], []

    for r in records:
        if r.get("machine") and r["machine"].get("entropy", 0) != 0:
            entropy_machine.append(r["machine"]["entropy"])
            hedge_machine.append(r["machine"].get("hedge_ratio", 0))
        if r.get("hybrid") and r["hybrid"].get("entropy", 0) != 0:
            entropy_hybrid.append(r["hybrid"]["entropy"])
            hedge_hybrid.append(r["hybrid"].get("hedge_ratio", 0))
        if r.get("control") and r["control"].get("entropy", 0) != 0:
            entropy_control.append(r["control"]["entropy"])

    return {
        "n_total": n_total,
        "n_accepted": n_accepted,
        "n_rejected": n_rejected,
        "token_drive_rate": token_drive_rate,
        "contrast_mean": np.mean(contrast_scores) if contrast_scores else 0,
        "contrast_std":  np.std(contrast_scores)  if contrast_scores else 0,
        "entropy_machine_mean": np.mean(entropy_machine) if entropy_machine else None,
        "entropy_hybrid_mean":  np.mean(entropy_hybrid)  if entropy_hybrid  else None,
        "entropy_control_mean": np.mean(entropy_control) if entropy_control else None,
        "hedge_machine_mean": np.mean(hedge_machine) if hedge_machine else None,
        "hedge_hybrid_mean":  np.mean(hedge_hybrid)  if hedge_hybrid  else None,
        "logprobs_available": len(entropy_machine) > 0,
    }


def print_report(stats: dict, records: list[dict]):
    """Rapport texte — peut être copié directement dans le papier."""
    print("=" * 60)
    print("NULH PROTOCOL — EXPERIMENTAL RESULTS SUMMARY")
    print("=" * 60)

    print(f"\n▸ Pairs processed      : {stats['n_total']}")
    print(f"▸ Token-drive accepted : {stats['n_accepted']} "
          f"({stats['token_drive_rate']:.1%})")
    print(f"▸ Template-drive reject: {stats['n_rejected']}")

    print(f"\n▸ Contrast score (M vs H)")
    print(f"    mean = {stats['contrast_mean']:.4f}")
    print(f"    std  = {stats['contrast_std']:.4f}")

    if stats["logprobs_available"]:
        print(f"\n▸ Response entropy (logprobs available)")
        print(f"    Nulh (machine) : {stats['entropy_machine_mean']:.4f}")
        print(f"    O    (hybrid)  : {stats['entropy_hybrid_mean']:.4f}")
        if stats["entropy_control_mean"] is not None:
            print(f"    Control        : {stats['entropy_control_mean']:.4f}")
        delta = (stats["entropy_hybrid_mean"] or 0) - (stats["entropy_machine_mean"] or 0)
        print(f"    Δ (H - M)      : {delta:+.4f}")
        if delta > 0:
            print("    → Hybrid mode produces higher entropy (expected)")
        else:
            print("    → WARNING: entropy did not increase in hybrid mode")
    else:
        print("\n▸ Response entropy : NOT AVAILABLE (logprobs disabled)")
        print("    Use --backend openai for full entropy measurement")

    if stats["hedge_machine_mean"] is not None:
        print(f"\n▸ Hedge ratio")
        print(f"    Nulh (machine) : {stats['hedge_machine_mean']:.4f}")
        print(f"    O    (hybrid)  : {stats['hedge_hybrid_mean']:.4f}")

    # Condition de contrôle : verdict
    n_control_closer_to_hybrid = sum(
        1 for r in records
        if r.get("control_proximity_to_hybrid", 0) >
           r.get("control_proximity_to_machine", 0)
    )
    pct = n_control_closer_to_hybrid / max(stats["n_total"], 1)
    print(f"\n▸ Control condition verdict")
    print(f"    Control closer to Hybrid  : {n_control_closer_to_hybrid} "
          f"({pct:.1%})")
    print(f"    Control closer to Machine : {stats['n_total'] - n_control_closer_to_hybrid} "
          f"({1-pct:.1%})")
    if pct > 0.6:
        print("    → TOKEN drives the effect (supports H1)")
    elif pct < 0.4:
        print("    → TEMPLATE drives the effect (H1 not supported)")
    else:
        print("    → INCONCLUSIVE — increase sample size")

    print("\n" + "=" * 60)

    # Exemples qualitatifs (3 paires à fort contraste)
    top3 = sorted(records, key=lambda r: r["mh_contrast_score"], reverse=True)[:3]
    if top3:
        print("\nTOP 3 HIGHEST-CONTRAST PAIRS (qualitative)\n")
        for i, r in enumerate(top3):
            print(f"[{i+1}] seed: {r['seed_prompt'][:70]}")
            print(f"     contrast={r['mh_contrast_score']:.3f}  "
                  f"token_drive={r['token_drives_effect']}")
            if r.get("machine"):
                resp = r["machine"]["response"][:120].replace("\n", " ")
                print(f"     Nulh: {resp}...")
            if r.get("hybrid"):
                resp = r["hybrid"]["response"][:120].replace("\n", " ")
                print(f"     O   : {resp}...")
            print()


def generate_figures(records: list[dict], save_dir: str | None = None):
    """
    Génère les figures matplotlib pour le papier.
    Nécessite : pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("[figures] matplotlib non installé — pip install matplotlib")
        return

    save_path = Path(save_dir) if save_dir else None
    if save_path:
        save_path.mkdir(parents=True, exist_ok=True)

    # ── Figure 1 : Distribution des contrast scores ───────────────────────
    scores = [r["mh_contrast_score"] for r in records]
    accepted = [r["mh_contrast_score"] for r in records if r.get("token_drives_effect")]
    rejected = [r["mh_contrast_score"] for r in records if not r.get("token_drives_effect")]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Nulh Protocol — Contrastive Testbed Results", fontsize=13)

    ax = axes[0]
    ax.hist(accepted, bins=15, alpha=0.7, color="#2196F3", label="Token-drive (accepted)")
    ax.hist(rejected, bins=15, alpha=0.7, color="#FF5722", label="Template-drive (rejected)")
    ax.axvline(0.25, color="black", linestyle="--", linewidth=1, label="Threshold=0.25")
    ax.set_xlabel("Contrast Score (M vs H)")
    ax.set_ylabel("Count")
    ax.set_title("Figure 1: Contrast Score Distribution")
    ax.legend(fontsize=9)

    # ── Figure 2 : Proximité du contrôle aux deux modes ──────────────────
    prox_machine = [r.get("control_proximity_to_machine", 0) for r in records]
    prox_hybrid  = [r.get("control_proximity_to_hybrid",  0) for r in records]

    ax2 = axes[1]
    ax2.scatter(prox_machine, prox_hybrid, alpha=0.6, c=[
        "#2196F3" if r.get("token_drives_effect") else "#FF5722"
        for r in records
    ], s=40)
    ax2.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="y=x (indeterminate)")
    ax2.set_xlabel("Control proximity to Machine (Nulh)")
    ax2.set_ylabel("Control proximity to Hybrid (O)")
    ax2.set_title("Figure 2: Control Condition Verdict")
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    p1 = mpatches.Patch(color="#2196F3", label="Token-drive")
    p2 = mpatches.Patch(color="#FF5722", label="Template-drive")
    ax2.legend(handles=[p1, p2], fontsize=9)

    plt.tight_layout()

    if save_path:
        out = save_path / "nulh_results_fig1_fig2.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        print(f"[figures] Sauvegardé → {out}")
    else:
        plt.show()
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Nulh Protocol — Analyze experimental results"
    )
    parser.add_argument("--input",  type=str, default="data/results",
                        help="Répertoire contenant les fichiers JSONL")
    parser.add_argument("--save",   type=str, default=None,
                        help="Répertoire de sauvegarde des figures (optionnel)")
    parser.add_argument("--no-figures", action="store_true",
                        help="Ne génère pas les figures matplotlib")
    args = parser.parse_args()

    records = load_results(args.input)
    if not records:
        print(f"[ERROR] Aucun fichier JSONL trouvé dans '{args.input}'")
        print("        Lance d'abord : python run_experiment.py")
        sys.exit(1)

    stats = compute_summary_stats(records)
    print_report(stats, records)

    if not args.no_figures:
        generate_figures(records, save_dir=args.save)


if __name__ == "__main__":
    main()
