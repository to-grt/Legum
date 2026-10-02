# Plan de développement — Legum

> État : phases 1 et 2 réalisées (cases cochées). La phase 3 reste à mener.

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
- [ ] Optionnel : interface **UCI** pour faire jouer Legum dans Arena / cutechess-cli et mesurer son Elo contre d'autres moteurs.

**Critère de fin de la phase 2 :** tous les perft passent ; une partie complète humain vs IA se joue dans le GUI ;
l'IA bat systématiquement un joueur aléatoire (test automatisé sur N parties).

> Remarque performance : un générateur en Python pur sur tableau numpy d'objets sera lent (perft 5 = ~4,9 M nœuds).
> C'est acceptable pour la version minimale ; une représentation en **bitboards** pourra être envisagée ensuite.
> Ce point compte pour la phase 3, car l'entraînement d'un réseau par self-play exige beaucoup de parties.

---

## Phase 3 — Réflexion : un moteur à base de GNN

Cette phase est une **étude**, pas encore une implémentation. Objectif : décider *si* et *comment* un GNN apporte
quelque chose à Legum, en s'appuyant sur l'existant.

### 3.1 État de l'art (à lire en premier)
| Travail | Idée clé | Pertinence pour Legum |
|---|---|---|
| AlphaZero — Silver et al., 2017/2018 ([arXiv:1712.01815](https://arxiv.org/abs/1712.01815)) | Réseau (ResNet) politique + valeur, entraîné par self-play, couplé à une recherche MCTS (PUCT). | Cadre d'entraînement de référence ; le GNN remplacerait le ResNet. |
| NNUE — Yu Nasu, 2018 ([Wikipedia](https://en.wikipedia.org/wiki/Efficiently_updatable_neural_network)) | Petit réseau d'évaluation mis à jour incrémentalement, utilisé par Stockfish avec alpha-bêta. | Alternative pragmatique : réseau d'évaluation + alpha-bêta de la phase 2. |
| Alwer & Plaat, *Graph Neural Networks for Chess*, BNAIC 2023 ([PDF](https://bnaic2023.tudelft.nl/static/media/BNAICBENELEARN_2023_paper_6.126319f7b46be1824e38.pdf), [mémoire](https://theses.liacs.nl/pdf/2022-2023-AlwerSaleh.pdf)) | Cases = nœuds, **coups légaux = arêtes**, GAT ; politique prédite **sur les arêtes** au lieu des 4 672 sorties d'AlphaZero. Selon le résumé, surpasse un ResNet sur tableau. | Inspiration directe pour la représentation. |
| Rigaux et al., *Enhancing Chess RL with Graph Representation* (AlphaGateau), NeurIPS 2024 ([arXiv:2410.23753](https://arxiv.org/abs/2410.23753), [code](https://github.com/akulen/AlphaGateau)) | Couche GATEAU (GAT avec caractéristiques d'arêtes), self-play type AlphaZero ; selon le résumé, progression plus rapide qu'un modèle de taille comparable, et un modèle entraîné en **5×5** se fine-tune vers le 8×8. | Très pertinent : `Board(board_size)` est déjà paramétré, on peut entraîner d'abord sur un petit plateau. |
| Ruoss et al., *Amortized Planning with Large-Scale Transformers: A Case Study on Chess* (titre initial « Grandmaster-Level Chess Without Search »), NeurIPS 2024 ([arXiv:2402.04494](https://arxiv.org/abs/2402.04494)) | Transformer jusqu'à 270 M paramètres, apprentissage supervisé sur valeurs Stockfish 16 (jeu ChessBench), Elo blitz Lichess 2895 **sans recherche**. | Montre qu'un apprentissage supervisé seul peut suffire ; ChessBench est réutilisable. |
| Monroe & Leela Chess Zero Team, *Mastering Chess with a Transformer Model*, 2024 ([arXiv:2409.12272](https://arxiv.org/abs/2409.12272)) | « Chessformer » : l'encodage de position dans l'attention est déterminant ; selon le résumé, dépasse AlphaZero avec 8× moins de FLOPS. | Un transformer sur 64 cases est une attention sur un graphe complet : point de comparaison naturel avec un GNN. |
| Fondations GNN : GCN ([arXiv:1609.02907](https://arxiv.org/abs/1609.02907)), MPNN ([arXiv:1704.01212](https://arxiv.org/abs/1704.01212)), GAT ([arXiv:1710.10903](https://arxiv.org/abs/1710.10903)), Battaglia et al. ([arXiv:1806.01261](https://arxiv.org/abs/1806.01261)), PyTorch Geometric ([arXiv:1903.02428](https://arxiv.org/abs/1903.02428)) | Formalisme du passage de messages, attention sur graphes, bibliothèque d'implémentation. | Bases techniques. |

### 3.2 Questions de conception à trancher
1. **Quel graphe ?**
   - (a) Grille fixe : 64 nœuds, arêtes = adjacence géométrique (ou lignes/diagonales/sauts de cavalier).
     Simple, mais proche d'un CNN et peu d'avantage attendu.
   - (b) Graphe des coups légaux (Alwer & Plaat ; AlphaGateau) : arêtes = coups → la politique est un score par arête,
     et le graphe dépend de la position. **Option recommandée comme point de départ.**
   - (c) Ajouter des arêtes d'attaque/défense (y compris sur ses propres pièces) : plus d'information tactique, plus coûteux.
2. **Caractéristiques des nœuds** : pièce (one-hot 12 + vide), couleur relative au trait, droits de roque, en passant, rang/colonne (encodage de position).
   **Caractéristiques des arêtes** : type de coup (capture, promotion, roque), direction, distance.
3. **Sorties** : tête *valeur* (pooling global → scalaire dans [-1, 1] ou classification gain/nulle/perte)
   et tête *politique* (softmax sur les arêtes-coups légaux).
4. **Utilisation dans le moteur** :
   - (i) évaluation dans l'alpha-bêta de la phase 2 (coûteux : un appel au réseau par feuille) ;
   - (ii) MCTS/PUCT à la AlphaZero (moins de nœuds, le réseau guide la recherche) ;
   - (iii) sans recherche (prendre l'argmax de la politique) : baseline facile à mesurer.
5. **Apprentissage** :
   - Supervisé d'abord : positions issues de la [base Lichess](https://database.lichess.org/) (parties PGN publiques)
     ou de ChessBench, étiquetées par une évaluation Stockfish. Rapide pour valider l'architecture.
   - Self-play ensuite (AlphaZero/AlphaGateau) : beaucoup plus coûteux en calcul ; exige un générateur de coups rapide
     (cf. remarque performance de la phase 2).
   - Curriculum par taille de plateau (5×5 → 8×8), comme exploré par AlphaGateau.
6. **Outils** : PyTorch + PyTorch Geometric (ou JAX, utilisé par AlphaGateau).

### 3.3 Protocole d'évaluation
- Métriques hors ligne : précision top-1 de la politique, erreur sur la valeur, taux de réussite sur des puzzles Lichess.
- Métriques en jeu : matchs contre l'IA alpha-bêta de la phase 2 et contre Stockfish bridé (via UCI + cutechess-cli),
  estimation d'Elo avec intervalles de confiance.
- **Baselines indispensables** à budget égal (paramètres, données, calcul) : MLP sur un encodage plat, petit ResNet type AlphaZero.
  Le GNN n'a d'intérêt que s'il fait mieux qu'elles.

### 3.4 Livrables de la phase 3
- [ ] Note de synthèse (1–2 pages) sur les articles ci-dessus.
- [ ] Décision argumentée sur : type de graphe, architecture, mode d'utilisation (i/ii/iii), stratégie d'entraînement.
- [ ] Prototype de conversion `GameState → graphe` (PyG `Data`) + test unitaire.
- [ ] Expérience minimale : entraînement supervisé sur un petit jeu de positions, comparé à la baseline MLP.
- [ ] Go / no-go pour une phase 4 (implémentation complète du moteur GNN).

---

### Note sur les sources
Les références de la phase 3 marquées « selon le résumé » ont été vérifiées par recherche web pendant la rédaction de ce plan,
à partir des résumés et des pages de présentation, pas des articles complets (accès aux PDF bloqué par le réseau du moment).
Les références fondatrices (AlphaZero, GCN, MPNN, GAT, Battaglia et al., PyG) et les valeurs de perft sont des références
standard citées de mémoire : leurs identifiants sont à revérifier lors de la lecture.
