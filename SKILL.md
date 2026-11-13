---
name: what-the-data-says-video
description: Produit de bout en bout une vidéo YouTube de 12 minutes pour la chaîne The Hidden Bargain (@hiddenbargain) au format « Do [Women/Men] Really [X]? What the Data Says » - choix du sujet par les chiffres, script orienté rétention fondé sur des études nommées, voix ElevenLabs, images Google Flow avec la troupe de la chaîne, montage HyperFrames, miniature, Short d'appel, fiche de publication conforme au Programme Partenaire YouTube, puis mesure dans Studio à J+2 et J+7. Utilise ce skill dès que l'utilisateur veut une nouvelle vidéo pour The Hidden Bargain, un sujet hommes-femmes ou d'attirance « données à l'appui », « what the data says », « do women really prefer… », un sujet qui rapporte des vues ou des heures de visionnage, la monétisation ou AdSense de cette chaîne, une miniature, un titre ou un Short pour elle, ou le bilan d'une vidéo publiée (clics, rétention), même s'il ne nomme pas le skill. Pour les vidéos préhistoriques « How did ancient humans… », utiliser ancient-humans-video.
---

# What the Data Says (The Hidden Bargain)

Une croyance sur l'attirance (« women prefer tall men »), posée comme question dans le titre, puis confrontée à six études ou jeux de données : ce que les gens disent, ce qu'ils font, ce qu'ils épousent, le chiffre qui contredit tout, et une réponse honnête. Le but de la chaîne est l'entrée au Programme Partenaire YouTube : 1 000 abonnés et 8 000 heures de visionnage (seuil du 1er février 2027) ; le 11 novembre 2026 elle a 12 abonnés et 27 heures. Chaque norme ci-dessous vient d'une mesure datée de cette chaîne (`references/channel-results.md`) et se corrige par la mesure suivante (étape 10).

## Langue et livrables

- Répondre à l'utilisateur dans sa langue. **Script, voix, titres, miniature, description et tags en anglais américain.**
- Un dossier de travail par vidéo (`<sujet>-en/`) à côté des précédents, et dedans `livraison/` : `video.mp4`, `short.mp4`, `thumbnail-A.jpg`, `thumbnail-B.jpg`, `titre-description-tags.txt`, `short-titre-description-tags.txt`, `chapters.md`, `credits.csv`, `publication.md`.
- Rien n'est publié ni modifié sur YouTube par le skill : l'utilisateur colle dans Studio.
- `<skill>` = `~/.claude/skills/what-the-data-says-video`. Sous Windows : outil Bash, `python -X utf8` si une sortie accentuée casse.

## Les normes (mesure, date)

| # | Norme | Mesure qui la fonde |
|---|---|---|
| 1 | **Un seul format, un seul thème** : hommes-femmes, « ce que disent les données » | les 2 vidéos longues les plus vues et le Short le plus vu sont à ce gabarit ; 4 formats mélangés, 99,7 % de spectateurs nouveaux, 12 abonnés (Studio, 11 nov. 2026) |
| 2 | **Sujet choisi par une note sur 9** (chaîne, demande, annonceurs) ; liste d'interdits | viol, contenu adulte, « Orgasm » : publicité limitée ou nulle, 4 à 101 vues (8 et 11 nov. 2026) |
| 3 | **Titre : une question ≤ 60 caractères**, « Do [Women/Men] Really [X]? What the Data Says », comptée par code | 52 car. : 9,3 % de clics ; 75 à 91 car. en deux questions : 3,3 à 7,2 % (11 nov. 2026) |
| 4 | **12 minutes, ≈ 2 000 mots** | l'objectif est en heures ; 4 min par vue sur la vidéo de 12:31 (11 nov. 2026) |
| 5 | **La question du titre dite avant 0:15, un premier chiffre avant 1:00** | question à 65 s dans bath-en ; à 12 s sur une chaîne comparable (10 nov. 2026) |
| 6 | **6 blocs de 80 à 110 s, un chiffre à l'écran par bloc, la réponse à 9:30** | données à 8:45 : chutes à 1:58 et 4:00, 33 % vus ; version 3:19 : 58 % (8 nov. 2026) |
| 7 | **Histoire ancienne : 30 s au plus, 2 blocs au plus** | la chute de 1:58 est l'entrée dans la préhistoire (8 nov. 2026) |
| 8 | **Formulations prudentes, 4 à 7 sources nommées, aucune phrase recopiée** | règles « contenu à gabarit » et « annonceurs » lues le 11 nov. 2026 (`monetisation-youtube.md`) |
| 9 | **Voix ElevenLabs en anglais, pause de 0,22 s, 165 à 175 mots/min** | pause réelle de 0,50 s, 155 mots/min ; corrigé : 165 mots/min (mesuré le 11 nov. 2026) ; 2 vidéos publiées en voix française |
| 10 | **Lit musical CC0 20 dB sous la voix ; ratio parole ≥ 0,92** | 0,80 avant ; 0,98 avec ce mixage (mesuré le 11 nov. 2026) ; 0,92 et 0,96 sur les chaînes comparables |
| 11 | **70 à 85 images Flow, 3 cadrages, coupe toutes les 2 à 2,5 s, un insert de données toutes les 20 à 25 s, contrôle en 2 passes** | 112 images, 27 refaites, 43 refus, 6 passes (bath-en, 10 nov. 2026) |
| 12 | **Troupe fixe et couverte** (héros, héroïne, ami), tout le monde en bonhomme bâton | miniatures suggestives et personnage en silhouette noire sur les vidéos les plus vues (11 nov. 2026) |
| 13 | **Miniature : la question du titre en jaune sur 2 lignes au-dessus de la scène, 2 variantes, test A/B** | question entière : 9,3 % ; « DO WOMEN REALLY?! » : 6,6 % (8 nov. 2026) |
| 14 | **Short d'appel relié en « Vidéo similaire », écran de fin, 13:00 ET, une longue tous les 2 ou 3 jours** | 78 % des vues du savon venaient de son Short ; écran de fin à 0,0 % ; 30 vidéos en 16 jours (11 nov. 2026) |
| 15 | **Mesure à J+2 et J+7, décision écrite** | aucune relecture de Studio dans l'ancien skill |

Si l'utilisateur veut un titre, un sujet ou une miniature hors norme : lui montrer la mesure, proposer la variante conforme, puis respecter son choix et l'écrire dans `brief.json` (`"risk_accepted"`).

## Workflow

Chaque étape a une porte de sortie par code ; on ne passe pas à la suivante tant qu'elle n'est pas franchie. Rôles et briefs des agents : `references/agents.md`.

1. **Sujet** (`references/sujets.md`). Lire `channel-results.md` (dernières lignes du journal et décisions). Prendre 3 à 5 candidats, mesurer la demande, **chercher sur YouTube si chaque sujet existe déjà** (tableau « 0 bis. Already on YouTube » de `keywords.md`), noter, montrer le tableau avec cette colonne, laisser l'utilisateur choisir.
   ```
   python <skill>/scripts/yt/keywords.py "do women prefer tall men" "do women prefer older men" --out keywords.md
   python <skill>/scripts/yt/ypp_lint.py --title "Do Women Really Prefer Tall Men? What the Data Says"
   ```
   Porte : titre « ok », ≤ 60 caractères, sujet absent de la chaîne, aucun interdit, et pour chaque candidat montré : le nombre de vidéos existantes, le lien de la plus proche et ce que la nôtre apporte (aucun titre repris mot pour mot).
2. **Angle et brief.** Agent `story-architect` : 3 angles (scène d'ouverture, premier chiffre, six jeux de données, renversement, réponse). L'utilisateur en choisit un. Écrire `brief.json` (ci-dessous), copier le `.env` et `flow/project.txt` de la vidéo précédente. Porte : `validated_by_user: true`.
3. **Faits.** Agent `fact-checker` sur l'angle : chaque chiffre avec sa source et son lien → `facts.md`. Porte : 6 jeux de données, 4 à 7 sources, aucun `[to verify]`. Un bloc qui tombe à la vérification se remplace par un jeu vérifié (brief dans `agents.md`) ; l'utilisateur est prévenu avant le script.
4. **Script** (`references/structure-ecriture.md`). Agent rédacteur, puis `fact-checker` sur le script.
   ```
   python <skill>/scripts/yt/script_lint.py script.md
   ```
   Porte : 0 erreur (question avant 0:15, chiffre avant 1:00, 9 chapitres, blocs de 80 à 110 s, relance toutes les 90 s au plus, formulations prudentes, sources nommées dans la voix).
5. **Voix** (`references/voix-musique.md`), en parallèle de l'étape 6.
   ```
   python make_shots.py --voice
   env -u ELEVENLABS_API_KEY python <skill>/scripts/tts.py shots_voice.json --only 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --out voicetest.wav     # écouter, régler voice.speed ICI (Daniel : 1,07 = 170 mots/min)
   env -u ELEVENLABS_API_KEY python <skill>/scripts/tts.py shots_voice.json
   ```
   Porte : 165 à 175 mots/min, aucun clip manquant. Code de sortie 3 (clé ou quota) : demander à l'utilisateur.
6. **Liste des plans** (`references/images-flow.md` §1-2). Agent imagier, puis `visual-director` une fois.
   ```
   python make_shots.py && python <skill>/scripts/prompts.py shots.json --strict
   ```
   Porte : 0 erreur, 70 à 85 images, un insert chiffré par bloc.
7. **Images** (`references/images-flow.md` §3-4). Prévenir l'utilisateur que Chrome sera fermé ; test sur 3 prompts ; puis le lot en arrière-plan.
   ```
   bash <skill>/scripts/flow/flow_loop.sh prompts.json flow/<video>
   python <skill>/scripts/flow/convert.py flow/<video> && python <skill>/scripts/sheets.py flow/<video> sheets
   ```
   Agent `image-qc` : passe 1 sur tout, passe 2 sur les images refaites, pas de passe 3. Porte : 0 rejet ou image remplacée.
8. **Montage, son, Short** (`references/montage.md`, `references/voix-musique.md` §4-5). Inserts par `hand-drawn-visuals`, puis :
   ```
   python <skill>/scripts/hf_build.py shots.json voice.wav timing.json hf --flow flow/<video> --split-long 2.5
   npx hyperframes check hf --json && HF_SEGMENTED_CAPTURE=true npx hyperframes render hf --workers 10 --gpu
   (mixage du lit musical : commande de voix-musique.md §4)  ->  out.mp4
   python <skill>/scripts/yt/analyze_video.py out.mp4 check
   python make_shots.py --chapters                                   # chapters.md + la fin du Short
   ```
   Porte : `check` ok, `gate … OK` (ratio parole ≥ 0,92), planche `check/out_sheet.jpg` lue, Short de moins de 60 s.
9. **Emballage et livraison** (`references/publication.md`), pendant le rendu. Agents `packaging-strategist` (scènes de miniature, noms de chapitres) et `seo-metadata-editor` (description, tags, Short) en parallèle.
   ```
   python <skill>/scripts/prompts.py --thumbs thumb_specs.json && bash <skill>/scripts/flow/flow_loop.sh thumbs.json flow/thumbs
   python <skill>/scripts/thumb.py flow/thumbs/T1.jpg livraison/thumbnail-A.jpg "DO WOMEN REALLY|PREFER TALL MEN?" --fit
   python <skill>/scripts/yt/ypp_lint.py .
   ```
   Porte : les deux miniatures regardées (aucun visage couvert, personnages couverts), `ypp_lint.py` à 0 erreur, `livraison/` complet, heure donnée en ET et en heure de Casablanca calculées par code. Rappeler à l'utilisateur : Short le même jour avec « Vidéo similaire », écran de fin, test A/B des miniatures, deux jours depuis la dernière vidéo longue.
10. **Mesure** (`references/mesure.md`). À J+2 puis à J+7, lire Studio avec `scripts/yt/studio.mjs` (lecture seule), ajouter la ligne au journal de `channel-results.md`, appliquer la règle de décision : clics < 5 % → la miniature, puis la famille de sujets ; % vu < 35 % → l'ouverture, le bloc de la falaise ou le rythme, selon la courbe. Toute norme modifiée porte sa mesure et sa date. Proposer à l'utilisateur de programmer ces deux relectures quand la vidéo est en ligne.

## `brief.json`

```json
{"format": "what-the-data-says-video", "channel": "@hiddenbargain",
 "title": "Do Women Really Prefer Tall Men? What the Data Says",
 "subject": {"score": {"a": 3, "b": 2, "c": 3}, "seed": "do women prefer tall men", "risk_accepted": null},
 "angle": {"choice": "A", "opening_scene": "...", "first_figure": "...", "datasets": ["1 ...", "2 ...", "3 ...", "4 (reversal) ...", "5 ...", "6 ..."],
           "honest_answer": "...", "thumbnail_object": "..."},
 "voice_language": "en", "voice": {"engine": "eleven", "name": "<voix de la vidéo précédente>", "model": "eleven_multilingual_v2", "speed": 1.0},
 "setting": "each scene in its own present-day place, drawn as a fully painted set with depth",
 "duration_min": 12, "music": "music.mp3 (CC0, credits.csv)", "previous_videos": ["..."], "validated_by_user": true}
```

## Fichiers du skill

| Fichier | Le lire quand |
|---|---|
| `references/channel-results.md` | avant de choisir un sujet ; à chaque mesure (chiffres des audits, journal) |
| `references/sujets.md` | étape 1 : grille de notation, interdits, banque de 15 titres |
| `references/structure-ecriture.md` | étapes 2 à 4 : plan minuté, bloc type, règles d'écriture, gabarit de `script.md` |
| `references/images-flow.md` | étapes 6, 7 et 9 : troupe, règles d'image, Flow, refus, contrôle, miniatures |
| `references/voix-musique.md` | étapes 5 et 8 : ElevenLabs, lit musical, mixage, porte audio |
| `references/montage.md` | étape 8 : inserts, HyperFrames, rendu, chapitres, Short, dossier de livraison |
| `references/publication.md` | étape 9 : titre, miniature, description, Short, réglages Studio, fichiers texte |
| `references/monetisation-youtube.md` | avant un sujet ou une miniature à risque ; avant une demande d'adhésion (règles lues le 11 nov. 2026) |
| `references/mesure.md` | étape 10 : commandes Studio, règle de décision |
| `references/agents.md` | avant de lancer un agent : tableau étape / agent / entrée / sortie / porte, briefs |

Scripts (`scripts/`) : `make_shots.py` (gabarit à copier dans le dossier de travail), `prompts.py`, `tts.py`, `hf_build.py`, `thumb.py`, `sheets.py`, `openverse.py`, `styles.json` ; `flow/` (`flow_loop.sh`, `batch.mjs`, `browser.mjs`, `login.mjs`, `goto.mjs`, `harvest.mjs`, `peek.mjs`, `convert.py`, `harvest_sheet.py`, `kill_flow_edge.ps1`, `cdp.mjs`) ; `yt/` (`keywords.py`, `script_lint.py`, `ypp_lint.py`, `analyze_video.py`, `studio.mjs`). Tests sans réseau : `--selftest` sur `prompts.py`, `tts.py`, `thumb.py`, `yt/script_lint.py`, `yt/ypp_lint.py`, `yt/keywords.py`. `assets/cast/` : les trois références de la troupe ; `assets/example/script.md` : un script de 12 lignes pour essayer `make_shots.py` et `prompts.py`.

Dépendances déjà installées sur la machine : Python 3.13 (Pillow, imageio-ffmpeg, librosa, soundfile, scenedetect), Node 24, Playwright dans `C:/Users/kamalAmmouri/Desktop/nastro`, `npx hyperframes`, yt-dlp, les skills `hand-drawn-visuals`, `hyperframes`, `yt-script`, `yt-package`, `yt-seo`, `yt-chapters`, `yt-retention`, `why-explainer-video` (lint de description de l'agent SEO).

## Contrôle avant de rendre la main

- [ ] Sujet noté et choisi par l'utilisateur ; titre au gabarit, ≤ 60 caractères, compté par `ypp_lint.py --title`
- [ ] `script_lint.py` : 0 erreur ; `fact-checker` : aucune correction restante ; `facts.md` et `## Sources` avec 4 à 7 sources
- [ ] Voix en anglais, 165 à 175 mots/min ; `out.mp4` : `gate … OK` ; l'utilisateur a écouté trois passages
- [ ] `prompts.py --strict` : 0 erreur ; 70 à 85 images ; contrôle en 2 passes terminé ; aucune carte « image manquante » sur la planche finale
- [ ] Deux miniatures 1280 × 720 regardées : question du titre lisible, aucun visage couvert, personnages couverts, ami dessiné avec un visage
- [ ] `ypp_lint.py` : 0 erreur ; `livraison/` complet ; Short < 60 s ; heure de publication calculée ; consignes Studio rappelées
- [ ] Date de la mesure J+2 et J+7 annoncée à l'utilisateur
