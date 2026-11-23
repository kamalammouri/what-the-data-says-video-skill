# Voix et musique

## 1. Ce que les mesures imposent

| Mesure | Avant (bath-en, 10 nov. 2026) | Cible | Comment |
|---|---|---|---|
| Ratio parole (`analyze_video.py`) | 0,80 sur la vidéo finale, 0,78 voix seule | **≥ 0,92** (0,959 et 0,92 sur les deux chaînes comparables) | pause courte + lit musical au bon niveau |
| Pause entre deux lignes | 0,50 s réelles (0,35 s ajoutées à 0,15 s de silence gardé autour de chaque clip) | **0,20 à 0,25 s** | `tts.py --gap 0.22` (défaut) : le silence gardé est maintenant compté dans la pause |
| Débit | 155 mots/min | **165 à 175** | même voix, pause corrigée : 165 mots/min |
| Musique | présente mais 0,08 de volume et écrasée par un sidechain qui la coupait dans les pauses | lit continu, 20 dB sous la voix | commande du §4 |

Mesures du 11 novembre 2026, refaites hors ligne sur les 166 clips ElevenLabs de bath-en (voix Daniel, `speed` 1,0) : pause de 0,22 s → 11:45, 165 mots/min, ratio 0,836 voix seule ; avec le lit à −34 LUFS → **ratio 0,982**, 0,5 pause par minute, −14,3 LUFS, pic −1,5 dB. Lit à −38 LUFS : 0,916 (insuffisant) ; à −30 LUFS : 0,999 (plus fort que nécessaire).

## 2. La voix (VoiceStudio, locale et gratuite, depuis le 22 novembre 2026)

`tts.py` parle à l'application **VoiceStudio** ouverte sur la machine (`http://127.0.0.1:3900`, autre adresse : variable `VOICESTUDIO_URL`). Chaque ligne passe par `/v1/audio/speech` avec la voix enregistrée dans VoiceStudio et une graine fixe, puis le clip est retranscrit avec l'heure de chaque mot (`/v1/audio/transcriptions`) ; les mots entendus sont réalignés sur le texte du script, ce qui donne les mêmes temps par caractère qu'ElevenLabs (sous-titres mot à mot inchangés dans `hf_build.py`). Aucune clé, aucun quota.

- **Créer la voix de la chaîne une seule fois** dans VoiceStudio (onglet Voices : « design » depuis une description, ou « clone » de ta propre voix avec ton consentement enregistré), lui donner un nom fixe, par exemple `Hidden Bargain Narrator`, puis l'écrire dans `brief.json` : `"voice": {"engine": "voicestudio", "name": "Hidden Bargain Narrator", "seed": 42, "speed": 1.0}`. La « Demo Voice » livrée avec l'app sert aux tests seulement. Ne jamais changer de voix ni de `seed` dans une vidéo : une autre graine change le timbre.
- **L'app doit tourner** : `voicestudio status`. Fermée → `tts.py` sort avec le code 3 : demander à l'utilisateur de l'ouvrir.
- **Lignes entières** : `python make_shots.py --voice` écrit `shots_voice.json` (une entrée par ligne de `script.md`). Un clip par ligne, jamais une ligne coupée en deux. `make_shots.py` refuse ensuite toute différence entre `script.md` et `shots_voice.json`.
- **Anglais seulement** : `tts.py` refuse un `voice_language` autre que `en` et toute ligne qui se lit comme du français (deux vidéos publiées avec une voix française sur cette chaîne anglaise, audit du 8 novembre 2026).

```
python <skill>/scripts/tts.py shots_voice.json --only 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --out voicetest.wav --timing voicetest_timing.json     # 14 lignes : écouter ET lire le débit
python <skill>/scripts/tts.py shots_voice.json                  # tout : voice.wav + timing.json (en arrière-plan : c'est long)
```

- **Durée mesurée le 22 novembre 2026** (Mac Apple Silicon, moteur OmniVoice, Demo Voice) : 3 lignes en 8 min 24 s, soit environ 2 à 3 min par ligne voix + minutage compris. Un script de 160 lignes demande donc plusieurs heures : lancer le lot complet en arrière-plan (ou la nuit). Le cache rend la reprise gratuite : une ligne déjà faite n'est jamais refaite. Pour aller plus vite, essayer un autre moteur dans VoiceStudio (`voicestudio engines list`, puis `engines select`), le tester sur les 14 lignes, et ne pas en changer au milieu d'une vidéo.
- **Débit** : 171 mots/min sur ce test de 3 lignes à `speed` 1,0 (non représentatif, comme avec ElevenLabs). Régler `voice.speed` sur le test de 14 lignes ; changer la vitesse ensuite refait tous les clips (du temps, plus d'argent).
- **Quand `speed` n'agit pas** (cas mesuré le 22 nov. 2026 avec la voix The Documentarian : 198 mots/min à `speed` 0,91) : `voice.wpm` dans le brief (ou `--wpm`) donne à chaque ligne une durée cible ; le moteur lit environ 14 % plus vite que demandé, donc 155 demandés donnent environ 170. `voice.tempo` (ou `--tempo`, par ex. 0,88) ralentit ensuite à l'assemblage, avec `atempo`, sans refaire les clips. `--num-step` règle la qualité du moteur. Le cache tient compte de la graine, de `wpm` et de `num_step`.
- **Minutage des mots** : une seule transcription de toute la piste, par morceaux de 60 s environ. Sur ce Mac elle prend environ 85 s par appel et a renvoyé des erreurs 504 sur la vidéo du bain : `timing.json` ne garde alors que le début de chaque ligne, et les sous-titres répartissent les mots dans la ligne. `--no-words` saute cette étape.
- La dernière ligne de la sortie donne la durée et le débit réel. Hors de 165–175 mots/min après le lot complet : raccourcir les lignes les plus lentes (seules ces lignes sont refaites) ou changer `--gap` entre 0,20 et 0,25 (instantané).
- Cache `tts/voicestudio/` indexé sur voix, graine, vitesse et texte : une ligne corrigée ne refait que son clip ; changer `--gap` ne refait rien.
- VoiceStudio sort du 24 kHz (aigus coupés au-dessus de 12 kHz) ; `tts.py` le passe en 44,1 kHz sans rien ajouter. Écouter le test au casque : si la voix sonne terne à côté des anciennes vidéos, le noter dans `channel-results.md`.
- Le minutage vient d'une transcription : un nombre dit en lettres et entendu en chiffres (« nineteen sixty-seven » → « 1967 ») est retrouvé par répartition entre les mots voisins. Vérifier sur la planche HyperFrames qu'aucun sous-titre ne décroche.
- **Repli ElevenLabs** (ancienne voix Brian ou Daniel) : `"engine": "eleven"` dans le brief ou `--engine eleven`, clé `ELEVENLABS_API_KEY` dans le `.env` du dossier de travail, lancer avec `env -u ELEVENLABS_API_KEY`, quota lu avant le premier appel (code 3 s'il manque).
- Écrire pour la voix : nombres en lettres, pas de symboles, d'abréviations ni de parenthèses, 25 mots au plus par ligne.

## 3. Le lit musical (obligatoire)

Un fond calme et régulier, sans montée ni percussion marquée, en **CC0** (aucun crédit, sans risque pour la monétisation). Reprendre `music.mp3` et `credits.csv` de la vidéo précédente, ou en chercher un autre :
```
python <skill>/scripts/openverse.py "calm ambient pad" --out audio/music --n 4 --length medium
```
Écouter les candidats, copier celui retenu en `music.mp3`, garder `audio/music/credits.csv` avec la livraison. `--license by` élargit aux sons CC BY : la ligne `attribution` va alors dans la description. Jamais de NC ni de ND.

## 4. Le mixage (après le rendu, une commande)

**Depuis le 23 novembre 2026, la musique joue par moments, comme dans un film** (choix de l'utilisateur après la vidéo du bain : « j'aime pas la musique sur la vidéo complète, il faut l'utiliser sur quelques parties comme les films »). C'est le mode par défaut de `python <skill>/scripts/mix.py hf/renders/<rendu>.mp4 music.mp3 out.mp4` :
- **Où joue la musique :** sous l'accroche (les 12 premières secondes), à chaque changement de chapitre (de 2,5 s avant à 5 s après), sur chaque temps fort `//` (le silence, puis 3,5 s sous la ligne suivante) et sous les 35 dernières secondes. Ailleurs, la voix est seule.
- **Niveau :** −28 LUFS (`--level`), environ 14 dB sous la voix. Entrée en 0,15 s, sortie en 1,2 s.
- **Mesuré sur la vidéo du bain remixée (23 nov.) :** musique sur environ 15 % de la durée, ratio parole 0,943, pause maximale 0,56 s.
- **Contrôle :** `analyze_video.py out.mp4 check --cues`. Le seuil du ratio y est de 0,78, celui d'une voix seule, avec toujours aucune pause de plus de 0,7 s.
- **L'ancien lit continu reste disponible** avec `--continuous`, décrit ci-dessous.

**Depuis le 22 novembre 2026 : `python <skill>/scripts/mix.py hf/renders/<rendu>.mp4 music.mp3 out.mp4`** fait la même chaîne que la commande ci-dessous, et remonte en plus le lit de 8 dB (`--lift`) sur chaque temps fort (ligne de `script.md` terminée par ` //`, silence de 0,9 s laissé par `tts.py`), avec des rampes de 0,15 s et 0,35 s. La pause s'entend comme une respiration, pas comme un trou, et le contrôle du §5 reste valable. Sans temps fort, le résultat est identique à la commande ci-dessous. Pourquoi : `structure-ecriture.md` §5.

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
