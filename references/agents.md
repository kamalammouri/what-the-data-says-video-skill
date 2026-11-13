# Agents : 8 rôles, dont 6 agents déjà installés

L'ancien format lançait une quinzaine d'agents par vidéo et six passes de contrôle. Ici, **l'orchestrateur (la session qui tient le skill) lance lui-même les scripts** (notation des sujets, voix, Flow, montage, mixage, miniature, lints, mesure) : un script ne se délègue pas. Un agent n'intervient que là où il faut une recherche sur le web, une écriture longue ou un regard qui n'est pas celui de l'auteur.

Les agents installés (`~/.claude/agents/`) se lancent par leur nom avec l'outil Agent (`subagent_type`) ; leur définition contient déjà leur méthode et leur format de sortie : **le brief ne la recopie pas**, il donne les fichiers, les règles propres à ce format et ce qui prime sur leurs réglages par défaut. Un agent ne voit pas la conversation : tout ce dont il a besoin est dans le brief, en chemins absolus.

## Modèle de chaque agent (demande de l'utilisateur du 11 novembre 2026 : ne pas consommer trop de tokens)

- Les 6 agents installés gardent le modèle de leur définition : `story-architect`, `fact-checker`, `image-qc`, `seo-metadata-editor` sur Sonnet ; `packaging-strategist`, `visual-director` sur Haiku. Ne pas passer de `model` plus cher.
- Les 2 agents `general-purpose` (rédacteur, imagier) héritent sinon du modèle de la session : **toujours les lancer avec `model: "opus"`** dans l'appel à l'outil Agent, jamais avec le modèle de la session s'il est plus cher.
- Aucun agent en `fork` (il recopie tout le contexte de la session) ; un brief court qui donne des chemins de fichiers, pas leur contenu.

## Tableau d'orchestration

| Étape | Agent | Entrée | Sortie | Porte de sortie (sinon on relance) |
|---|---|---|---|---|
| 1. Sujet | orchestrateur | `sujets.md`, `channel-results.md`, `keywords.py` | tableau candidat / a / b / c / total, `keywords.md` | l'utilisateur choisit ; titre validé par `ypp_lint.py --title` |
| 2. Angle | **`story-architect`** | sujet, titre, `structure-ecriture.md`, vidéos déjà publiées | 3 angles | l'utilisateur en choisit un ; `brief.json` avec `validated_by_user: true` |
| 3. Faits | **`fact-checker`** (sur l'angle) | l'angle choisi | `PASS` ou la liste des corrections, chacune avec sa source | 6 jeux de données et 4 à 7 sources sans `[to verify]`, écrits dans `facts.md` |
| 4. Script | **rédacteur** (`general-purpose`) | `brief.json`, `facts.md`, `structure-ecriture.md`, scripts publiés | `script.md` | `script_lint.py` : 0 erreur |
| 4 bis. Vérification | **`fact-checker`** (sur le script) | `script.md`, `facts.md` | tableau phrase / verdict / correction / source | aucune ligne `corrected` ou `unverifiable` restante ; `script_lint.py` toujours à 0 |
| 5. Voix | orchestrateur (`tts.py`), en parallèle de 6 | `shots_voice.json`, `brief.json`, `.env` | `voice.wav`, `timing.json` | 165 à 175 mots/min, aucun clip manquant |
| 6. Shot list | **imagier** (`general-purpose`), puis **`visual-director`** une fois | `script.md`, `images-flow.md`, `make_shots.py` | `make_shots.py` rempli, `shots.json`, `prompts.json` | `prompts.py --strict` : 0 erreur ; 70 à 85 images |
| 7. Images | orchestrateur (`flow_loop.sh`), **`image-qc`** en 2 passes | planches, `shots.json`, phrase `qc` | liste des rejets avec prompt réécrit | 0 rejet après la passe 2, ou image remplacée par `R(...)` / `D(...)` |
| 8. Montage, son | orchestrateur (`hf_build.py`, rendu, mixage) | tout ce qui précède, `music.mp3` | `out.mp4`, `short.mp4`, `chapters.md` | `check` ok ; `analyze_video.py` : `gate … OK` |
| 9. Emballage | **`packaging-strategist`** et **`seo-metadata-editor`** en parallèle, pendant le rendu | titre, `script.md`, `chapters.md`, `keywords.md` | scènes et texte de miniature, noms de chapitres ; `desc.txt`, `tags.txt`, `short_desc.txt` | `meta_lint.py` de l'agent sans refus ; `ypp_lint.py` : 0 erreur ; miniatures regardées |
| 10. Mesure | orchestrateur (`studio.mjs`) à J+2 et J+7 | Studio | une ligne dans `channel-results.md` | décision écrite (`mesure.md` §2) |

`character-designer` n'est pas utilisé : la troupe est fixe (`images-flow.md` §1).

## Briefs (à compléter, en chemins absolus)

### story-architect (étape 2)
```
Format : vidéo YouTube de 12 minutes « Do [Women/Men] Really [X]? What the Data Says » pour la chaîne The Hidden Bargain
(hommes américains de 25 à 65 ans). Lis <skill>/references/structure-ecriture.md : c'est la structure imposée.
Le titre est fixé et identique pour les trois angles : « [TITRE] ». Sujet : [SUJET]. Déjà publié : [LISTE].
Dans ton format habituel, donne pour chaque angle : hook = la scène d'ouverture en deux lignes à la 2ᵉ personne, suivie de
la question du titre mot pour mot ; les « temps forts » = les SIX jeux de données dans l'ordre des blocs (qui, année,
échantillon, le chiffre), le premier chiffre qui répond en partie avant 1:00 et le renversement au bloc 4 ; motif = la scène
d'ouverture et ce qu'elle veut dire à la fin ; twist = la réponse honnête en une phrase (préférence individuelle contre
biais social) ; à la place du costume : l'objet qui dit le sujet sur la miniature.
Chaque chiffre porte sa source avec un lien, sinon [to verify]. Le premier chiffre et le renversement du bloc 4 viennent
obligatoirement d'une étude dont tu as OUVERT le résumé original (PubMed, PMC, page de l'éditeur, Pew, Census) : donne ce
lien et la phrase lue ; un blog ou une fiche de révision ne compte pas. Un angle dont ces deux chiffres ne sont pas lus
n'est pas proposé. Écarte toute donnée qui porte sur des moins de 18 ans. Histoire ancienne : 30 s au plus, deux blocs au plus.
Interdits : viol et violences sexuelles, pornographie, pratiques sexuelles, tout classement de groupes, toute thèse sur un
groupe (on rapporte des études et leurs limites).
```

### fact-checker (étapes 3 et 4 bis)
Étape 3 (l'agent n'écrit pas de fichier : son rapport est copié dans `facts.md` par l'orchestrateur ; `brief.json` doit exister avant de le lancer) :
```
Vidéo de 12 minutes « [TITRE] ». Le script n'est pas écrit : tu vérifies l'ANGLE de <travail>/brief.json (champ "angle")
pour produire la liste des seuls faits que le rédacteur pourra utiliser. Il faut SIX jeux de données, un par bloc, et 4 à 7
sources nommées et datées, chacune ouverte par toi (article, PubMed/PMC, éditeur, Pew, Census ; pas un blog).
Pour chaque bloc : auteurs, année, revue ou organisme ; échantillon (qui, combien, où, quand) ; LE chiffre principal exact
avec son unité et la phrase lue ; un ou deux chiffres secondaires ; la limite principale (ce que l'étude ne permet pas de
dire) ; le lien ouvert. Ce que tu n'as pas lu toi-même : [to verify], avec un remplaçant vérifié. Signale tout chiffre qui
porte sur des moins de 18 ans : il est exclu. Un PDF scanné illisible : cherche la phrase dans un article qui la cite.
Blocs : [les six lignes de brief.json, avec pour chacune le chiffre à trancher].
Sortie : « ## Block N — … » par bloc, puis « ## Sources » (4 à 7 lignes « - Nom, année, titre, lien »), puis « ## Écarté ».
```
Une deuxième passe est normale (mesuré le 11 novembre 2026 : 5 points restés [to verify] après la première) : la relancer
par SendMessage sur le même agent, avec la liste numérotée des seuls points à lever et des pistes d'adresses.
Si un bloc tombe (étude hors sujet, chiffres sur des mineurs, source illisible), l'orchestrateur recompose les six blocs
avec les jeux vérifiés, garde la scène, le motif et la réponse de l'angle choisi, et le dit à l'utilisateur avant le script.

Étape 4 bis : lui donner `script.md`, avec cette ligne en plus :
```
En plus de tes vérifications : signale toute phrase qui dit plus que sa source (un échantillon présenté comme « les femmes »
ou « les hommes », une corrélation présentée comme une cause, un pays présenté comme le monde) avec le verdict
[corrected: …] et une réécriture prudente (« on average », « in this data set », « the women in this study »).
Les nombres sont écrits en lettres dans le script : vérifie la valeur, garde l'écriture en lettres.
```

### Rédacteur (étape 4, `general-purpose`)
```
Tu écris le script anglais (américain) d'une vidéo YouTube de 12 minutes de la chaîne The Hidden Bargain :
« [TITRE] ». Public : des hommes américains de 25 à 65 ans ; ton posé, curieux, jamais moqueur.
Lis dans cet ordre : <travail>/brief.json (angle choisi), <travail>/facts.md (les seuls faits autorisés : n'en ajoute aucun,
n'en arrondis aucun), <skill>/references/structure-ecriture.md (structure, règles, gabarit de script.md), puis les
script.md déjà publiés ([CHEMINS]) pour ne reprendre aucune de leurs phrases.
Écris <travail>/script.md : le titre en première ligne, 9 chapitres « ## Chapter N — nom », une phrase par ligne, puis
« ## Sources ». Écris comme on parle à une personne : contractions, détails concrets avant les idées, une image par ligne.
Pour l'ouverture, écris cinq versions des deux premières lignes, note-les avec
python ~/.claude/skills/yt-script/hookscore.py hooks.txt et garde la meilleure ; la question du titre, elle, ne change pas.
Lance python <skill>/scripts/yt/script_lint.py <travail>/script.md et réécris jusqu'à 0 erreur. Un écart se corrige
dans le passage fautif, pas en ajoutant des mots ailleurs.
Rends : le chemin de script.md, la sortie complète du lint, les scores des cinq ouvertures.
```

### Imagier (étape 6, `general-purpose`)
```
Tu écris la liste des plans d'une vidéo de la chaîne The Hidden Bargain. Lis <skill>/references/images-flow.md (la troupe,
les six règles, le budget) et l'en-tête de <skill>/scripts/make_shots.py.
Copie <skill>/scripts/make_shots.py dans <travail>/ et remplace SPECS : une entrée par ligne de <travail>/script.md.
Budget : 70 à 85 images Flow, chacune tenue sur 2 ou 3 lignes (R(key, cadrage)) ; un insert de données D(...) ou card(...)
toutes les 20 à 25 s, avec le chiffre exact de la ligne, son unité et la source en petit ; chaque bloc a au moins un insert ;
le dernier chapitre revient à la première image. Scènes au présent (era="modern") ; era="tribe" seulement pour la preuve
par l'histoire ancienne. Aucun mot de la liste BANNED de prompts.py, aucun texte ni chiffre demandé à Flow.
Lance, dans <travail>/ : python make_shots.py puis python <skill>/scripts/prompts.py shots.json --strict, jusqu'à
0 erreur ; traite les avertissements ou dis pourquoi tu les gardes. Ne modifie pas script.md.
Rends : la dernière ligne de chaque commande et la liste des avertissements gardés.
```

### visual-director (étape 6, une passe)
```
Fichier : <travail>/shots.json (écrit par make_shots.py : ne le modifie pas, il serait écrasé). Règles : <skill>/references/images-flow.md.
Ce qui prime sur tes réglages : les chiffres sont des inserts « html » (pas cards.py) ; une image tenue sur 2 ou 3 lignes
avec des cadrages différents est voulue. Rends seulement un tableau : numéro du plan | problème | la ligne de SPECS à
écrire à la place (S, N, M, R ou D), 15 lignes au plus, puis tes cinq lignes de résumé.
```
L'orchestrateur applique dans `make_shots.py`, puis relance `make_shots.py` et `prompts.py --strict`.

### image-qc (étape 7, passes 1 et 2)
```
Planches : [CHEMINS des sheet_*.jpg]. Liste des plans : <travail>/shots.json. Prompts : <travail>/prompts.json.
Fiche des personnages : [la phrase « qc » de <skill>/scripts/styles.json, recopiée].
Rejette aussi : épaules ou jambes nues, pose suggestive, arme dans une scène moderne, symbole religieux, l'ami dessiné en
silhouette ou en caricature, un humain détaillé à côté des bonshommes.
```
Passe 2 : seulement la planche des images refaites. Pour les miniatures : la même fiche, plus « visages grands et lisibles ».

### packaging-strategist (étape 9)
```
Dossier : <travail> (script.md, chapters.md, timing.json, keywords.md). Chaîne : The Hidden Bargain.
Ce qui prime sur tes réglages : le TITRE est fixé, ne le réécris pas : « [TITRE] » ; vérifie-le seulement avec
python <skill>/scripts/yt/ypp_lint.py --title "[TITRE]". Le TEXTE de miniature est la question du titre sur deux lignes
(mesure de la chaîne : 9,3 % de clics avec la question entière, 6,6 % avec « DO WOMEN REALLY?! ») : ignore la règle « ne pas
répéter le titre » de title.py.
Rends : (1) deux scènes de miniature au format thumb_specs.json de <skill>/references/images-flow.md §5 (A : le trio et
l'objet qui dit le sujet ; B : le héros et l'héroïne avec l'objet), personnages couverts, sans pose suggestive ; (2) le
découpage du texte en deux lignes ; (3) un nom de 3 à 5 mots pour chacun des 9 chapitres (la promesse du passage,
jamais un mot à risque). Le script et la voix sont terminés : ne propose aucune réécriture du script (le score
hookscore.py se lit à l’étape 4 ; il note « WEAK » toute ouverture dont les nombres sont en lettres ou qui dépasse
24 mots : mesuré le 11 novembre 2026, 35 à 48 sur cinq ouvertures conformes au gabarit, ne pas en faire une porte).
Quatre scènes plutôt que deux (A1, A2, B1, B2) quand l’utilisateur veut choisir : les quatre se génèrent en un lot.
```

### seo-metadata-editor (étape 9)
```
Mode NEW. Dossier : <travail>. Titre fixé : « [TITRE] ». Lien de la vidéo longue pour le Short : [LIEN ou « à remplacer »].
En plus de ta méthode : la description contient une section « Sources: » avec les 4 à 7 lignes de « ## Sources » de
script.md (auteur, année, titre, lien) et la phrase « Narration and illustrations are AI-generated. » ; aucun mot de la
liste RISK de <skill>/scripts/yt/ypp_lint.py dans les tags ni dans les deux premières lignes.
```
L'orchestrateur assemble ensuite les deux fichiers de `livraison/` (`publication.md` §6) et lance `ypp_lint.py`.

## Règles d'usage

- Aucun agent avant que l'utilisateur ait choisi le sujet ; aucun agent d'image avant que `script_lint.py` soit à 0.
- Les agents indépendants partent dans le même message : 5 ‖ 6, puis les deux agents de l'étape 9.
- Une sortie d'agent s'applique ou se refuse avec une raison ; on ne relance pas un agent pour confirmer ce qu'un lint mesure déjà.
- Les agents `seo-metadata-editor` et `packaging-strategist` s'appuient sur `~/.claude/skills/why-explainer-video/` (fiche de description, `meta_lint.py`) et sur `~/.claude/skills/yt-package`, `yt-script`, `yt-seo`, `yt-chapters` : ne pas supprimer ces dossiers.
