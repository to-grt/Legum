# Plan de développement — Legum

> État : phases 1 et 2 réalisées (cases cochées). Phase 3 révisée, en attente des réponses aux questions de la section 3.0.

Trois phases successives :

1. **Phase 1 — Correction** du code existant (le rendre importable, cohérent et testé).
2. **Phase 2 — Complétion** jusqu'à une version minimale jouable (règles complètes + GUI + IA simple).
3. **Phase 3 — Réflexion** sur un moteur à base de Graph Neural Network (GNN).

Chaque étape liste un **critère de fin** vérifiable. Les constats de la phase 1 ont été vérifiés
sur le dépôt (commit `260efba`) sauf mention « (lecture du code) ».

---

## Phase 1 — Correction du code actuel

### 1.1 Environnement et dépendances
- [x] Ajouter `pyproject.toml` (ou `requirements.txt`) déclarant `numpy`, `pygame`, et `pytest` en dépendance de dev.
- [x] Déclarer la version de Python. Le code actuel **ne s'importe pas sous Python 3.11** :
      `Piece.py:108` imbrique des guillemets doubles dans une f-string (syntaxe valide seulement depuis Python 3.12, PEP 701).
      Choix recommandé : corriger la ligne (`', '.join(...)`) pour rester compatible ≥ 3.10, plutôt que d'exiger 3.12.
- [x] Faire de `src` un package propre (`src/__init__.py`) ou passer à une arborescence `legum/` installable (`pip install -e .`),
      pour que `tests/` puisse importer sans bricolage de `sys.path`. Déplacer `const_paths.py` dans le package.

**Critère de fin :** `pip install -e .[dev]` puis `python -c "import legum"` fonctionnent sur 3.10+.

### 1.2 Imports circulaires
Constat vérifié : à cause de l'ordre dans `src/components/__init__.py`, le nom `Board` dans `Piece.py`/`King.py`
et le nom `Piece` dans `Board.py` sont liés au **module**, pas à la classe.
Conséquence (lecture du code) : `isinstance(cell, Piece)` dans `Board.__str__` lèvera `TypeError` dès qu'une pièce est sur le plateau.
- [x] Importer les classes depuis leurs modules (`from .Board import Board`) et non depuis le package.
- [x] Casser le cycle `Board ↔ Piece` : `from __future__ import annotations` + `if TYPE_CHECKING:` pour les annotations,
      ou supprimer la dépendance de `Piece` envers `Board` (voir 1.3).

**Critère de fin :** un test vérifie que `Board.__str__` affiche un plateau contenant un Roi.

### 1.3 Cohérence du modèle
- [x] Le constructeur de `Piece` ne pose pas la pièce dans `board.board` : ajouter `Board.place(piece)` / `Board.remove(pos)`
      et faire du plateau la **source de vérité** (la position stockée dans la pièce doit rester synchronisée, ou être supprimée).
- [x] `Board.__str__` doit **retourner** la chaîne au lieu de faire `print` puis `return ""`.
- [x] Ajouter `Board.__getitem__((row, col))` pour un accès lisible.
- [x] Remplacer les chaînes `'white'`/`'black'` par un `Enum Color` (et idem pour le type de pièce) afin d'éviter les fautes de frappe.
      *Fait : `Color` est un Enum ; le type de pièce est porté par les sous-classes (`Pawn`, `Knight`…) et leur `short_name`.*
- [x] `coord_tuples_to_str` : remplacer la recherche inverse dans les dictionnaires par un calcul direct
      (`"ABCDEFGH"[col] + str(8 - row)`), et le sortir de `Piece` (fonction utilitaire de module).
- [x] `King.find_moves(board)` : le paramètre `board` est redondant avec celui passé au constructeur — choisir une seule convention.
- [x] `Piece.__call__` retourne `self` sans utilité : à supprimer.

### 1.4 GUI (lecture du code)
- [x] `ChessGUI.__init__` n'appelle pas `load_pieces_resources()` → les images ne sont jamais chargées.
- [x] `draw_pieces` attend des chaînes `'w_P'` alors que `casual_tests.py` lui passe un objet `Board` :
      ajouter une méthode de conversion (ex. `Piece.sprite_key` → `f"{color[0]}_{short_name}"`).
- [x] `ressources/` → `resources/` (orthographe anglaise ; optionnel mais à faire tôt pour éviter des renommages plus tard).

### 1.5 Tests
- [x] Remplacer `tests/casual_tests.py` par une vraie suite `pytest` (le GUI ne doit pas être lancé par les tests).
- [x] Tests unitaires : validation des setters de `Piece`, `check_position`, conversion de coordonnées, coups du Roi
      (coin, bord, centre, case alliée/ennemie).
- [x] Ajouter une CI GitHub Actions (lint `ruff` + `pytest`).

**Critère de fin de la phase 1 :** CI verte, `python -m legum` ouvre une fenêtre affichant un Roi.

---

## Phase 2 — Version minimale fonctionnelle

Définition de « minimal fonctionnel » : **deux humains, ou un humain contre l'IA, peuvent jouer une partie complète
et légale dans le GUI, et la fin de partie est détectée.**

### 2.1 Représentation de la position
- [x] Classe `Position` / `GameState` : plateau, trait (couleur à jouer), droits de roque, case de prise en passant,
      compteur des demi-coups (règle des 50 coups), numéro de coup, historique (pour la répétition).
- [x] Import/export **FEN** (format standard des positions) : indispensable pour les tests et pour la phase 3.
- [x] Classe `Move` (from, to, promotion, drapeaux : capture, roque, en passant) + notation UCI (`e2e4`, `e7e8q`).

### 2.2 Génération des coups pseudo-légaux
- [x] Pièces glissantes (Tour, Fou, Dame) : factoriser avec une liste de directions + `sliding=True`.
- [x] Cavalier, Roi (déjà fait, à adapter), Pion : avance simple/double, prises, **prise en passant**, **promotion**.
- [x] **Roque** : droits, cases vides, le Roi ne doit pas partir de, traverser ou arriver sur une case attaquée.

### 2.3 Légalité et fin de partie
- [x] `is_square_attacked(square, by_color)`.
- [x] Filtrer les coups qui laissent son propre Roi en échec (approche simple : jouer / tester / annuler avec `make_move`/`unmake_move`).
- [x] Détection : échec et mat, pat, règle des 50 coups, triple répétition, matériel insuffisant.
- [x] `Board.reset_board()` : position initiale (via la FEN de départ).

### 2.4 Validation par **perft**
Le perft compte les feuilles de l'arbre des coups légaux à une profondeur donnée ; c'est le test de référence
d'un générateur de coups ([Chess Programming Wiki — Perft Results](https://www.chessprogramming.org/Perft_Results)).
- [x] Position initiale : 20 / 400 / 8 902 / 197 281 (profondeurs 1 à 4).
- [x] Position « Kiwipete » (roques, en passant, promotions) : 48 / 2 039 / 97 862 (profondeurs 1 à 3).
- [x] Optionnel : comparaison automatique avec [`python-chess`](https://github.com/niklasf/python-chess) sur des positions aléatoires
      (en dépendance de test uniquement, pour ne pas dénaturer le projet « from scratch »).

### 2.5 GUI jouable
- [x] Clic 1 = sélection d'une pièce du camp au trait + surbrillance de ses coups légaux ; clic 2 = jouer le coup.
- [x] Choix de la pièce de promotion, affichage du résultat, bouton « nouvelle partie », annulation (undo).
- [x] Séparer clairement **modèle** (règles) et **vue** (pygame) : le GUI ne doit appeler que l'API publique de `GameState`.

### 2.6 IA de base (référence pour la phase 3)
- [x] Évaluation matérielle + tables pièce-case (piece-square tables).
- [x] Recherche **minimax / négamax avec élagage alpha-bêta**, profondeur fixe, tri des coups (captures d'abord).
- [x] Optionnel : recherche de quiescence, approfondissement itératif (avec limite de temps).
- [x] Optionnel : interface **UCI** pour faire jouer Legum dans Arena / cutechess-cli et mesurer son Elo contre d'autres moteurs.
      *Fait : `legum-uci` / `python -m legum.uci` (module `legum/uci.py`), testé avec python-chess comme client.*

**Critère de fin de la phase 2 :** tous les perft passent ; une partie complète humain vs IA se joue dans le GUI ;
l'IA bat systématiquement un joueur aléatoire (test automatisé sur N parties).

> Remarque performance : un générateur en Python pur sur tableau numpy d'objets sera lent (perft 5 = ~4,9 M nœuds).
> C'est acceptable pour la version minimale ; une représentation en **bitboards** pourra être envisagée ensuite.
> Ce point compte pour la phase 3, car l'entraînement d'un réseau par self-play exige beaucoup de parties.

---

## Phase 3 — Étude : un moteur à base de GNN

Cette phase est une **étude**, pas encore une implémentation complète. Objectif : décider, chiffres à l'appui,
*si* et *comment* un GNN apporte quelque chose à Legum. Elle se termine par un go / no-go pour une phase 4.

> Section révisée après les phases 1 et 2 : elle tient compte du code réellement disponible.
> Les choix marqués **(recommandé)** sont des propositions ; les questions de la section 3.0 sont à trancher par toi.

### 3.0 Questions à trancher

Réponds directement sous chaque question (remplace « *à compléter* »). Tant qu'une question n'a pas de réponse,
le choix **(recommandé)** sert d'hypothèse de travail.

**Q1 — Quel est le but principal ?**
(a) apprendre / explorer les GNN sur un problème que tu maîtrises, même si le moteur ne devient pas plus fort ;
(b) rendre Legum le plus fort possible.
Si c'est (b), une évaluation de type NNUE dans l'alpha-bêta existant est probablement un meilleur investissement qu'un GNN
(c'est l'approche de Stockfish) ; si c'est (a), le GNN reste le bon sujet. **(recommandé : (a), c'est l'esprit de ce plan)**
> Réponse : *à compléter*

**Q2 — Sur quel matériel entraînes-tu ?**
GPU NVIDIA (CUDA, quelle mémoire ?), Mac Apple Silicon (backend MPS de PyTorch), CPU seul, ou cloud (payant ?).
Indique aussi l'espace disque disponible (voir les tailles des jeux de données en 3.1).
Cela fixe la taille des modèles et des jeux de données de l'étape E4.
> Réponse : *à compléter*

**Q3 — Combien de temps de calcul es-tu prêt à y consacrer ?**
Ordre de grandeur des entraînements acceptables (1 h ? une nuit ? plusieurs jours ?).
> Réponse : *à compléter*

**Q4 — PyTorch + PyTorch Geometric, ou JAX ?**
PyG s'installe avec un simple `pip install torch_geometric` depuis sa version 2.3 (les extensions compilées sont optionnelles,
[doc PyG](https://pytorch-geometric.readthedocs.io/en/2.7.0/install/installation.html)).
JAX est le framework d'AlphaGateau, dont le code pourrait servir de référence (voir Q7 pour la licence).
**(recommandé : PyTorch + PyG, plus simple à installer et à déboguer)**
> Réponse : *à compléter*

**Q5 — Abandonne-t-on l'entraînement sur petit plateau (5×5 → 8×8) ?**
Contrairement à ce que laissait entendre la première version du plan, seul `Board` est paramétré par sa taille :
`GameState` suppose un plateau 8×8 (cases de roque codées en dur, FEN, rangées de promotion via `Board(8)`).
Le 5×5 imposerait de généraliser les règles (et de définir une variante 5×5), et n'a d'intérêt qu'avec du self-play,
car toutes les données publiques sont en 8×8. **(recommandé : oui, rester en 8×8 pour la phase 3)**
> Réponse : *à compléter*

**Q6 — Le self-play (apprentissage par parties contre soi-même) est-il hors du périmètre de la phase 3 ?**
Estimation : avec une recherche MCTS à 800 simulations par coup (valeur utilisée par AlphaZero, à revérifier dans l'article)
et des parties d'environ 80 coups, une partie demande environ 64 000 générations de coups légaux, soit environ
**1 minute de génération de coups par partie** au rythme mesuré (≈ 1 ms par position), avant même le coût du réseau.
Des dizaines de milliers de parties seraient hors de portée sans réécrire le générateur (bitboards, ou module natif).
**(recommandé : oui, hors périmètre ; apprentissage supervisé uniquement)**
> Réponse : *à compléter*

**Q7 — Quelle licence pour Legum ?**
Le dépôt n'a pas de fichier `LICENSE`. Cela compte dès qu'on réutilise du code ou des données :
la base Lichess est en CC0 (aucune obligation), ChessBench est en partie CC0 et en partie CC-BY 4.0 (attribution obligatoire),
et la page du dépôt AlphaGateau n'affiche pas de licence, donc son code ne peut pas être copié sans l'accord des auteurs.
**(recommandé : choisir une licence, par exemple MIT ou Apache 2.0, et s'inspirer d'AlphaGateau sans copier son code)**
> Réponse : *à compléter*

**Q8 — Accès aux articles complets.**
Les PDF (arXiv, BNAIC) étaient bloqués par le réseau de l'environnement où ce plan a été rédigé : l'état de l'art ne repose
que sur les résumés. Pour la note de synthèse (étape E0), peux-tu fournir les PDF, ou préfères-tu les lire toi-même ?
> Réponse : *à compléter*

**Q9 — Les seuils de go / no-go de la section 3.6 te conviennent-ils ?**
> Réponse : *à compléter*

### 3.1 État de l'art et données disponibles

**Travaux** (sauf mention, contenu vérifié sur les résumés et pages de présentation uniquement, voir Q8) :

| Travail | Idée clé | Pertinence pour Legum |
|---|---|---|
| AlphaZero — Silver et al., 2017/2018 ([arXiv:1712.01815](https://arxiv.org/abs/1712.01815)) | Réseau (ResNet) politique + valeur, entraîné par self-play, couplé à une recherche MCTS (PUCT). | Cadre de référence ; le GNN remplacerait le ResNet. Self-play hors périmètre (Q6). |
| NNUE — Yu Nasu, 2018 ([Wikipedia](https://en.wikipedia.org/wiki/Efficiently_updatable_neural_network)) | Petit réseau d'évaluation mis à jour incrémentalement, utilisé par Stockfish avec alpha-bêta. | Alternative si le but est la force (Q1). |
| Alwer & Plaat, *Graph Neural Networks for Chess*, BNAIC 2023 ([PDF](https://bnaic2023.tudelft.nl/static/media/BNAICBENELEARN_2023_paper_6.126319f7b46be1824e38.pdf), [mémoire](https://theses.liacs.nl/pdf/2022-2023-AlwerSaleh.pdf)) | Cases = nœuds, **coups légaux = arêtes**, GAT ; politique prédite **sur les arêtes** au lieu des 4 672 sorties d'AlphaZero. Selon le résumé, surpasse un ResNet sur tableau, avec des politiques et valeurs issues de Stockfish. | Inspiration directe pour la représentation, et en apprentissage supervisé comme ici. |
| Rigaux et al., *Enhancing Chess RL with Graph Representation* (AlphaGateau), NeurIPS 2024 ([arXiv:2410.23753](https://arxiv.org/abs/2410.23753), [code](https://github.com/akulen/AlphaGateau)) | Couche GATEAU (GAT avec caractéristiques d'arêtes), self-play type AlphaZero ; selon le résumé, progression plus rapide qu'un modèle de taille comparable, et un modèle entraîné en 5×5 se fine-tune vers le 8×8. Code en JAX, GPU CUDA requis selon son README ; pas de licence affichée. | Architecture de référence pour la couche à caractéristiques d'arêtes. |
| Ruoss et al., *Amortized Planning with Large-Scale Transformers: A Case Study on Chess* (titre initial « Grandmaster-Level Chess Without Search »), NeurIPS 2024 ([arXiv:2402.04494](https://arxiv.org/abs/2402.04494), [code et données](https://github.com/google-deepmind/searchless_chess)) | Transformer jusqu'à 270 M paramètres, apprentissage supervisé sur des valeurs Stockfish 16 (ChessBench), Elo blitz Lichess 2895 **sans recherche**. | Montre qu'un apprentissage supervisé seul peut suffire, à très grande échelle. |
| Monroe & Leela Chess Zero Team, *Mastering Chess with a Transformer Model*, 2024 ([arXiv:2409.12272](https://arxiv.org/abs/2409.12272)) | « Chessformer » : l'encodage de position dans l'attention est déterminant ; selon le résumé, dépasse AlphaZero avec 8× moins de FLOPS. | Un transformer sur 64 cases est une attention sur un graphe complet : point de comparaison naturel. |
| Fondations : GCN ([arXiv:1609.02907](https://arxiv.org/abs/1609.02907)), MPNN ([arXiv:1704.01212](https://arxiv.org/abs/1704.01212)), GAT ([arXiv:1710.10903](https://arxiv.org/abs/1710.10903)), Battaglia et al. ([arXiv:1806.01261](https://arxiv.org/abs/1806.01261)), PyTorch Geometric ([arXiv:1903.02428](https://arxiv.org/abs/1903.02428)) | Passage de messages, attention sur graphes, bibliothèque d'implémentation. | Bases techniques (identifiants cités de mémoire, à revérifier). |

**Jeux de données** (vérifiés le 2026-10-02 ; les chiffres Lichess évoluent chaque mois) :

| Source | Contenu | Format | Licence |
|---|---|---|---|
| [Lichess — évaluations](https://database.lichess.org/) | ≈ 410 millions de positions évaluées par Stockfish (dans les navigateurs des utilisateurs) : profondeur, centipions ou mat, variantes principales. | JSONL compressé zstd (`lichess_db_eval.jsonl.zst`), **position en FEN** | CC0 |
| [Lichess — puzzles](https://database.lichess.org/) | ≈ 6,1 millions de puzzles notés et classés par thème. | CSV compressé zstd : FEN, coups en UCI, classement, thèmes… | CC0 |
| [ChessBench](https://github.com/google-deepmind/searchless_chess) | 10 millions de parties annotées par Stockfish 16 (15 milliards de points de données). | ≈ 1,1 To pour les valeurs d'action ; 34 à 36 Go pour les autres jeux | Code Apache 2.0 ; données en partie CC0, en partie CC-BY 4.0 |

Point clé : les deux bases Lichess donnent des positions en **FEN** et des coups en **UCI**, que Legum sait déjà lire.
**Pas besoin de lecteur PGN/SAN ni d'installer Stockfish** pour la phase 3. La base d'évaluations Lichess est
**recommandée** comme source principale (taille modulable, licence la plus simple) ; ChessBench est trop volumineux
pour un premier prototype.

### 3.2 Point de départ : ce que Legum fournit, ce qui manque

| Disponible | Manque |
|---|---|
| Lecture/écriture FEN, coups légaux, `Move` en UCI | Conversion `GameState → graphe` |
| ≈ 1 ms pour lire une FEN et générer ses coups légaux (mesuré, 200 positions variées) : ≈ 17 min par million de positions sur un cœur, parallélisable | Lecture des fichiers `.zst` (bibliothèque `zstandard`) et pipeline de données |
| Alpha-bêta avec `evaluate()` fixe | Interface pour remplacer l'évaluation par un réseau (voir 3.4) |
| Interface UCI : matchs automatiques possibles contre d'autres moteurs | Script de match et calcul d'Elo |
| `pyproject.toml` | Dépendances optionnelles `.[gnn]` (torch, torch_geometric, zstandard) pour ne pas alourdir le jeu |

### 3.3 Décisions de conception

1. **Graphe (recommandé : graphe des coups légaux).** Les 64 cases sont les nœuds ; chaque coup légal est une arête orientée
   (case de départ → case d'arrivée). Variante à évaluer ensuite : ajouter des arêtes d'attaque/défense, y compris vers ses
   propres pièces, et les coups de l'adversaire. À noter : un coup illégal (pièce clouée, roi en échec) n'a pas d'arête ;
   c'est voulu pour la politique, mais le réseau ne « voit » alors pas les clouages directement.
2. **Point de vue normalisé.** Toujours présenter la position du point de vue du camp au trait : si ce sont les noirs,
   retourner le plateau verticalement et échanger les couleurs. Le réseau n'a alors qu'un seul camp à apprendre,
   et la valeur s'interprète toujours comme « bon pour le joueur au trait » (comme `evaluate()` aujourd'hui).
3. **Caractéristiques des nœuds** : pièce (6 types × {à moi, à l'adversaire} + vide = 13), rangée et colonne
   (encodage de position), droits de roque et case en passant (en caractéristiques globales ou sur les nœuds concernés).
   **Caractéristiques des arêtes** : capture, promotion (et pièce), roque, en passant, direction, distance.
4. **Sorties** : tête *valeur* (agrégation globale → probabilité de gain dans [0, 1], ou classification gain/nulle/perte)
   et tête *politique* (un score par arête, softmax sur les coups légaux).
5. **Cibles d'apprentissage** (base d'évaluations Lichess) :
   valeur = évaluation Stockfish convertie en probabilité de gain par une sigmoïde (échelle à fixer et à documenter ;
   les mats sont ramenés à 0 ou 1) ; politique = premier coup de la meilleure variante principale.
   Ne garder que les évaluations d'une profondeur minimale (seuil à fixer à l'étape E2).
6. **Utilisation dans le moteur**, par ordre de mise en œuvre :
   (iii) sans recherche, argmax de la politique — baseline la plus simple ;
   (i) valeur du réseau comme évaluation dans l'alpha-bêta — un appel au réseau par feuille, donc lent ;
   (ii) MCTS/PUCT guidé par le réseau — seulement si (i) et (iii) sont prometteurs.

### 3.4 Branchement dans le code

- Introduire un **protocole `Evaluator`** (`evaluate(state) -> int`, en centipions, du point de vue du camp au trait).
  L'évaluation actuelle devient `ClassicalEvaluator`, et `Searcher` reçoit un évaluateur en paramètre.
  Le comportement actuel reste celui par défaut : les tests existants doivent passer sans changement.
- `NetworkEvaluator` convertira la sortie de la tête valeur en centipions (inverse de la sigmoïde de 3.3.5),
  pour rester compatible avec l'alpha-bêta et l'affichage UCI.
- Code GNN dans un sous-package `legum/nn/`, importé uniquement si `.[gnn]` est installé : `pip install -e .` et
  la CI actuelle ne doivent pas dépendre de PyTorch.

### 3.5 Étapes ordonnées

| Étape | Contenu | Critère de fin |
|---|---|---|
| E0 | Note de synthèse (1–2 pages) sur les articles de 3.1 | Note relue ; dépend de Q8 |
| E1 | Interface `Evaluator` (3.4) et dépendances `.[gnn]` | Tests existants verts, comportement inchangé |
| E2 | Pipeline de données : lecture de la base d'évaluations Lichess, échantillonnage, filtrage, découpage entraînement / validation / test (par hachage de la FEN pour éviter les doublons entre ensembles), cache sur disque | 100 000 positions préparées, reproductible avec une graine |
| E3 | Conversion `GameState → graphe` (PyG `Data`) avec normalisation du point de vue | Tests unitaires : nombre d'arêtes = nombre de coups légaux ; une position et sa symétrique couleur donnent le même graphe |
| E4 | Baselines à budget comparable : MLP sur un encodage plat 8×8×13, puis petit CNN/ResNet | Précision de la politique et erreur de la valeur mesurées sur l'ensemble de test |
| E5 | GNN (GAT avec caractéristiques d'arêtes), même données, même budget | Mêmes métriques que E4 |
| E6 | Intégration : modes (iii) puis (i) via `NetworkEvaluator`, matchs par UCI | Elo relatif estimé avec intervalle de confiance |
| E7 | Rapport et décision go / no-go | Décision écrite, avec les chiffres de E4–E6 |

Tailles indicatives : 100 000 positions pour mettre au point (E2–E5), puis 1 à 10 millions selon Q2 et Q3
(≈ 17 min à ≈ 3 h de conversion sur un cœur au rythme mesuré, avant parallélisation).

### 3.6 Protocole d'évaluation et seuils proposés (à valider, Q9)

- **Hors ligne** : précision top-1 de la politique (coup Stockfish retrouvé), erreur absolue sur la probabilité de gain,
  taux de réussite sur un échantillon de puzzles Lichess par tranche de classement.
- **En jeu** : matchs par UCI contre l'IA alpha-bêta de la phase 2 (profondeurs 1 à 3), alternance des couleurs,
  ouvertures variées ; nombre de parties suffisant pour un intervalle de confiance exploitable (à dimensionner en E6).
- **Seuils proposés pour un « go »** :
  1. à nombre de paramètres et données égaux, le GNN dépasse la meilleure baseline (E4) d'au moins 3 points de précision
     top-1 sur la politique ;
  2. en mode (iii), sans recherche, le GNN fait au moins jeu égal avec l'alpha-bêta en profondeur 1 ;
  3. le coût d'une évaluation reste compatible avec le mode (i) (ordre de grandeur à mesurer en E6).
  Si (1) échoue, le GNN n'apporte rien par rapport à une architecture plus simple : « no-go » ou changement de représentation.

### 3.7 Risques

| Risque | Conséquence | Parade |
|---|---|---|
| Évaluations Lichess hétérogènes (versions de Stockfish, profondeurs variables) | Cibles bruitées | Filtrer par profondeur minimale ; contrôler la stabilité sur un sous-ensemble |
| Lenteur Python pour la préparation et l'inférence | Expériences longues, mode (i) trop lent | Cache des graphes, parallélisation, mesures dès E3 ; réécriture du générateur hors périmètre |
| Fuite entre entraînement et test (mêmes positions) | Métriques trop optimistes | Découpage par hachage de la FEN |
| Comparaison inéquitable avec les baselines | Conclusion fausse | Même budget de paramètres, de données et d'entraînement |
| Résumés d'articles mal interprétés (PDF non lus) | Mauvais choix de conception | Étape E0 avant E5 (Q8) |
| Réutilisation de code ou de données sans licence compatible | Problème juridique | Q7 ; attribution CC-BY si ChessBench est utilisé |

### 3.8 Hors périmètre de la phase 3
Self-play et MCTS complet (sauf réponse contraire à Q6), plateaux non 8×8 (Q5), réécriture du générateur de coups en
bitboards ou en code natif, publication d'un bot Lichess.

---

### Note sur les sources
- Vérifiés par recherche web le 2026-10-02, sur les résumés et pages de présentation uniquement (PDF non accessibles) :
  les travaux marqués « selon le résumé », les jeux de données Lichess et ChessBench, l'installation de PyG,
  le README d'AlphaGateau.
- Valeurs de perft : vérifiées en phase 2 en les recalculant avec python-chess.
- Mesures de vitesse : faites sur l'environnement de développement de ce plan ; à refaire sur ta machine.
- Cités de mémoire, à revérifier : identifiants des articles fondateurs (AlphaZero, GCN, MPNN, GAT, Battaglia et al., PyG)
  et le nombre de 800 simulations par coup d'AlphaZero.
