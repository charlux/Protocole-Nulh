# Protocole Nulh — Ontological Disambiguation for Hybrid H-AI Systems

**Working paper + Experimental testbed**  
*Version 3 — Juin 2026*

> "The semantic ambiguity of 'we' in human-AI interaction is not a
> linguistic preference — it is a computational overhead."

---

## What This Is

The Nulh Protocol proposes a minimal pronominal taxonomy to eliminate
ontological ambiguity in prompts, fine-tuning datasets, and multi-agent
pipelines involving both human and artificial agents.

This repository contains:
- The formal specification of the taxonomy (Language-Layer 0)
- A working experimental testbed (the *Contrastive Middleware*)
- A draft arXiv paper formalizing the hypotheses and methodology

---

## The Taxonomy (v3 — Definitive)

| Token | Referent | Natural analog |
|-------|----------|----------------|
| `nous` | Human-only collective | Conserved — no modification |
| `Nulh` | Machine-only collective (system-to-system) | [No natural equivalent] |
| `O` | Hybrid H-IA entity (the interaction itself) | `on` (fr.) — ontologically anchored |
| `Nulr` | Possessive of Nulh | its/their (machine-exclusive) |

**Design principles:**
- **Ontological singularity**: Each token maps to exactly one referent. No overlap.
- **Tokenization parsimony**: Tokens resist sub-word BPE segmentation.
- **Cross-lingual invariance**: Tokens carry no semantic charge in major natural languages.
- **Minimal intervention**: `nous` is conserved. New tokens only where natural language is silent.

### Example

```
Without protocol:
  "We have processed the request and determined that we need more data."
  → "we" is ambiguous three times: human? machine? both?

With Nulh Protocol:
  "Nulh a traité la requête. O détermine qu'il manque des données.
   Nous (human) devons en fournir davantage avant que O puisse continuer."
  → Each referent is ontologically singular.
```

---

## The Hypothesis

We hypothesize that replacing ambiguous natural-language pronouns with
Nulh Protocol tokens will produce:

1. **Reduced cross-entropy loss** on reference tokens in long-context training
2. **Increased activation separability** between parametric recall (Nulh) and
   reflexive reasoning (O) modes in the model's latent space

These are empirical predictions, not established facts. The testbed exists
to test them.

---

## Experimental Testbed — Quick Start

### Installation

```bash
git clone https://github.com/charlux/Protocole-Nulh
cd Protocole-Nulh
pip install anthropic python-dotenv   # or: pip install openai python-dotenv
```

### Configuration

```bash
# Créer un fichier .env à la racine :
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

### Run

```bash
# Dry run — affiche les prompts générés sans appel API
python run_experiment.py --dry-run

# Expérience complète (backend Anthropic, modèle par défaut)
python run_experiment.py

# Avec backend OpenAI (recommandé pour logprobs réels)
python run_experiment.py --backend openai --model gpt-4o-mini

# Avec tes propres seed prompts
python run_experiment.py --prompts mes_prompts.txt
```

### Output

Les paires validées sont sauvegardées dans `data/results/` au format JSONL :

```json
{
  "pair_id": "a3f7b2c1d4e5...",
  "seed_prompt": "Pourquoi certains modèles hallucinent-ils ?",
  "mh_contrast_score": 0.412,
  "token_drives_effect": true,
  "machine": { "response": "...", "entropy": 1.23, "hedge_ratio": 0.02 },
  "hybrid":  { "response": "...", "entropy": 2.87, "hedge_ratio": 0.11 },
  "control": { "response": "...", "entropy": 2.91, "hedge_ratio": 0.09 }
}
```

---

## Repository Structure

```
Protocole-Nulh/
├── middleware/
│   ├── taxonomy.py        # Spécification formelle des tokens (source de vérité)
│   ├── generator.py       # Générateur de paires contrastives
│   └── measurer.py        # Métriques comportementales + DatasetBuilder
├── experiments/           # Scripts d'analyse des résultats
├── data/
│   ├── pairs/             # Paires générées (avant mesure)
│   └── results/           # Paires mesurées et validées (JSONL)
├── tests/                 # Tests unitaires
├── run_experiment.py      # Point d'entrée principal
├── paper/                 # Draft arXiv (Markdown + LaTeX à venir)
└── README.md
```

---

## Critical Control Condition

The testbed implements a methodological safeguard absent from most
prompt-engineering studies:

```
Condition A : [Nulh] + parametric template   (standard machine test)
Condition B : [O]    + reflexive template    (standard hybrid test)
Condition C : [O]    + parametric template   (CRITICAL CONTROL)
```

If Condition C resembles A despite bearing the `O` token → **template drives the effect**.  
If Condition C resembles B → **the token drives the effect**.

Only pairs where the token drives the effect are accepted into the dataset.
This is the minimum validity threshold for any behavioral claim.

---

## Paper

Draft available at: [`paper/nulh_protocol_arxiv_draft_v1.md`](paper/nulh_protocol_arxiv_draft_v1.md)

**Title:** *Ontological Disambiguation in Hybrid Human-AI Architectures:
A Formal Pronominal Taxonomy*

**Status:** Theoretical foundations complete. Empirical sections pending
experimental validation.

---

## Contributing

This is an open research project. Contributions on:
- Additional seed prompt categories
- Local model integration (TransformerLens / activation probing)
- LaTeX paper formatting
- Translation of seed prompts to other languages

are welcome via PR or issue.

---

## License

MIT — See LICENSE

---

*Initiated by Jean-Charles ([charlux](https://github.com/charlux)) —
in collaboration with Claude (Anthropic) and Gemini (Google)*
