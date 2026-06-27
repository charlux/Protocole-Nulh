"""
Nulh Protocol — Contrastive Middleware Testbed
==============================================
Script principal. Lance une session d'expérimentation complète.

Usage :
  python run_experiment.py                    # prompts par défaut
  python run_experiment.py --prompts seeds.txt # prompts custom (un par ligne)
  python run_experiment.py --dry-run           # affiche les prompts sans appel API

Prérequis :
  pip install anthropic python-dotenv
  export ANTHROPIC_API_KEY=sk-...
  (ou créer un fichier .env avec ANTHROPIC_API_KEY=sk-...)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Compatibilité import depuis la racine du repo
sys.path.insert(0, str(Path(__file__).parent))

from middleware.generator import ContrastiveGenerator
from middleware.measurer import BehavioralMeasurer, DatasetBuilder


def call_api(client, prompt: str, model: str = "claude-sonnet-4-6") -> dict:
    """
    Appel API avec récupération des logprobs.
    Retourne {"text": str, "logprobs": list[float]}.

    Note : l'API Anthropic ne retourne pas de logprobs natifs sur tous les modèles.
    Pour les logprobs, utiliser l'API OpenAI (gpt-4o-mini) ou un modèle local.
    Ce wrapper est adaptatif selon le client détecté.
    """
    try:
        # Client Anthropic
        if hasattr(client, 'messages'):
            response = client.messages.create(
                model=model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            # Anthropic ne retourne pas de logprobs : on simule avec des zéros
            # → les métriques basées sur l'entropie seront indisponibles
            # → seuls hedge_ratio, assertion_ratio, TTR sont calculables
            tokens = text.split()
            logprobs = [0.0] * len(tokens)
            return {"text": text, "logprobs": logprobs, "logprobs_available": False}

        # Client OpenAI (pour comparaison avec logprobs réels)
        elif hasattr(client, 'chat'):
            response = client.chat.completions.create(
                model=model,
                max_tokens=512,
                logprobs=True,
                top_logprobs=1,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content
            lps = response.choices[0].logprobs.content
            logprobs = [t.logprob for t in lps] if lps else [0.0]
            return {"text": text, "logprobs": logprobs, "logprobs_available": True}

    except Exception as e:
        print(f"  [API ERROR] {e}")
        return {"text": "", "logprobs": [], "logprobs_available": False}


def run_experiment(
    seed_prompts: list[str],
    client,
    model: str,
    output_dir: str = "data/results",
    dry_run: bool = False,
    delay: float = 1.0,
):
    generator = ContrastiveGenerator()
    measurer  = BehavioralMeasurer()
    builder   = DatasetBuilder(output_dir=output_dir, threshold=0.25)

    pairs = generator.generate_batch(seed_prompts)
    print(f"\n[Testbed] {len(pairs)} paires à traiter.")
    print(f"[Testbed] Mode : {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"[Testbed] Modèle : {model}\n")

    for i, pair in enumerate(pairs):
        print(f"[{i+1}/{len(pairs)}] seed: {pair.seed_prompt[:60]}...")

        if dry_run:
            print(f"  → machine_prompt :\n{pair.machine_prompt}\n")
            print(f"  → hybrid_prompt  :\n{pair.hybrid_prompt}\n")
            print(f"  → control_prompt :\n{pair.control_prompt}\n")
            continue

        # ── 3 appels par paire ────────────────────────────────────────────
        r_machine = call_api(client, pair.machine_prompt, model)
        time.sleep(delay)
        r_hybrid  = call_api(client, pair.hybrid_prompt,  model)
        time.sleep(delay)
        r_control = call_api(client, pair.control_prompt, model)
        time.sleep(delay)

        if not r_machine["text"] or not r_hybrid["text"]:
            print("  [SKIP] réponse vide — API error")
            continue

        # ── Mesures ───────────────────────────────────────────────────────
        m_machine = measurer.measure_response(
            r_machine["text"], r_machine["logprobs"], pair.pair_id, "machine"
        )
        m_hybrid  = measurer.measure_response(
            r_hybrid["text"],  r_hybrid["logprobs"],  pair.pair_id, "hybrid"
        )
        m_control = measurer.measure_response(
            r_control["text"], r_control["logprobs"], pair.pair_id, "control"
        )

        pm = measurer.analyze_pair(m_machine, m_hybrid, m_control, pair.seed_prompt)

        # ── Affichage en temps réel ───────────────────────────────────────
        verdict = "✓ TOKEN DRIVE" if pm.token_drives_effect else "✗ TEMPLATE DRIVE"
        accepted = "→ ACCEPTÉE" if pm.accepted_for_dataset else "→ rejetée"
        print(f"  contrast={pm.mh_contrast_score:.3f}  {verdict}  {accepted}")

        if not r_machine["logprobs_available"]:
            print("  [NOTE] logprobs non disponibles — entropie indisponible")

        builder.add(pm)

    builder.finalize()


def main():
    parser = argparse.ArgumentParser(description="Nulh Protocol — Contrastive Testbed")
    parser.add_argument("--prompts",  type=str, default=None,
                        help="Fichier texte de seed prompts (un par ligne)")
    parser.add_argument("--model",    type=str, default="claude-sonnet-4-6",
                        help="Modèle à utiliser")
    parser.add_argument("--output",   type=str, default="data/results",
                        help="Répertoire de sortie")
    parser.add_argument("--delay",    type=float, default=1.0,
                        help="Délai entre appels API (secondes)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Affiche les prompts sans appel API")
    parser.add_argument("--backend",  type=str, default="anthropic",
                        choices=["anthropic", "openai"],
                        help="Backend API à utiliser")
    args = parser.parse_args()

    # ── Chargement des seed prompts ────────────────────────────────────────
    if args.prompts:
        with open(args.prompts, encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip()]
    else:
        seeds = ContrastiveGenerator.default_seed_prompts()

    # ── Client API ────────────────────────────────────────────────────────
    client = None
    if not args.dry_run:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        if args.backend == "anthropic":
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    print("[ERROR] ANTHROPIC_API_KEY non définie.")
                    sys.exit(1)
                client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("[ERROR] pip install anthropic")
                sys.exit(1)

        elif args.backend == "openai":
            try:
                import openai
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    print("[ERROR] OPENAI_API_KEY non définie.")
                    sys.exit(1)
                client = openai.OpenAI(api_key=api_key)
            except ImportError:
                print("[ERROR] pip install openai")
                sys.exit(1)

    run_experiment(
        seed_prompts=seeds,
        client=client,
        model=args.model,
        output_dir=args.output,
        dry_run=args.dry_run,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
