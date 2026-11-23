# Publication : titre, miniature, description, Short, réglages

Rien n'est publié par le skill : il prépare `livraison/`, l'utilisateur colle dans YouTube Studio. Le trafic de la chaîne vient de l'accueil (50 %) et du flux Shorts (37 %), la recherche 3 % (Studio, 8 novembre 2026) : le titre et la miniature décident presque tout, la description sert l'examinateur du Programme Partenaire.

## 1. Titre

- Gabarit : **« Do [Women/Men] Really [X]? What the Data Says »**, une seule question, **≤ 60 caractères**. Mesure : 52 caractères, 9,3 % de clics ; deux questions de 75 à 91 caractères, 3,3 à 7,2 % (Studio, 11 novembre 2026).
- Compté par code, jamais de tête, et jamais écrit avec son décompte : `python scripts/yt/ypp_lint.py --title "…"` (deux titres ont été publiés avec « (53 caractères) »).
- Le titre est fixé à l'étape 1 et écrit en première ligne de `script.md` ; il ne change plus ensuite (la voix dit sa question mot pour mot avant 0:15).

## 2. Miniature : deux variantes couvertes, test A/B

1. Deux scènes Flow (`images-flow.md` §5) : A = le trio autour de l'objet qui dit le sujet ; B = le héros et l'héroïne avec l'objet. Personnages couverts, aucune pose suggestive, l'ami avec un vrai visage.
2. Le texte = **la question du titre en jaune sur deux lignes, au-dessus de la scène** (le gabarit de la miniature à 9,3 % ; « DO WOMEN REALLY?! », qui ne disait plus le sujet, a fait 6,6 %) :
   ```
   python scripts/thumb.py flow/thumbs/T1.jpg livraison/thumbnail-A.jpg "DO WOMEN REALLY|PREFER TALL MEN?" --fit
   python scripts/thumb.py flow/thumbs/T2.jpg livraison/thumbnail-B.jpg "DO WOMEN REALLY|PREFER TALL MEN?" --fit
   ```
   `--fit` réduit la scène à 70 % vers le bas (lettres d'environ 90 px ; à 80 % elles ne font que 58 px) sur un fond flouté et pose le texte dans la bande libérée : il ne couvre jamais un visage (Flow remplit le haut du cadre de têtes quoi que dise le prompt). Mesuré sur `thumb-blackmen-safe/S3.jpg` le 11 novembre 2026 : lettres de 58 px à 80 %, de 90 px avec `--fit=0.7`.
3. **Regarder chaque image produite** (outil Read) : visages entiers, texte lisible réduit à 320 px de large, rien de suggestif.
4. Dans Studio : « Tester et comparer » avec A et B (une troisième variante possible : A en `--fit=0.65`, lettres encore plus grosses, scène plus petite). Le résultat va dans `channel-results.md`.
5. `thumb.py` refuse un texte qui n'est pas une question de 3 à 8 mots ou qui porte un mot à risque.

### 2b. Le style mème (demande de l'utilisateur, 23 novembre 2026)

L'utilisateur veut ses miniatures dans le style de ses anciennes vignettes : la troupe en très gros plan, qui remplit le cadre et déborde en bas, avec des expressions exagérées (yeux exorbités injectés de sang, gouttes de sueur, dents serrées, dégoût ou regard en coin). Le fond est sombre, et un titre court de 2 à 4 mots est écrit en énormes lettres jaunes cernées de noir, directement sur l'image.
- **Scènes :** générées dans Meta Muse (`images-flow.md` §3b) ou dans Flow. Joindre la vignette de référence comme modèle de style et une image réussie de la troupe (F006 pour die-at-30) comme modèle des visages. L'image ne doit contenir ni texte ni chiffre.
- **Texte :** `python scripts/thumb.py T1.png livraison/thumbnail-A.jpg "DEAD BY 30?" --noband --force` donne des lettres d'environ 150 px posées sur l'image. `--force` est nécessaire, parce que le lint exige la question entière du titre.
- **Test A/B :** toujours garder une variante avec la question entière du titre (le format mesuré à 9,3 %). Le test de Studio tranche, et le résultat va dans `channel-results.md`.
- **Mesuré sur die-at-30 :** Muse ne laisse pas le tiers haut vide malgré la consigne, mais le texte peut couvrir le haut des têtes, comme sur la référence. Un vieux héros dessiné en gros plan dérive vers un visage réaliste (nez, rides).

## 3. Description, tags, hashtags (agent `seo-metadata-editor`)

L'agent écrit `desc.txt`, `short_desc.txt`, `tags.txt` et les passe à son propre lint (`meta_lint.py`). Ce que la description doit contenir pour cette chaîne :
- lignes 1 et 2 : la question du titre dans les mots que les gens tapent (`keywords.md`), puis le chiffre de l'étude principale ;
- un paragraphe de 60 à 120 mots, les chapitres de `chapters.md` (temps réels), **les 4 à 7 sources** de `## Sources` (auteur, année, titre, lien), la question finale, une ligne `▶ Watch next:` vers la meilleure vidéo du thème, la ligne d'abonnement, la mention de la musique si elle est en CC BY, et « Narration and illustrations are AI-generated » ;
- 3 hashtags de thème (`#Psychology #Dating` + un du sujet), jamais d'histoire ni de préhistoire ;
- tags : 10 à 15, ≤ 500 caractères, les requêtes réelles d'abord ; aucun mot à risque.

## 4. Le Short d'appel (obligatoire)

78 % des vues de la vidéo du savon venaient des suggestions, donc de son Short (1 157 vues en 13 h, Studio, 11 novembre 2026) ; le Short « Bald » a fait 1 256 vues. Les heures d'un Short ne comptent pas pour le Programme Partenaire : il sert à envoyer vers la vidéo longue.
- Fichier : `short.mp4` = le chapitre 1 (`montage.md` §5), qui s'arrête sur « But that number hides something ».
- Titre : la question seule, puis 2 hashtags (`Do Women Really Prefer Tall Men? #Dating #Psychology`), ≤ 100 caractères, première lettre vérifiée.
- Description : deux phrases qui finissent sur la question ouverte, `▶ Full answer: <lien de la longue>`, `#shorts` et deux hashtags du sujet.
- Mise en ligne **le même jour, après la vidéo longue**, et dans Studio : Détails → **Vidéo similaire** = la vidéo longue. Sans ce lien, le Short n'envoie personne.

## 5. Réglages dans Studio

| Champ | Valeur | Pourquoi |
|---|---|---|
| Heure | **13:00 ET** = 18:00 à Casablanca le 11 novembre 2026 ; recalculer la date choisie : `python -c "from datetime import datetime;from zoneinfo import ZoneInfo as Z;print(datetime(2026,11,14,13,tzinfo=Z('America/New_York')).astimezone(Z('Africa/Casablanca')))"` | la seule vidéo publiée à 13 h ET a fait 269 vues, les quatre publiées entre 18 h et 20 h ET 4 à 37 ; les heures allaient de 02:00 à 20:09 ET (audit du 8 novembre) |
| Cadence | **une vidéo longue tous les 2 ou 3 jours**, deux jours au moins entre deux | 30 vidéos en 16 jours avec des doublons = « production de masse » (`monetisation-youtube.md` §3) |
| Catégorie, langue | Éducation ; English (United States) pour la vidéo et les métadonnées | catégories mélangées et deux vidéos déclarées en français (audit du 8 novembre) |
| Contenu modifié ou synthétique | oui | `monetisation-youtube.md` §6 |
| Public | pas conçue pour les enfants ; commentaires activés avec la retenue des commentaires inappropriés | — |
| Écran de fin | sur les 15 dernières secondes : « vidéo la plus adaptée au spectateur » + bouton S'abonner | 0,0 % de clics sur toute la chaîne : il n'était jamais posé (audit du 8 novembre) |
| Playlist | « What the Data Says » | une série, un thème |
| Commentaire épinglé | la question finale de la vidéo | — |
| Doublage automatique | laissé comme il est réglé sur la chaîne | aucune mesure sur cette chaîne |

Avant de publier : aucun doublon (`yt-dlp --flat-playlist --print title "https://www.youtube.com/@hiddenbargain/videos"`), validation en deux étapes du compte Google active.

## 6. Les deux fichiers texte de `livraison/`

`titre-description-tags.txt` (les libellés sont lus par `ypp_lint.py`) :
```
TITLE
Do Women Really Prefer Tall Men? What the Data Says

THUMBNAIL TEXT
DO WOMEN REALLY|PREFER TALL MEN?

DESCRIPTION (paste as is)
<le contenu de desc.txt, avec la section « Sources: » et ses 4 à 7 lignes datées>

TAGS (comma separated)
<le contenu de tags.txt>
```
`short-titre-description-tags.txt` : `SHORT TITLE`, `SHORT DESCRIPTION`, `TAGS`, sur le même modèle.

## 7. La porte de sortie

```
python scripts/yt/ypp_lint.py <dossier de travail>
```
**0 erreur** : titre au gabarit et ≤ 60 caractères, aucun mot à risque dans les titres, le texte de miniature et les tags, aucune phrase du script reprise d'un script déjà publié (il compare avec `../*/script.md`), 4 sources datées dans la description, voix en anglais. Chaque avertissement est corrigé ou accepté par écrit dans `livraison/publication.md`.
