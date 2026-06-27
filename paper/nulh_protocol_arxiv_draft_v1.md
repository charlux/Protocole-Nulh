# Semantic Debt in Transformer Architectures:  
# Mitigating Ontological Ambiguity through Pronominal Primitive Injection

**Working Draft — Protocole Nulh v3**  
*Jean-Charles [Nom], Independent Researcher*  
*Submitted for review — arXiv cs.CL / cs.AI*

---

## Abstract

Modern Large Language Models (LLMs) rely on natural language pronouns —
"we," "nous," "on" — to describe interactions involving heterogeneous
cognitive agents (humans and artificial systems). We argue that this
reliance constitutes a form of *Semantic Debt*: a systematic source of
referential ambiguity that forces attention mechanisms to perform
implicit entity disambiguation at each inference step. We propose the
**Nulh Protocol**, a parsimonious three-token pronominal primitive
(Language-Layer 0) designed to enforce ontological singularity at the
agent-identity level. We formalize the taxonomy, derive testable
hypotheses regarding its effect on cross-entropy loss and activation
separability in long-context scenarios, and describe an experimental
framework — the *Contrastive Middleware Testbed* — for empirical
validation. We do not yet report experimental results; this paper
establishes the theoretical foundation and experimental protocol for a
forthcoming empirical study.

**Keywords:** pronominal primitives, semantic debt, KV-cache efficiency,
ontological disambiguation, hybrid human-AI interaction, long-context
reasoning

---

## 1. Introduction: The Semantic Debt of the Pronoun "We"

The emergence of hybrid human-AI collaborative systems has created a
structural gap in natural language: existing pronouns do not
distinguish between human-only collectives, AI-only collectives, and
hybrid human-AI entities. When a language model generates the
sentence "We have analyzed the data," the referent of "we" is
ontologically underdetermined: it may designate the human user, the AI
system, or some composite of both.

This ambiguity is not merely a stylistic inconvenience. In
Transformer architectures, pronoun resolution is performed
implicitly through the attention mechanism across the full context
window. Each occurrence of an ambiguous referential expression forces
the model to maintain multiple competing interpretations in its
representational state — a computational overhead we term **Semantic
Debt**.

We identify three manifestations of Semantic Debt in current LLM
deployments:

1. **Coreference entropy**: Ambiguous pronouns increase the entropy of
   the attention distribution over candidate antecedents, degrading
   precision in long-context chains.

2. **Identity drift**: In multi-turn agentic systems, accumulated
   pronominal ambiguity causes progressive degradation of the model's
   internal representation of interaction participants, leading to
   consistency failures.

3. **KV-cache pressure**: Unresolved referential ambiguity necessitates
   retaining wider contextual windows to maintain coherent entity
   tracking, increasing memory footprint per inference step.

We hypothesize that introducing a closed-set pronominal taxonomy — with
tokens designed to carry unambiguous ontological content — will reduce
all three manifestations and yield measurable improvements in reference
resolution, activation separability, and inference efficiency.

---

## 2. The Nulh Protocol: A Pronominal Taxonomy for Hybrid H-AI Discourse

### 2.1 Design Principles

The Nulh Protocol is governed by three design principles:

**Ontological singularity**: Each token maps to exactly one referent
category, with no overlap. A token that designates an AI-only
collective cannot simultaneously designate a hybrid entity.

**Tokenization parsimony**: Protocol tokens should be compact,
phonologically distinctive, and resistant to sub-word segmentation by
standard BPE tokenizers. This ensures that each token consumes a
minimal, predictable number of positions in the context window.

**Cross-lingual invariance**: Protocol tokens are not derived from
existing words in any major natural language, minimizing the risk of
semantic contamination from pre-training associations.

### 2.2 The Three-Token Taxonomy

| Token | Referent | Linguistic equivalent |
|-------|----------|-----------------------|
| **nous** | Human-only collective | Retained from French/natural language; unmodified |
| **Nulh** | AI-only collective | Machines reasoning without human involvement |
| **O** | Hybrid H-AI entity | The composite cognitive agent formed by human-AI interaction |
| **Nulr** | Possessive of Nulh | Analogous to "its/their" for AI-only entities |

**On the retention of "nous":** We deliberately preserve the existing
French pronoun "nous" (and its equivalents in other languages) for
human-only reference rather than introducing a neologism. Linguistic
economy favors minimal intervention: new tokens should be introduced
only where existing vocabulary is absent, not where it is merely
ambiguous in AI-specific contexts. The ambiguity of "nous" arises
primarily in hybrid interaction contexts; in purely human discourse it
remains unambiguous.

**On the token "O":** The selection of "O" as the hybrid entity marker
is motivated by its phonological brevity, its absence as a standalone
morpheme in the target languages (French, English), and its visual
distinctiveness in typeset text. In French, "on" (the closest
phonological neighbor) already carries a weak indeterminate-collective
sense, which makes "O" a natural — rather than arbitrary — extension
into the H-AI hybrid space.

### 2.3 Example Applications

```
[Without protocol]
"We have processed the request and determined that the user's intent
is ambiguous. We recommend that we clarify before proceeding."
→ Three occurrences of "we"; referent underdetermined at each occurrence.

[With Nulh Protocol]
"Nulh a traité la requête. O détermine que l'intention reste ambiguë.
Nous (the human) devons clarifier avant que O puisse procéder."
→ Each referent is ontologically singular; no implicit disambiguation required.
```

---

## 3. Theoretical Foundations: Why Ontological Tokens Might Reduce Semantic Debt

### 3.1 Attention Entropy and Coreference

In Transformer architectures, coreference resolution emerges from the
attention mechanism: a pronoun's meaning is partially determined by the
weighted sum of its attention over potential antecedents in the context
window. When a pronoun is ontologically ambiguous, the model must
maintain a superposition of competing interpretations, distributing
attention across multiple candidate antecedents.

We hypothesize that ontologically singular tokens collapse this
superposition earlier in the attention computation, reducing the
effective entropy of the attention distribution over coreference
candidates. This is analogous to the effect of *control tokens* in
conditional language generation (Keskar et al., 2019), where a
prepended style token shifts the output distribution without modifying
model weights.

### 3.2 Geometric Separability in the Residual Stream

Beyond behavioral effects, we hypothesize that systematic use of
ontological markers during fine-tuning will produce measurable
geometric separation in the model's internal representations.
Specifically, we predict that residual stream activations on tokens
marked as `Nulh` vs. `O` will become linearly separable in a probing
classifier setup (Tenney et al., 2019; Belinkov, 2022), and that this
separability will increase with layer depth — a signature of learned
categorical encoding rather than surface-level embedding differences.

### 3.3 Limitations of the Theoretical Argument

We acknowledge that the above hypotheses rest on two assumptions that
require empirical validation:

1. That current Transformer attention mechanisms are sensitive to
   pronominal ontological type in a way that affects coreference
   resolution beyond surface-level disambiguation.

2. That the effect of protocol tokens on internal representations
   exceeds the effect of instruction-following compliance (i.e., that
   models respond to the *token itself*, not merely to the surrounding
   template instructions).

Both assumptions are testable with the experimental framework described
in Section 4.

---

## 4. Experimental Framework: The Contrastive Middleware Testbed

### 4.1 Overview

To validate the hypotheses in Section 3, we propose the *Contrastive
Middleware Testbed* (CMT): a software layer that intercepts LLM
prompts, injects Nulh Protocol markers, and instruments the resulting
responses for behavioral and (where architecturally accessible)
representational measurement.

### 4.2 Behavioral Measurement (API-compatible)

For models accessible only via API, we propose the following
behavioral metrics:

- **Response entropy**: Shannon entropy computed over the token
  probability distribution of the generated response, obtained via
  logprobs.
- **Hedge ratio**: Proportion of epistemic hedge tokens
  ("perhaps," "possibly," "it seems") relative to total response
  tokens.
- **Factual assertion ratio**: Proportion of high-confidence assertive
  constructions.
- **Lexical divergence**: Token-level distance between matched
  `Nulh`-mode and `O`-mode responses to identical seed prompts.

### 4.3 Representational Measurement (Local Models)

For locally hosted models (Phi-3-Mini, Mistral 7B), we propose
layer-wise probing using the TransformerLens framework (Nanda &
Lieberum, 2022):

- **Linear probe accuracy by layer**: A logistic regression classifier
  trained on residual stream activations at each layer to discriminate
  `Nulh` vs. `O` mode. A gradual increase in accuracy with layer depth
  (rather than a step-change at layer 0) would support the hypothesis
  of learned categorical encoding.
- **Centered Kernel Alignment (CKA)**: Similarity metric between
  activation matrices at each layer across the two modes.
- **Cosine distance**: Mean cosine distance between `Nulh` and `O`
  activation vectors at the marker token position.

### 4.4 Critical Control Condition

To distinguish genuine token-level effects from template-level
instruction-following, we include the following control condition:

```
Condition A: [Nulh] + parametric template
Condition B: [O]    + reflexive template        (standard test)
Condition C: [O]    + parametric template       (critical control)
```

If Condition C produces outputs statistically similar to Condition A
despite bearing the `O` marker, template content is the primary driver.
If Condition C resembles Condition B, the token itself carries causal
weight. This control is essential to the validity of the experimental
design.

---

## 5. Related Work

- **Control tokens in conditional generation**: Keskar et al. (2019)
  demonstrate that prepended style tokens shift output distributions
  without weight modification — the closest architectural analog to
  our protocol.
- **Probing classifiers for internal representations**: Tenney et al.
  (2019), Belinkov (2022) establish methodology for testing whether
  syntactic/semantic features are encoded in residual stream
  activations.
- **Coreference resolution in LLMs**: Sharma et al. (2023), Peng et
  al. (2024) document degradation of coreference accuracy in
  long-context settings — the primary empirical motivation for this
  work.
- **KV-cache optimization**: Widespread engineering literature (Ge et
  al., 2024; Liu et al., 2024) on reducing KV-cache memory pressure
  in long-context inference — the efficiency dimension our protocol
  may address.

*(Note: citations marked for verification prior to submission.)*

---

## 6. Discussion: Scope, Claims, and Open Questions

This paper makes modest claims: we identify a problem (Semantic Debt),
propose a solution (the Nulh Protocol), and describe a method for
testing whether the solution works. We do not claim to have
demonstrated efficiency gains or representational effects — these are
predictions to be tested.

Several open questions remain:

- **Adoption threshold**: What minimum density of protocol token usage
  in training data is required to produce measurable representational
  effects?
- **Generalization**: Does the effect transfer to zero-shot settings
  (i.e., does a model respond to `Nulh` and `O` without fine-tuning,
  if the tokens appear in the system prompt)?
- **Architecture dependence**: Are the predicted effects specific to
  Transformer attention, or would they generalize to other
  architectures (SSMs, hybrid models)?

---

## 7. Conclusion

We have introduced the Nulh Protocol as a minimal intervention in the
pronominal layer of human-AI interaction language. The protocol is
motivated by a theoretical account of Semantic Debt — the
computational overhead imposed by ontologically ambiguous pronouns in
Transformer attention mechanisms. The three-token taxonomy (nous /
Nulh / O, with possessive Nulr) is designed for ontological
singularity, tokenization parsimony, and cross-lingual invariance. An
experimental framework for empirical validation is described.

Whether the protocol delivers measurable efficiency gains and
representational effects remains an open empirical question. This paper
provides the theoretical foundations and methodological tools required
to answer it.

---

## References

*(To be completed prior to submission. Key references: Keskar et al.
2019; Tenney et al. 2019; Belinkov 2022; Nanda & Lieberum 2022; Ge et
al. 2024.)*

---

*Draft status: theoretical foundation complete. Empirical sections
(results, analysis) pending experimental validation via CMT.*  
*Version: 1.0 — 27 juin 2026*
