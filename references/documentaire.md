# Plans documentaires : cartes, dates, extraits de sources (fusion du skill documentary-explainer-video)

Ajouté le 22 novembre 2026. Le skill `documentary-explainer-video` (fourni par l'utilisateur) décrit le style des chaînes d'histoire « sans présentateur » : cartes animées, itinéraires, cartes de date, extraits de sources surlignés. Il ne contenait pas de code : ces plans sont maintenant dessinés par `scripts/docfx.py` et montés par `hf_build.py`, **entre les images Flow** de la troupe. Ils ne coûtent aucune image Flow.

## 1. Les trois plans (dans `make_shots.py`)

| Helper | À l'écran | Quand l'utiliser |
|---|---|---|
| `DATE("1292", "Paris tax roll")` | grand chiffre blanc qui tombe lettre par lettre, barre de couleur, sous-titre en capitales | une date ou une heure clé, 2 à 3 s, au début d'un bloc |
| `CLIP(quote, mark, source, file="P01")` | carte papier légèrement inclinée, la citation exacte, `mark` surligné en jaune mot par mot, « Source: … » en bas ; la vraie page (`assets/photos/P01…`) floutée derrière | une phrase d'une source de `facts.md` que la voix cite ou résume |
| `MAP(places, route, fill, focus)` | carte sombre (Natural Earth, domaine public, `assets/maps/countries-50m.json`), pays de `fill` en couleur, villes qui s'allument avec leur nom, itinéraire qui se trace avec un point qui le parcourt, lente poussée vers `focus` | un lieu nouveau, un déplacement, une comparaison entre villes |

```python
DATE("1523", "Erasmus, The Inns"),
CLIP("within these five and twenty Years, nothing was more in Vogue in Brabant, than hot Baths", "hot Baths", "Erasmus, Colloquies (trans. Bailey)"),
MAP(["Paris", "Vienna"], route=["Paris", "Vienna"], fill=["FRA", "AUT"], focus="Paris", title="Two cities, two records"),
MAP([["Kill Devil Hills", 36.02, -75.67]], fill=["USA"], focus=["Kill Devil Hills", 36.02, -75.67]),   # lieu hors de docfx.CITIES
```
- `places` / `route` : noms de `docfx.CITIES` ou `[nom, lat, lon]`. `fill` : codes ISO3 (FRA, AUT, BEL, NLD, GBR, USA…). `view=[lon0, lat0, lon1, lat1]` force le cadre ; `zoom` (1,35 par défaut) règle la poussée.
- Testé le 22 novembre 2026 sur le début de medieval-bath-en (59 s) : `hyperframes check` 0 erreur, rendu 1 min 38, planche lue (surlignage visible, carte centrée sur Paris, itinéraire Paris → Vienne).

## 2. Règles (reprises du skill documentaire, adaptées à la chaîne)

- **Les faits à l'écran sont ceux de `facts.md`.** Un `CLIP` cite mot pour mot une phrase lue dans sa source ; jamais une citation reconstituée ou traduite présentée comme l'original (une traduction se crédite comme telle : « trans. Bailey »).
- **Une seule couleur d'accent** (celle des sous-titres, `--accent` de `hf_build.py`), fond sombre désaturé, étiquettes en capitales avec ombre. Jamais un plan figé : tout plan dérive lentement.
- **Rythme** : une coupe toutes les 2 à 6 s ; alterner plan de la troupe (Flow), plan documentaire (DATE, CLIP, MAP) et insert chiffré. Pas plus de 2 plans documentaires d'affilée.
- **Combien par vidéo de 12 min** : environ 4 à 8 `MAP`, 3 à 6 `CLIP`, 2 à 4 `DATE`. Ils remplacent des images Flow (moins de générations, moins de refus « activité inhabituelle ») mais ne remplacent pas la troupe, qui reste l'identité de la chaîne. Effet sur la rétention : **pas encore mesuré**, à juger à J+7.
- **Scènes dramatisées** : seulement avec la troupe en bonhomme bâton (Flow). Jamais une image générée présentée comme une archive, jamais une personne réelle reconnaissable dessinée de façon réaliste.
- **Son** (optionnel, non branché) : un souffle sur les transitions de carte. Les effets sonores restent retirés tant qu'aucune mesure ne les justifie (`voix-musique.md` §5).

## 3. Ce qui n'est pas repris

- Les étapes du skill documentaire (brief, recherche, script, voix, plan, animation) existent déjà dans ce skill avec leurs portes (`SKILL.md`) ; on n'en garde que le gabarit de **plan de scènes** : chaque ligne de `make_shots.py` indique déjà le plan, et un plan documentaire porte sa source.
- Le rendu Remotion de secours : HyperFrames fait le rendu ici.
- Les vues 3D et les objets en mouvement (avions, navires) : à faire avec `open-3d-skills` (`archives-3d.md` §3) si un sujet le demande.
