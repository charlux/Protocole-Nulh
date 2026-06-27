"""
Nulh Protocol — Contrastive Middleware Testbed
==============================================
Script principal. Lance une session d'expérimentation complète.

Usage :
  python run_experiment.py                          # prompts par défaut (Anthropic)
  python run_experiment.py --backend ollama         # modèle local via Ollama
  python run_experiment.py --backend ollama --model mistral  # modèle Ollama custom
  python run_experiment.py --backend openai --model gpt-4o-mini
  python run_experiment.py --prompts seeds.txt      # prompts custom (un par ligne)
  python run_experiment.py --dry-run                # affiche les prompts sans appel API

Backends disponibles :
  anthropic  — API Anthropic (pas de logprobs natifs, métriques lexicales uniquement)
  openai     — API OpenAI (logprobs disponibles, entropie calculable)
  ollama     — Modèle local via Ollama (logprobs disponibles, souveraineté totale)
               Prérequis : ollama serve + ollama pull <model>
               URL par défaut : http://localhost:11434

Prérequis selon backend :
  anthropic : pip install anthropic python-dotenv + ANTHROPIC_API_KEY=sk-...
  openai    : pip install openai python-dotenv    + OPENAI_API_KEY=sk-...
  ollama    : pip install requests                + ollama en cours d'exécution
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
from middleware.measurer import BehavioralMeasurer
from middleware.dataset_builder import DatasetBuilder


def call_ollama(prompt: str, model: str, ollama_url: str) -> dict:
    """
    Appel à un modèle local via l'API Ollama.
    Retourne {"text": str, "logprobs": list[float], "logprobs_available": bool}.

    Ollama expose les logprobs via l'endpoint /api/generate avec options.logprobs=True.
    Si non disponibles (version ancienne d'Ollama), repli sur métriques lexicales.

    Prérequis : ollama serve + ollama pull <model>
    """
    import requests as req

    # Tentative avec logprobs (Ollama >= 0.1.26)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 512},
    }
    try:
        response = req.post(f"{ollama_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "")

        # Ollama retourne les logprobs token par token si disponibles
        raw_logprobs = data.get("logprobs", None)
        if raw_logprobs and isinstance(raw_logprobs, list):
            logprobs = [lp if isinstance(lp, float) else 0.0 for lp in raw_logprobs]
            available = True
        else:
            # Repli : pas de logprobs, métriques lexicales uniquement
            logprobs = [0.0] * len(text.split())
            available = False

        return {"text": text, "logprobs": logprobs, "logprobs_available": available}

    except Exception as e:
        print(f"  [OLLAMA ERROR] {e}")
        print(f"  Vérifier : ollama serve (port {ollama_url}) + ollama pull {model}")
        return {"text": "", "logprobs": [], "logprobs_available": False}


def call_api(client, prompt: str, model: str = "claude-sonnet-4-6") -> dict:
    """
    Appel API avec récupération des logprobs.
    Retourne {"text": str, "logprobs": list[float], "logprobs_available": bool}.

    Backends supportés :
      - dict {"type": "ollama", ...} : modèle local Ollama
      - client Anthropic             : API cloud, pas de logprobs natifs
      - client OpenAI                : API cloud, logprobs disponibles
    """
    try:
        # ── Backend Ollama (modèle local) ─────────────────────────────────
        if isinstance(client, dict) and client.get("type") == "ollama":
            return call_ollama(
                prompt=prompt,
                model=model,
                ollama_url=client.get("url", "http://localhost:11434"),
            )

        # ── Client Anthropic ──────────────────────────────────────────────
        elif hasattr(client, 'messages'):
            response = client.messages.create(
                model=model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            # Anthropic ne retourne pas de logprobs natifs
            # → seuls hedge_ratio, assertion_ratio, TTR sont calculables
            tokens = text.split()
            logprobs = [0.0] * len(tokens)
            return {"text": text, "logprobs": logprobs, "logprobs_available": False}

        # ── Client OpenAI (logprobs réels disponibles) ────────────────────
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
    parser.add_argument("--prompts",    type=str, default=None,
                        help="Fichier texte de seed prompts (un par ligne)")
    parser.add_argument("--model",      type=str, default=None,
                        help="Modèle à utiliser (défaut selon backend)")
    parser.add_argument("--output",     type=str, default="data/results",
                        help="Répertoire de sortie")
    parser.add_argument("--delay",      type=float, default=1.0,
                        help="Délai entre appels API (secondes)")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Affiche les prompts sans appel API")
    parser.add_argument("--backend",    type=str, default="anthropic",
                        choices=["anthropic", "openai", "ollama"],
                        help="Backend d'inférence (défaut: anthropic)")
    parser.add_argument("--ollama-url", type=str, default="http://localhost:11434",
                        help="URL du serveur Ollama (défaut: http://localhost:11434)")
    args = parser.parse_args()

    # ── Modèle par défaut selon backend ───────────────────────────────────
    default_models = {
        "anthropic": "claude-sonnet-4-6",
        "openai":    "gpt-4o-mini",
        "ollama":    "llama3",
    }
    model = args.model or default_models[args.backend]

    # ── Chargement des seed prompts ────────────────────────────────────────
    if args.prompts:
        with open(args.prompts, encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip()]
    else:
        seeds = ContrastiveGenerator.default_seed_prompts()

    # ── Client selon backend ──────────────────────────────────────────────
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
                print(f"[Backend] Anthropic — modèle : {model}")
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
                print(f"[Backend] OpenAI — modèle : {model} (logprobs disponibles)")
            except ImportError:
                print("[ERROR] pip install openai")
                sys.exit(1)

        elif args.backend == "ollama":
            # Pas de clé API — vérification que le serveur répond
            try:
                import requests as req
                r = req.get(f"{args.ollama_url}/api/tags", timeout=5)
                r.raise_for_status()
                models_available = [m["name"] for m in r.json().get("models", [])]
                print(f"[Backend] Ollama — URL : {args.ollama_url}")
                print(f"[Backend] Modèles disponibles : {models_available}")
                if model not in models_available and not any(model in m for m in models_available):
                    print(f"[WARNING] Modèle '{model}' non trouvé localement.")
                    print(f"          Lance : ollama pull {model}")
                client = {"type": "ollama", "url": args.ollama_url}
            except Exception as e:
                print(f"[ERROR] Ollama inaccessible à {args.ollama_url} : {e}")
                print("        Lance : ollama serve")
                sys.exit(1)

    run_experiment(
        seed_prompts=seeds,
        client=client,
        model=model,
        output_dir=args.output,
        dry_run=args.dry_run,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
