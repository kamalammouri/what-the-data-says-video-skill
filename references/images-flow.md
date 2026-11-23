# Images : la troupe, la shot list, Google Flow, le contrôle

Mesure de départ (bath-en, 9-10 novembre 2026) : 112 images Flow pour 12 min, 27 refaites, 43 refus « unusual activity », 6 passes de contrôle. Ce format en demande **70 à 85**, contrôlées en **2 passes**.

## 1. La troupe (un seul style, `scripts/styles.json`)

| Rôle (`cast`) | Dessin | Référence Flow | Costume `modern` | Costume `tribe` |
|---|---|---|---|---|
| `hero` | bonhomme bâton à tête blanche, houppe blonde, petite moustache brune | `reference.png` | sweat gris, jean, mains vides | tunique de fourrure brune |
| `heroine` | tête blanche, longs cheveux roux ondulés, lèvres rouges | `heroine.png` | pull vert à manches longues, jupe longue | robe de fourrure longue, manches longues, encolure ronde |
| `friend` | tête brune au visage dessiné et souriant, cheveux noirs bouclés, barbe courte | `second-male.png` | pull rouge sombre, jean, mains vides | tunique de loup grise |

Copies des trois références : `assets/cast/` (origine : `bath-en/flow/`). Elles montrent une lance et, pour l'héroïne, une robe courte : le texte du costume les corrige dans chaque prompt, et le contrôle le vérifie.

Règles de l'utilisateur (9 au 11 novembre 2026), refusées par `prompts.py` quand le texte de la scène les enfreint :
1. **Tout le monde est un bonhomme bâton.** Jamais un humain détaillé ou réaliste à côté d'eux ; les figurants sont de petits bonshommes simples. Un chercheur se nomme dans la voix et dans un insert, il ne se dessine pas.
2. **Personnages couverts** : manches longues et vêtements longs pour l'héroïne, aucune pose suggestive (à genoux, penchée, main sur la hanche).
3. **Aucune lance ni arme dans une scène moderne** (`era: modern` est le défaut).
4. **Aucun symbole religieux** (croix, église, mosquée, auréole…) ; un mariage se montre par une arche de fleurs.
5. **Une personne noire a un vrai visage dessiné** (le rôle `friend`), jamais une silhouette noire, jamais une caricature.
6. Jamais de texte, de chiffre ni de bulle demandés à Flow : les chiffres passent par les inserts.

## 2. La shot list (`make_shots.py`, gabarit dans `scripts/`)

- Une ligne de `script.md` = un clip de voix = un plan. Copier `scripts/make_shots.py` à côté de `script.md` et remplacer `SPECS` (une liste par chapitre, une entrée par ligne).
- **6 à 7 images Flow par minute** (`prompts.py --flow-per-min 7`, soit 70 à 85 pour 12 min). Chaque image sert jusqu'à **3 lignes de suite** avec trois cadrages (`S(...)` puis `R(key, "zoom")`, `R(key, "pan-left")`). Au montage, `--split-long 2.5` recoupe tout plan de plus de 2,5 s : une coupe toutes les 2,2 s sans image de plus (mesuré le 11 novembre 2026 sur l'exemple de 12 lignes).
- **Un insert de données toutes les 20 à 25 s** (`D({...})` ou `card(...)`), dessiné par le skill `hand-drawn-visuals` : `card`, `compare`, `gauge`, `bar`, `line`, `pie`, `timeline`, `list`. Le lint refuse 30 s sans chiffre à l'écran, un premier chiffre après 1:00, et `make_shots.py` refuse un bloc sans insert chiffré. Le chiffre de l'insert est celui de la voix, avec son unité et la source en petit (« Pew, 2017 »).
- Le dernier chapitre revient à l'image d'ouverture par `R(<clé de la première image>)` : aucune génération de plus, et `make_shots.py` le vérifie.
- Scènes : le présent d'abord (bar, appli sur un téléphone à l'écran vide, bureau, rue, cuisine). `era="tribe"` seulement pour la preuve courte par l'histoire ancienne.
- Varier les cadrages (`wide`, `medium`, `close`, `cutaway`, `overhead`, `pov`) ; jamais deux images voisines de même composition sur le même sujet (avertissement « near-duplicate »).

Commandes, dans le dossier de travail :
```
python make_shots.py --voice                                  # shots_voice.json : la voix peut partir
python make_shots.py                                          # shots.json, chapters.json, files.json
python <skill>/scripts/prompts.py shots.json --strict         # lint à 0 erreur + prompts.json (avec "refs")
```
L'agent `visual-director` relit ensuite `shots.json` une fois (`agents.md`).

## 3. Générer dans Google Flow (`scripts/flow/`)

Flow n'a pas d'API : un vrai Chrome piloté par Playwright (`PLAYWRIGHT_DIR=C:/Users/kamalAmmouri/Desktop/nastro`, profil `~/.flow-profile`, port 9222).

1. `flow/project.txt` = l'adresse du projet Flow qui contient déjà les trois références (la reprendre du dossier de la vidéo précédente). Projet neuf : y importer les trois PNG de `assets/cast/` sans les renommer ; `batch.mjs` les retrouve par leur nom et les attache comme ingrédients à chaque prompt qui porte `refs`.
2. Première fois ou session expirée : `node scripts/flow/browser.mjs` puis `node scripts/flow/login.mjs` ; **l'utilisateur se connecte lui-même** dans la fenêtre, on ne saisit jamais un mot de passe.
3. **Test sur 3 prompts** (un extrait `p3.json` : une scène à trois, un gros plan, une métaphore) : `bash scripts/flow/flow_loop.sh p3.json flow/test`, planche, lecture. On ne lance le lot qu'après.
4. Le lot : `bash scripts/flow/flow_loop.sh prompts.json flow/<video>` en arrière-plan, sortie dans `batch.log`. Prévenir l'utilisateur avant : avec Chrome, **toutes les fenêtres Chrome de la machine sont fermées** à chaque redémarrage (`FLOW_CHANNEL=msedge FLOW_PROFILE=~/.flow-profile-edge` ne ferme que l'Edge du profil Flow).
5. `python scripts/flow/convert.py flow/<video>` puis `python scripts/sheets.py flow/<video> sheets` (12 images par planche).

**Procédure de refus (règle de l'utilisateur, 9-10 novembre 2026), appliquée par `flow_loop.sh`** : au **premier** refus (`MAXFAIL=1`), on garde ce qui est sur disque, on ferme tout Chrome, on attend une minute, on relance Flow dans une session neuve et on reprend. On ne retélécharge jamais ce qui est déjà là ; `harvest.mjs` ne tourne que si une image a été générée sans être téléchargée (`TIMEOUT`, `NOT QUEUED`). Après 5 redémarrages sans image nouvelle, le script s'arrête : demander à l'utilisateur (attendre, ou ouvrir un projet Flow neuf). Mesuré : 20 s entre deux images (`PACE=20000`) ; à 7 s, blocage de deux à trois heures (octobre 2026).

Pièges connus : laisser le bouton **Agent** désactivé ; réglage du projet sur Image · 16:9 · x1 (après une génération de vidéo, le remettre sur Image) ; `node scripts/flow/peek.mjs peek.png` montre la page quand un lot cale.

## 3b. Secours : Meta Muse (muse.ai), quand Flow bloque

À utiliser quand Flow refuse (« activité inhabituelle ») ou cale. Testé le 22 novembre 2026 sur le compte gratuit de l'utilisateur (Muse Spark 1.3), avec 4 scènes de medieval-bath-en :
- **Ce qui marche :** les images sortent en 2048×1152 (vrai 16:9) au format WebP, sans texte. Le héros est reconnaissable, la qualité est proche de Flow, avec des décors un peu plus sombres.
- **Quantité et délai :** 4 images par demande au plus, environ une minute par demande.
- **Limite hebdomadaire gratuite :** la limite exacte en nombre d'images n'a pas encore été mesurée. La noter dans `channel-results.md` le jour où elle bloque.

1. **Préparer les messages :** `python scripts/flow/muse.py batches prompts.json flow/<video>` écrit `muse_batches.md`. Chaque message regroupe 4 images qui demandent les mêmes personnages. Les règles et le style commun n'y sont écrits qu'une fois. La liste exclut les images déjà présentes dans `flow/<video>`.
2. **Les références à joindre :** les fichiers de `assets/cast/`, en remplaçant `reference.png` par **`hero-modern.png`**. L'ancienne référence montre le héros en homme des cavernes avec une lance, et Muse a recopié la lance et les jambes nues dans une rue médiévale. Chaque message interdit donc aussi les armes et les jambes nues.
3. **Envoyer les messages :** l'utilisateur colle chaque message dans muse.ai avec les fichiers joints, ou Claude le fait avec Claude in Chrome après l'accord de l'utilisateur, un lot à la fois. Ne jamais connecter d'application à Muse (Gmail, Agenda) pour la chaîne.
4. **Récupérer les images :** ouvrir chaque image et cliquer sur Télécharger, **dans l'ordre des codes**. Les fichiers arrivent dans `~/Downloads` sous le nom que Muse leur donne (`media-generation-<description>-0-<id>.webp`). Un script de la page ne peut pas envoyer les fichiers vers 127.0.0.1, car muse.ai le bloque.
5. **Les importer :** `python scripts/flow/muse.py import flow/<video> --order F048,F050,...` range dans `flow/<video>/F###.png` le fichier qui porte son code dans le nom, et les autres du plus ancien au plus récent, dans l'ordre donné. Puis planche et contrôle, comme pour Flow (§4).
6. **Muse Video : pas pour la troupe.** Le clip testé faisait 10 s en 1248×704 avec un son d'ambiance, sans filigrane visible, et le mouvement de caméra était bon. Mais dès 2 s, le héros a pris des yeux bleus, un nez et un visage réaliste. Il reste à essayer, un jour, pour des plans de décor sans personnage (vapeur, feu, rue la nuit).
7. **Droits :** les conditions de Meta ne disent rien de l'usage commercial des images générées (vérifié le 22 nov. 2026). Les noter dans `credits.md` (« Meta Muse Image ») et revérifier les conditions avant une monétisation à grande échelle.

## 4. Contrôle en 2 passes (agent `image-qc`)

- **Passe 1** : toutes les planches, avec la phrase `qc` de `styles.json` et `shots.json`. Pour chaque rejet : fichier, défaut, prompt réécrit. Supprimer les `.jpg` et `.png` rejetés, remplacer leur prompt dans `prompts.json`, relancer `flow_loop.sh` (seuls les fichiers absents sont générés).
- **Passe 2** : la planche des images refaites seulement.
- **Pas de passe 3.** Une image encore refusée est remplacée dans `make_shots.py` par `R(...)` de l'image voisine ou par un insert `D(...)`, puis `make_shots.py` et `prompts.py` sont relancés.

Motifs de rejet : texte, chiffre ou bulle ; personnage différent de sa fiche ; humain détaillé ; épaules ou jambes nues, pose suggestive ; arme dans une scène moderne ; symbole religieux ; ami en silhouette ou caricaturé ; cadrage vertical ; membre en trop ; scène qui ne correspond pas à la phrase.

## 5. Les deux scènes de miniature

Écrire `thumb_specs.json` puis `python scripts/prompts.py --thumbs thumb_specs.json` : les mêmes fiches, costumes couverts et références que la vidéo.
```json
[{"file": "T1", "cast": "hero+heroine+friend", "era": "tribe",
  "action": "The heroine in the middle holds a flat grey stone tablet upright and smiles calmly, the hero on her left stares at it with huge worried eyes and sweat drops, the friend on her right raises his eyebrows",
  "prop": "The tablet shows only small carved bars of different heights and two tiny stick figures, no letters and no digits",
  "setting": "a night-blue forest with a big pale full moon and a small campfire"},
 {"file": "T2", "cast": "hero+heroine", "era": "tribe", "action": "…", "prop": "…", "setting": "…"}]
```
Variante A : le trio autour de l'objet qui dit le sujet (le gabarit de la miniature à 9,3 %). Variante B : le héros et l'héroïne seuls avec l'objet. Génération : `bash scripts/flow/flow_loop.sh thumbs.json flow/thumbs`. Le contrôle `image-qc` s'applique aussi (personnages couverts, visages lisibles, ami dessiné). Le texte se pose par code : `publication.md` §2.
