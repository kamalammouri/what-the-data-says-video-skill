# Photos d'archives et images 3D (cinematic-film + open-3d-skills)

Ajouté le 22 novembre 2026 pour les sujets d'histoire (« la vie avant le confort moderne ») : une vraie photo d'époque, sourcée et créditée, montre que la vidéo repose sur des documents et pas seulement sur des images générées. Effet sur les clics et la rétention : **pas encore mesuré** ; commencer à une photo pour 4 à 5 plans et juger à J+7 (`mesure.md`).

Deux skills externes fournissent les outils, installés à part et mis à jour par `git pull` :
- `cinematic-film` (`~/.cinematic-skill`, MIT, Moh4696/cinematic-skill) : recherche et téléchargement d'images libres avec leur licence.
- `open-3d-skills` (`~/.open-3d-skills`, MIT, Moh4696/open-3d-skills) : scènes three.js construites par code, vues éclatées, enregistrement d'une page en vidéo.

Installation (une fois) :
```
git clone --depth 1 https://github.com/Moh4696/cinematic-skill ~/.cinematic-skill && bash ~/.cinematic-skill/install.sh --claude
git clone --depth 1 https://github.com/Moh4696/open-3d-skills ~/.open-3d-skills && bash ~/.open-3d-skills/install.sh --claude
```

## 1. Les règles

1. **Une photo d'archive est un plan à elle seule.** Jamais la troupe collée dessus : la règle « tout le monde est un bonhomme bâton » (`images-flow.md` §1) reste vraie pour les images Flow.
2. **Rien d'inventé qui ait l'air vrai** (règle 7 de `cinematic-film`). Une image Flow n'est jamais présentée comme une photo d'époque ou la preuve d'un fait ; une photo réelle est toujours créditée à l'écran (`caption`) et dans la description.
3. **Licences acceptées :** domaine public, CC0, CC BY, CC BY-SA. `fetch_commons.py` refuse le reste. CC BY et CC BY-SA : l'auteur et la licence dans la description (ligne « Image credits »). Jamais NC ni ND.
4. **La photo dit la même chose que la voix.** Si la voix parle de Paris en 1292, la photo n'est pas un bain hongrois de 1885 présenté comme parisien : le `caption` donne le vrai lieu et la vraie date.

## 2. Photos d'archives (étape 6, avant `make_shots.py`)

Dans le dossier de travail :
```
python ~/.cinematic-skill/skills/cinematic-film/scripts/fetch_commons.py search "medieval bathhouse illumination" --limit 12
python ~/.cinematic-skill/skills/cinematic-film/scripts/fetch_commons.py category "Category:Public baths in art" --limit 40
```
Écrire `photos.json` avec les fichiers retenus :
```json
{"photos": [
  {"id": "P01", "kind": "photo", "commons": "File:Mészöly Bath-house at lake Balaton c. 1885.jpg"},
  {"id": "P02", "kind": "doc", "url": "https://tile.loc.gov/.../full.jpg", "credit": "Library of Congress", "license": "Public domain", "source": "https://www.loc.gov/item/..."}
]}
```
Puis :
```
python ~/.cinematic-skill/skills/cinematic-film/scripts/fetch_commons.py get --project .        # -> assets/photos/P01_<titre>.jpg
python ~/.cinematic-skill/skills/cinematic-film/scripts/fetch_commons.py credits --project .    # -> credits.md (à recopier dans livraison/)
```
Dans `make_shots.py`, une ligne du script devient :
```python
A("bathhouse", "P01", "pan-left", caption="Géza Mészöly, c. 1885 · Public domain · Wikimedia Commons"),
```
`A()` ne compte pas dans le budget Flow et n'a pas de prompt. `R("bathhouse", "zoom")` la réutilise comme une image Flow. `hf_build.py` la cherche dans `--flow`, puis dans `--photos` (défaut `assets/photos`, où `fetch_commons.py` écrit) ; il pose l'image entière, jamais déformée, sur une copie floutée d'elle-même, avec le crédit en haut à droite (le bas appartient aux sous-titres). Testé le 22 novembre 2026 sur l'exemple de 12 lignes : 1 photo trouvée, 0 erreur de `prompts.py --strict`.

Sources utiles hors Commons (entrées `url`, crédit et licence recopiés de la fiche) : Library of Congress (loc.gov, beaucoup de domaine public américain), National Archives (catalog.archives.gov), Smithsonian Open Access (CC0).

## 3. Images 3D (open-3d-skills)

Pour les sujets « comment ça marche » : la glacière en bois, les latrines d'un château, la coupe d'une maison en terre de pionnier. Le skill `exploded-view` (ou `threejs-scene` pour un lieu) construit la scène dans une page HTML ; `frame-capture` l'enregistre :
```
python3 ~/.open-3d-skills/skills/frame-capture/scripts/serve.py scene-3d --port 8000
python3 ~/.open-3d-skills/skills/frame-capture/scripts/record.py http://127.0.0.1:8000/ scene-3d.mp4 --seconds 6 --fps 30 --size 1920x1080 --dpr 1
```
**Ce qui est branché aujourd'hui : des images fixes.** `hf_build.py` monte des images animées par GSAP, pas des clips vidéo. Extraire les instants utiles en PNG, puis les utiliser comme des photos :
```
"$FF" -y -ss 2.0 -i scene-3d.mp4 -frames:v 1 assets/photos/X01.png      # X01, X02... : un id par instant
```
```python
A("icebox-cut", "X01", "zoom", caption="3D reconstruction"),
```
Le mot « reconstruction » est obligatoire dans le `caption` (règle 2). Couleurs de la scène : celles de `styles.json`, pour rester dans l'univers de la chaîne. `site-check` peut vérifier la page avant l'enregistrement.

Pas repris : `cursor-rig`, `scroll-film`, `alpha-cutout`, `motion-assets` (outils de sites web, pas de vidéo YouTube).

## 4. Ce qui reste à part

- **Le moteur de film de `cinematic-film`** (une caméra continue sur un mur de photos, de cartes et de chiffres) produit son propre MP4. Il peut servir pour un Short ou une ouverture, mais il n'est pas branché sur `hf_build.py`. Sa voix peut venir de VoiceStudio : `tts_say.py --cmd 'voicestudio speak --voice "<voix>" --text-file {txt} -o {out} --overwrite'`.
- **Les cartes** (`make_map.py`) sortent des données pour ce moteur, pas une image : pour une carte dans la vidéo longue, passer par un insert `hand-drawn-visuals` ou une capture du moteur.
- **Les effets sonores** (`build_sfx.py`) restent retirés (`voix-musique.md` §5 : aucun effet mesuré sur la rétention). Ne les remettre qu'avec un test mesuré.
