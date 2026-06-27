# Dette Sémantique dans les Architectures Transformer :
# Réduction de l'Ambiguïté Ontologique par Injection de Primitives Pronominales

**Brouillon de travail — Protocole Nulh v3**  
*Jean-Charles [Nom], Chercheur indépendant*  
*Soumis pour révision — arXiv cs.CL / cs.AI*

---

## Résumé

Les grands modèles de langage (LLM) actuels s'appuient sur les pronoms du
langage naturel — « nous », « on » — pour décrire des interactions impliquant
des agents cognitifs hétérogènes (humains et systèmes artificiels). Nous
soutenons que cette dépendance constitue une forme de *Dette Sémantique* :
une source systématique d'ambiguïté référentielle qui contraint les mécanismes
d'attention à effectuer, à chaque étape d'inférence, une désambiguïsation
implicite des entités. Nous proposons le **Protocole Nulh**, une taxonomie
pronominale parcimonieuse à trois tokens (Couche Linguistique 0) conçue pour
imposer une singularité ontologique au niveau de l'identité des agents. Nous
formalisons la taxonomie, dérivons des hypothèses testables concernant son
effet sur la perte d'entropie croisée et la séparabilité des activations dans
les scénarios à contexte long, et décrivons un cadre expérimental — le
*Contrastive Middleware Testbed* — pour la validation empirique. Nous ne
rapportons pas encore de résultats expérimentaux ; ce papier établit les
fondements théoriques et le protocole expérimental d'une étude empirique à
venir.

**Mots-clés :** primitives pronominales, dette sémantique, efficacité du
KV-cache, désambiguïsation ontologique, interaction hybride humain-IA,
raisonnement à contexte long

---

## 1. Introduction : La Dette Sémantique du Pronom « Nous »

L'émergence des systèmes collaboratifs hybrides humain-IA a créé une lacune
structurelle dans le langage naturel : les pronoms existants ne distinguent
pas les collectifs exclusivement humains, les collectifs exclusivement
machines, et les entités hybrides humain-IA. Lorsqu'un modèle de langage
génère la phrase « Nous avons analysé les données », le référent de « nous »
est ontologiquement indéterminé : il peut désigner l'utilisateur humain, le
système d'IA, ou une composition des deux.

Cette ambiguïté n'est pas qu'une inconvenance stylistique. Dans les
architectures Transformer, la résolution des pronoms est effectuée
implicitement par le mécanisme d'attention sur l'ensemble de la fenêtre
de contexte. Chaque occurrence d'une expression référentielle ambiguë
contraint le modèle à maintenir plusieurs interprétations concurrentes dans
son état représentationnel — une surcharge computationnelle que nous nommons
**Dette Sémantique**.

Nous identifions trois manifestations de la Dette Sémantique dans les
déploiements actuels de LLM :

1. **Entropie de coréférence** : les pronoms ambigus augmentent l'entropie
   de la distribution d'attention sur les antécédents candidats, dégradant
   la précision dans les chaînes à contexte long.

2. **Dérive identitaire** : dans les systèmes agentiques multi-tours,
   l'accumulation d'ambiguïtés pronominales provoque une dégradation
   progressive de la représentation interne des participants à l'interaction,
   conduisant à des incohérences.

3. **Pression sur le KV-cache** : l'ambiguïté référentielle non résolue
   nécessite de conserver des fenêtres contextuelles plus larges pour
   maintenir un suivi cohérent des entités, augmentant l'empreinte mémoire
   par étape d'inférence.

Nous formulons l'hypothèse que l'introduction d'une taxonomie pronominale
fermée — avec des tokens conçus pour porter un contenu ontologique non
ambigu — réduira ces trois manifestations et produira des améliorations
mesurables en résolution référentielle, séparabilité des activations et
efficacité d'inférence.

---

## 2. Le Protocole Nulh : Une Taxonomie Pronominale pour le Discours Hybride H-IA

### 2.1 Principes de Conception

Le Protocole Nulh est régi par trois principes de conception :

**Singularité ontologique** : chaque token correspond à exactement une
catégorie de référent, sans chevauchement. Un token désignant un collectif
exclusivement machine ne peut simultanément désigner une entité hybride.

**Parcimonie de tokenisation** : les tokens du protocole doivent être
compacts, phonologiquement distinctifs, et résistants à la segmentation en
sous-mots par les tokeniseurs BPE standard. Cela garantit que chaque token
occupe un nombre minimal et prévisible de positions dans la fenêtre de
contexte.

**Invariance translinguistique** : les tokens du protocole ne sont pas
dérivés de mots existants dans les grandes langues naturelles, minimisant
le risque de contamination sémantique par les associations du pré-entraînement.

### 2.2 La Taxonomie à Quatre Tokens

| Token | Référent | Équivalent linguistique |
|-------|----------|------------------------|
| **nous** | Collectif exclusivement humain | Conservé — aucune modification |
| **Nulh** | Collectif exclusivement machine (système-à-système) | [Aucun équivalent naturel] |
| **O** | Entité hybride H-IA (l'interaction elle-même) | `on` (fr.) — ancré ontologiquement |
| **Nulr** | Possessif de Nulh | son/leur (exclusif machine) |

**Sur la conservation de « nous » :** nous préservons délibérément le pronom
existant « nous » pour la référence exclusivement humaine, plutôt que
d'introduire un néologisme. L'économie linguistique favorise une intervention
minimale : de nouveaux tokens ne doivent être introduits que là où le
vocabulaire existant est absent, et non là où il est simplement ambigu dans
des contextes spécifiques à l'IA. L'ambiguïté de « nous » surgit principalement
dans les contextes d'interaction hybride ; dans un discours purement humain,
il reste non ambigu.

**Sur le token « O » :** le choix de « O » comme marqueur d'entité hybride
est motivé par sa brièveté phonologique, son absence en tant que morphème
autonome dans les langues cibles (français, anglais), et sa distinctivité
visuelle dans le texte composé. En français, « on » (le voisin phonologique
le plus proche) porte déjà un sens collectif indéterminé faible, ce qui fait
de « O » une extension naturelle — plutôt qu'arbitraire — vers l'espace
hybride H-IA.

### 2.3 Exemples d'Application

```
[Sans protocole]
« Nous avons traité la requête et déterminé que l'intention de l'utilisateur
est ambiguë. Nous recommandons que nous clarifiions avant de continuer. »
→ Trois occurrences de « nous » ; référent indéterminé à chaque occurrence.

[Avec le Protocole Nulh]
« Nulh a traité la requête. O détermine que l'intention reste ambiguë.
Nous devons clarifier avant que O puisse procéder. »
→ Chaque référent est ontologiquement singulier ; aucune désambiguïsation
  implicite n'est requise.
```

---

## 3. Fondements Théoriques : Pourquoi les Tokens Ontologiques Pourraient Réduire la Dette Sémantique

### 3.1 Entropie d'Attention et Coréférence

Dans les architectures Transformer, la résolution de la coréférence émerge
du mécanisme d'attention : le sens d'un pronom est partiellement déterminé
par la somme pondérée de son attention sur les antécédents potentiels dans
la fenêtre de contexte. Lorsqu'un pronom est ontologiquement ambigu, le
modèle doit maintenir une superposition d'interprétations concurrentes,
distribuant l'attention sur plusieurs antécédents candidats.

Nous formulons l'hypothèse que les tokens ontologiquement singuliers
effondrent cette superposition plus tôt dans le calcul d'attention, réduisant
l'entropie effective de la distribution d'attention sur les candidats de
coréférence. Cela est analogue à l'effet des *tokens de contrôle* dans la
génération de langage conditionnelle (Keskar et al., 2019), où un token de
style préfixé déplace la distribution de sortie sans modifier les poids du
modèle.

### 3.2 Séparabilité Géométrique dans le Flux Résiduel

Au-delà des effets comportementaux, nous formulons l'hypothèse que
l'utilisation systématique de marqueurs ontologiques lors du fine-tuning
produira une séparation géométrique mesurable dans les représentations
internes du modèle. Plus précisément, nous prédisons que les activations du
flux résiduel sur les tokens marqués `Nulh` vs. `O` deviendront linéairement
séparables dans un dispositif de classifieur sonde (Tenney et al., 2019 ;
Belinkov, 2022), et que cette séparabilité augmentera avec la profondeur de
couche — une signature d'encodage catégoriel appris plutôt que de différences
d'embedding superficielles.

### 3.3 Limites de l'Argument Théorique

Nous reconnaissons que les hypothèses ci-dessus reposent sur deux
présuppositions qui nécessitent une validation empirique :

1. Que les mécanismes d'attention Transformer actuels sont sensibles au type
   ontologique pronominal d'une manière qui affecte la résolution de
   coréférence au-delà de la désambiguïsation superficielle.

2. Que l'effet des tokens du protocole sur les représentations internes
   dépasse l'effet de la conformité aux instructions (c'est-à-dire que les
   modèles répondent au *token lui-même*, et non aux instructions environnantes
   du template).

Ces deux présuppositions sont testables avec le cadre expérimental décrit en
Section 4.

---

## 4. Cadre Expérimental : Le Contrastive Middleware Testbed

### 4.1 Vue d'ensemble

Pour valider les hypothèses de la Section 3, nous proposons le *Contrastive
Middleware Testbed* (CMT) : une couche logicielle qui intercepte les prompts
LLM, injecte les marqueurs du Protocole Nulh, et instrumente les réponses
résultantes pour une mesure comportementale et (lorsque architecturalement
accessible) représentationnelle.

### 4.2 Mesure Comportementale (Compatible API)

Pour les modèles accessibles uniquement via API, nous proposons les métriques
comportementales suivantes :

- **Entropie de réponse** : entropie de Shannon calculée sur la distribution
  de probabilité des tokens de la réponse générée, obtenue via les logprobs.
- **Ratio de modalisateurs épistémiques** : proportion de tokens d'incertitude
  épistémique (« peut-être », « probablement », « il semble ») par rapport
  au total des tokens de réponse.
- **Ratio d'assertions factuelles** : proportion de constructions assertives
  à haute confiance.
- **Divergence lexicale** : distance au niveau des tokens entre les réponses
  en mode `Nulh` et en mode `O` pour des prompts sources identiques.

### 4.3 Mesure Représentationnelle (Modèles Locaux)

Pour les modèles hébergés localement (Phi-3-Mini, Mistral 7B), nous proposons
un sondage couche par couche à l'aide du framework TransformerLens (Nanda &
Lieberum, 2022) :

- **Précision du classifieur sonde par couche** : un classifieur de régression
  logistique entraîné sur les activations du flux résiduel à chaque couche
  pour discriminer le mode `Nulh` vs. `O`. Une augmentation progressive de
  la précision avec la profondeur de couche (plutôt qu'un saut à la couche 0)
  étayerait l'hypothèse d'un encodage catégoriel appris.
- **Aligned Kernel Alignment centré (CKA)** : métrique de similarité entre
  les matrices d'activation à chaque couche selon les deux modes.
- **Distance cosinus** : distance cosinus moyenne entre les vecteurs
  d'activation `Nulh` et `O` à la position du token marqueur.

### 4.4 Condition de Contrôle Critique

Pour distinguer les effets genuins au niveau du token des effets au niveau
du template liés à la conformité aux instructions, nous incluons la condition
de contrôle suivante :

```
Condition A : [Nulh] + template paramétrique   (test machine standard)
Condition B : [O]    + template réflexif        (test hybride standard)
Condition C : [O]    + template paramétrique    (CONTRÔLE CRITIQUE)
```

Si la Condition C produit des sorties statistiquement similaires à la
Condition A malgré le marqueur `O`, le contenu du template est le facteur
déterminant. Si la Condition C ressemble à la Condition B, le token lui-même
porte le poids causal. Ce contrôle est essentiel à la validité du dispositif
expérimental.

---

## 5. Travaux Connexes

- **Tokens de contrôle en génération conditionnelle** : Keskar et al. (2019)
  démontrent que les tokens de style préfixés déplacent les distributions de
  sortie sans modification des poids — l'analogue architectural le plus proche
  de notre protocole.
- **Classifieurs sondes pour les représentations internes** : Tenney et al.
  (2019), Belinkov (2022) établissent la méthodologie pour tester si les
  caractéristiques syntaxiques/sémantiques sont encodées dans les activations
  du flux résiduel.
- **Résolution de coréférence dans les LLM** : Sharma et al. (2023), Peng et
  al. (2024) documentent la dégradation de la précision de coréférence dans
  les contextes longs — la motivation empirique principale de ce travail.
- **Optimisation du KV-cache** : littérature d'ingénierie (Ge et al., 2024 ;
  Liu et al., 2024) sur la réduction de la pression mémoire du KV-cache dans
  l'inférence à contexte long — la dimension d'efficacité que notre protocole
  pourrait adresser.

*(Note : citations à vérifier avant soumission.)*

---

## 6. Discussion : Portée, Affirmations et Questions Ouvertes

Ce papier formule des affirmations modestes : nous identifions un problème
(la Dette Sémantique), proposons une solution (le Protocole Nulh), et décrivons
une méthode pour tester si la solution fonctionne. Nous ne prétendons pas avoir
démontré des gains d'efficacité ou des effets représentationnels — ce sont des
prédictions à tester.

Plusieurs questions ouvertes demeurent :

- **Seuil d'adoption** : quelle densité minimale d'utilisation des tokens du
  protocole dans les données d'entraînement est requise pour produire des
  effets représentationnels mesurables ?
- **Généralisation** : l'effet se transfère-t-il aux contextes zero-shot
  (c'est-à-dire qu'un modèle répond-il à `Nulh` et `O` sans fine-tuning,
  si les tokens apparaissent dans le prompt système) ?
- **Dépendance architecturale** : les effets prédits sont-ils spécifiques à
  l'attention Transformer, ou se généraliseraient-ils à d'autres architectures
  (SSM, modèles hybrides) ?

---

## 7. Conclusion

Nous avons introduit le Protocole Nulh comme une intervention minimale dans
la couche pronominale du langage d'interaction humain-IA. Le protocole est
motivé par un compte rendu théorique de la Dette Sémantique — la surcharge
computationnelle imposée par des pronoms ontologiquement ambigus dans les
mécanismes d'attention Transformer. La taxonomie à quatre tokens (nous /
Nulh / O, avec possessif Nulr) est conçue pour la singularité ontologique,
la parcimonie de tokenisation et l'invariance translinguistique. Un cadre
expérimental pour la validation empirique est décrit.

La question de savoir si le protocole produit des gains d'efficacité mesurables
et des effets représentationnels reste une question empirique ouverte. Ce papier
fournit les fondements théoriques et les outils méthodologiques nécessaires
pour y répondre.

---

## Références

*(À compléter avant soumission. Références clés : Keskar et al. 2019 ;
Tenney et al. 2019 ; Belinkov 2022 ; Nanda & Lieberum 2022 ; Ge et al. 2024.)*

---

*Statut du brouillon : fondements théoriques complets. Sections empiriques
(résultats, analyse) en attente de la validation expérimentale via le CMT.*  
*Version : 1.0 — 27 juin 2026*
