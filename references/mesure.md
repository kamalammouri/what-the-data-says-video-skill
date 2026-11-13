# Mesure après publication (J+2 et J+7) et règle de décision

L'ancien skill ne relisait jamais Studio : ses normes venaient d'une autre chaîne et n'ont pas été corrigées quand les vidéos de 12 min retenaient 19 à 33 %. Ici, chaque vidéo ajoute une ligne à `channel-results.md` §4, et cette ligne décide de ce qui change dans le skill.

## 1. Lire Studio (lecture seule)

`scripts/yt/studio.mjs` ouvre une adresse dans l'onglet Studio du Chrome lancé par `scripts/flow/browser.mjs`, attend, imprime le texte visible et prend une capture. **Il ne clique sur rien** ; ne jamais lui ajouter un clic sur Enregistrer, Publier ou Supprimer.

Préparation : `node scripts/flow/browser.mjs` (laisser tourner) ; l'utilisateur vérifie dans la fenêtre qu'il est connecté et **sur la chaîne The Hidden Bargain** (on ne saisit aucun identifiant à sa place). `<ID>` = l'identifiant de la vidéo (la fin de son adresse).

```
export PLAYWRIGHT_DIR=C:/Users/kamalAmmouri/Desktop/nastro; mkdir -p mesure
node <skill>/scripts/yt/studio.mjs "https://studio.youtube.com/video/<ID>/analytics/tab-overview/period-default"   9000 mesure/<ID>-overview.png   > mesure/<ID>-overview.txt
node <skill>/scripts/yt/studio.mjs "https://studio.youtube.com/video/<ID>/analytics/tab-reach/period-default"      9000 mesure/<ID>-reach.png      > mesure/<ID>-reach.txt
node <skill>/scripts/yt/studio.mjs "https://studio.youtube.com/video/<ID>/analytics/tab-engagement/period-default" 9000 mesure/<ID>-engagement.png > mesure/<ID>-engagement.txt
```

| Onglet | Ce qu'on y lit |
|---|---|
| overview | vues, heures de visionnage, abonnés gagnés, sources de trafic (part des « Suggestions de vidéos » = l'effet du Short) |
| reach | impressions, taux de clics des impressions, résultat du test A/B de miniature |
| engagement | durée moyenne, % moyen vu, rétention à 30 s, courbe de rétention (lire la capture `.png` : le temps et la hauteur de chaque marche) |

Pour la courbe exacte, l'utilisateur peut exporter le CSV (Engagement → rétention d'audience → icône de téléchargement) : `python ~/.claude/skills/yt-retention/retention.py retention.csv --duration <s>` nomme la fuite d'accroche, les falaises et la pente. Le Short se lit avec les mêmes commandes et son propre identifiant.

- **J+2** : vues, impressions, taux de clics, part des suggestions. Studio a jusqu'à deux jours de retard et la rétention n'est pas encore calculée.
- **J+7** : les mêmes, plus les heures, le % vu, la rétention à 30 s et la chute (le temps de la plus forte perte après 0:30, le nombre de points, et la ligne de `script.md` dite à ce moment, retrouvée par `timing.json`).

Ajouter la ligne au tableau de `channel-results.md` §4, avec la décision. Moins de 500 impressions à J+7 : noter « trop peu de données », ne rien conclure.

## 2. Règle de décision

Lire dans cet ordre ; une seule cause, un seul changement par vidéo, pour savoir ce qui a joué.

| Constat à J+7 | Cause probable | Ce qu'on change | Où |
|---|---|---|---|
| **Clics < 5 %** (500 impressions ou plus) | la miniature ou le sujet, pas la vidéo | garder le titre ; passer à la variante de miniature gagnante du test A/B, ou refaire une scène où l'objet dit mieux le sujet, texte en `--fit=0.7` | Studio, puis `publication.md` §2 |
| Clics < 5 % sur deux vidéos de suite | la famille de sujets | relire les notes (a) et (b) des deux sujets ; recaler les seuils de (b) ; prendre le prochain sujet dans la famille de la vidéo à 9,3 % (un trait d'homme jugé par des femmes) | `sujets.md` §1 |
| **% vu < 35 %** et rétention à 30 s < 50 % | l'ouverture | scène en 2 lignes, question du titre avant 0:10, premier chiffre avant 0:30 ; baisser les plafonds du chapitre 1 dans le lint | `structure-ecriture.md` §2, `script_lint.py` |
| % vu < 35 % avec une falaise (10 points ou plus en moins de 30 s) | ce qui se disait à ce moment | histoire ancienne : la supprimer du format ; bloc sans chiffre à l'écran ou de plus de 100 s : resserrer la limite ; boucle ouverte absente : la rendre obligatoire. Écrire la règle et la faire vérifier par le lint | `structure-ecriture.md`, `script_lint.py` |
| % vu < 35 % sans falaise (pente régulière) | le rythme | blocs de 80 s (1 900 mots), un insert toutes les 20 s, une relance toutes les 60 s | `structure-ecriture.md` §2, `prompts.py` (`DATA_WARN`) |
| % vu < 30 % sur deux vidéos de suite, sans cause trouvée | la durée | proposer à l'utilisateur 8 min (4 blocs) pour la suivante et comparer les **heures pour 1 000 impressions** des deux durées | `brief.json`, `channel-results.md` |
| Suggestions < 30 % des vues | le Short ne renvoie pas | vérifier « Vidéo similaire » ; réécrire la première ligne du Short ; le publier dans l'heure qui suit la longue | `publication.md` §4 |
| **Clics ≥ 5 % et % vu ≥ 35 %** | le motif tient | refaire le même motif avec le sujet voisin de la banque ; ne rien changer au skill | `sujets.md` §3 |

Les deux seuils sont ceux fixés par l'utilisateur le 11 novembre 2026. 35 % vient de l'audit du même jour (« si elle tient au-dessus de 35 %, ce format de 12 min est le bon pour faire des heures » ; les 12 min mesurées font 19 à 33 %). 5 % est la moyenne de la chaîne (5,2 % de clics sur 16 126 impressions, audit du 8 novembre), entre les 3,3 % des titres longs et les 9,3 % du titre court. Les recaler quand le journal compte cinq vidéos.

Toute modification d'une norme s'écrit dans le fichier concerné **avec sa mesure et sa date**, et dans la colonne « Décision » du journal. Une norme sans mesure ne s'ajoute pas.

Comparer les vidéos entre elles par les **heures pour 1 000 impressions** : c'est la grandeur qui mène aux 8 000 h, elle réunit les clics, la durée et la rétention.
