# Voix et musique

## 1. Ce que les mesures imposent

| Mesure | Avant (bath-en, 10 nov. 2026) | Cible | Comment |
|---|---|---|---|
| Ratio parole (`analyze_video.py`) | 0,80 sur la vidéo finale, 0,78 voix seule | **≥ 0,92** (0,959 et 0,92 sur les deux chaînes comparables) | pause courte + lit musical au bon niveau |
| Pause entre deux lignes | 0,50 s réelles (0,35 s ajoutées à 0,15 s de silence gardé autour de chaque clip) | **0,20 à 0,25 s** | `tts.py --gap 0.22` (défaut) : le silence gardé est maintenant compté dans la pause |
| Débit | 155 mots/min | **165 à 175** | même voix, pause corrigée : 165 mots/min |
| Musique | présente mais 0,08 de volume et écrasée par un sidechain qui la coupait dans les pauses | lit continu, 20 dB sous la voix | commande du §4 |

Mesures du 11 novembre 2026, refaites hors ligne sur les 166 clips ElevenLabs de bath-en (voix Daniel, `speed` 1,0) : pause de 0,22 s → 11:45, 165 mots/min, ratio 0,836 voix seule ; avec le lit à −34 LUFS → **ratio 0,982**, 0,5 pause par minute, −14,3 LUFS, pic −1,5 dB. Lit à −38 LUFS : 0,916 (insuffisant) ; à −30 LUFS : 0,999 (plus fort que nécessaire).

## 2. La voix (ElevenLabs)

- **La voix est celle de `brief.json`** (`"voice": {"engine": "eleven", "name": "...", "model": "eleven_multilingual_v2", "speed": 1.0}`), reprise du brief de la vidéo précédente pour que la chaîne garde une voix. Voix déjà utilisées sur la chaîne : Brian (la vidéo à 9,3 % de clics) et Daniel (bath-en). Sans voix dans le brief, demander à l'utilisateur ; ne jamais changer de voix dans une vidéo.
- **La clé** est dans le `.env` du dossier de travail (copier celui de la vidéo précédente ; jamais dans le skill, la mémoire ou la conversation). Lancer **toujours** avec `env -u ELEVENLABS_API_KEY` : une vieille clé dans le shell masque celle du `.env` et renvoie 401 (4 novembre 2026).
- **Lignes entières** : `python make_shots.py --voice` écrit `shots_voice.json` (une entrée par ligne de `script.md`). Un clip par ligne, jamais une ligne coupée en deux. `make_shots.py` refuse ensuite toute différence entre `script.md` et `shots_voice.json`.
- **Anglais seulement** : `tts.py` refuse un `voice_language` autre que `en` et toute ligne qui se lit comme du français (deux vidéos publiées avec une voix française sur cette chaîne anglaise, audit du 8 novembre 2026).

```
env -u ELEVENLABS_API_KEY python <skill>/scripts/tts.py shots_voice.json --only 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --out voicetest.wav --timing voicetest_timing.json     # 14 lignes : écouter ET lire le débit
env -u ELEVENLABS_API_KEY python <skill>/scripts/tts.py shots_voice.json                  # tout : voice.wav + timing.json
```

- Le quota de caractères est lu avant le premier appel ; code de sortie 3 s'il manque : demander à l'utilisateur, ne rien bricoler.
- **Régler la vitesse sur le test de 14 lignes, avant le lot complet** : changer `voice.speed` ensuite repaie tous les clips (environ 11 500 caractères), ce qu'un quota entamé ne permet pas. Mesuré le 11 novembre 2026 (older-men-en, voix Daniel) : 3 lignes donnent 156 mots/min (non représentatif), 14 lignes 163 mots/min à 1,0 ; à **1,07 le script entier sort à 170 mots/min** (12,21 min pour 2 080 mots). Les lignes d'ouverture, pleines de nombres en lettres, sont 3 à 4 % plus lentes que le reste : viser 163 à 167 sur le test. Plage utile : 1,0 à 1,10.
- La dernière ligne de la sortie donne la durée et le débit réel. Hors de 165–175 mots/min après le lot complet : raccourcir les lignes les plus lentes (seules ces lignes sont repayées) ou changer `--gap` entre 0,20 et 0,25 (gratuit).
- Une ligne corrigée ne coûte que ses caractères (cache `tts/eleven/` indexé sur le texte). Changer `--gap` ne coûte rien : aucun appel à ElevenLabs quand tous les clips sont en cache.
- Écrire pour la voix : nombres en lettres, pas de symboles, d'abréviations ni de parenthèses, 25 mots au plus par ligne.

## 3. Le lit musical (obligatoire)

Un fond calme et régulier, sans montée ni percussion marquée, en **CC0** (aucun crédit, sans risque pour la monétisation). Reprendre `music.mp3` et `credits.csv` de la vidéo précédente, ou en chercher un autre :
```
python <skill>/scripts/openverse.py "calm ambient pad" --out audio/music --n 4 --length medium
```
Écouter les candidats, copier celui retenu en `music.mp3`, garder `audio/music/credits.csv` avec la livraison. `--license by` élargit aux sons CC BY : la ligne `attribution` va alors dans la description. Jamais de NC ni de ND.

## 4. Le mixage (après le rendu, une commande)

Le rendu HyperFrames ne contient que la voix. La commande ajoute le lit 20 dB sous la voix, sans sidechain (c'est lui qui vidait les pauses), et sort à −14 LUFS avec un pic vrai de −1,5 dB, le niveau de lecture de YouTube. `<fin-3>` = la durée de la vidéo moins 3 s (fondu de sortie du lit seulement : la dernière ligne est la question au spectateur).
```
FF=$(python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -i hf/renders/<rendu>.mp4 -stream_loop -1 -i music.mp3 -filter_complex "[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3dB,loudnorm=I=-14:TP=-2:LRA=9[v];[1:a]loudnorm=I=-34:TP=-9:LRA=7,afade=t=in:d=1,afade=t=out:st=<fin-3>:d=3[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=disabled[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 out.mp4
```

## 5. La porte de sortie

```
python <skill>/scripts/yt/analyze_video.py out.mp4 check
```
La ligne finale doit dire `gate … OK` : ratio parole ≥ 0,92 et aucune pause de plus de 0,7 s. Si le ratio est sous 0,92 : monter le lit de 2 dB (`I=-32`) et remesurer ; ne pas descendre sous −30. L'utilisateur écoute 30 s au début, au milieu et à la fin avant la livraison : la mesure ne dit pas si la musique gêne.

Les effets sonores de l'ancien format (une trentaine par vidéo, quatre commandes, une écoute) sont retirés : aucun effet mesuré sur la rétention.
