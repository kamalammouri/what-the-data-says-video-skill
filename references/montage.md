# Montage (HyperFrames), mixage, Short

Une seule voie : HyperFrames (sous-titres animés mot à mot, 53 % des vues sont sur mobile), puis le lit musical par ffmpeg. Tout se lance depuis le dossier de travail ; `<skill>` = `~/.claude/skills/what-the-data-says-video`.

## 1. Les inserts de données (par code, pas par Flow)

```
cd ~/.claude/skills/hand-drawn-visuals
PLAYWRIGHT_DIR=C:/Users/kamalAmmouri/Desktop/nastro node scripts/render.mjs <travail>/shots.json <travail>/flow/<video>/html --shots --anim
python <skill>/scripts/sheets.py flow/<video>/html sheets_html
```
Lire la planche : chaque chiffre est celui de la voix, avec son unité ; aucun texte ne déborde ; le journal ne dit pas `icon "x" not found` (noms d'icônes Lucide : `users`, `heart`, `ruler`, `calendar-days`, `coins`, `smartphone`…). Types et champs : `~/.claude/skills/hand-drawn-visuals/references/spec-format.md`.

**Inserts animés (13 novembre 2026).** `--anim` écrit, à côté de chaque PNG, `H<i>.anim.json` (le dessin en SVG et texte + la liste de ses entrées) et `html/fonts/` (Patrick Hand et Caveat en fichiers). `hf_build.py` monte alors l'insert vivant : la barre monte pendant que son chiffre compte de 0 à sa valeur, la jauge se remplit, la courbe se trace, l'icône apparaît, les lignes d'une liste arrivent une à une ; tout est en place avant la moitié du plan, puis l'insert tient sous un léger zoom. Raison : dans older-men-en les inserts restaient fixes de 2,4 à 8,4 s (médiane 5,5 s), et YouTube range les « diaporamas d'images » dans le contenu répétitif. Effet sur la rétention : pas encore mesuré.
- Un chiffre compte s'il est seul dans son texte (`53%`, `10,047`, `4.5 years`) ; `3:47`, `1 in 3` et les années (`1989`) apparaissent sans compter.
- Le PNG reste obligatoire : c'est lui qu'on lit sur la planche, et il règle la réduction au-dessus des sous-titres. Un PNG redessiné sans `--anim` efface son `.anim.json` (sinon l'ancien chiffre resterait à l'écran).
- Sans `.anim.json`, ou avec `hf_build.py … --static-inserts`, l'insert est l'image fixe d'avant.

## 2. Le projet

```
python <skill>/scripts/hf_build.py shots.json voice.wav timing.json hf --flow flow/<video> --split-long 2.5
npx hyperframes check hf --json
```
- `hf_build.py` annonce le nombre de clips et le rythme des coupes (attendu : une coupe toutes les 2 à 2,5 s) et **sort en erreur s'il manque une image** : la générer ou la remplacer avant le rendu.
- `--split-long 2.5` recoupe en deux ou trois cadrages tout plan animé de plus de 2,5 s ; les inserts ne sont pas recoupés (ils s'animent, §1). Les cartes-titres `T("…")` deviennent de la typographie animée. La dernière ligne de `hf_build.py` annonce `N animated inserts` : 0 = `--anim` oublié à l'étape 1.
- `python <skill>/scripts/hf_build.py --selftest` : vérifie que chaque entrée d'insert finit dans son plan et qu'une barre et son chiffre partent ensemble.
- `check` doit donner `ok: true` et 0 erreur. Une erreur se corrige dans `hf_build.py` si elle se répéterait, jamais à la main dans un fichier généré.
- `npx hyperframes snapshot hf --at 5,30,<un insert>,<fin>` : lire la planche (sous-titre lisible, jamais sur un chiffre d'insert, image qui bouge). Pour un insert animé, prendre trois instants : début du plan + 0,4 s (chiffre en cours de compte), + 1 s, et la fin du plan (le chiffre final est celui de la voix).
- Avertissement `line_unread` sur un insert : la ligne de source reste à l'écran moins longtemps que sa lecture ; raccourcir le champ `small` du plan, pas l'animation.

## 3. Le rendu

```
HF_SEGMENTED_CAPTURE=true npx hyperframes render hf --workers 10 --gpu      # en arrière-plan
```
Mesuré : 170 ms par image, 1 h pour 12 min avec les 4 workers du mode automatique (4 novembre 2026) ; 45 min pour les 12 min 30 de bath-en (10 novembre 2026). 25 min pour les 12 min 13 de older-men-en avec `--workers 10 --gpu` (11 novembre 2026). `--resume` reprend un rendu coupé ; `--quality draft` pour un aperçu. Pendant le rendu : la fiche de publication et les scènes de miniature.

## 4. Le lit musical et la porte audio

Commande et mesure : `voix-musique.md` §4 et §5 → `out.mp4`, `gate … OK`. `analyze_video.py out.mp4 check` écrit aussi `check/out_sheet.jpg` (48 images réparties) : la lire une fois pour repérer une carte crème « image manquante », un sous-titre coupé, une image hors sujet.

## 5. Les chapitres et le Short

```
python make_shots.py --chapters      # chapters.md aux temps réels de timing.json + la seconde où finit le chapitre 1
```
Le **Short d'appel** est le chapitre 1 entier : la scène, la question du titre, le premier chiffre, « But that number hides something ». Il s'arrête sur la boucle ouverte, moins de 60 s (le lint du script limite le chapitre 1 à 160 mots). `<fin>` = la valeur affichée par `--chapters` :
```
FF=$(python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -i out.mp4 -t <fin> -vf "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2" -c:a aac short.mp4
```

## 6. Le dossier de livraison (`livraison/`)

`video.mp4` (= `out.mp4`), `short.mp4`, `thumbnail-A.jpg`, `thumbnail-B.jpg`, `titre-description-tags.txt`, `short-titre-description-tags.txt`, `chapters.md`, `credits.csv` (musique), `publication.md` (réglages et heure). Formats des fichiers texte : `publication.md` §6.
