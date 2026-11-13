# Choisir le sujet par les chiffres (étape 1)

L'utilisateur veut « le sujet qui rapporte le plus de vues ». On ne choisit donc pas à l'intuition : on note 3 à 5 candidats sur trois mesures, on retient le plus haut, et l'utilisateur valide.

## 1. La grille (chaque note de 0 à 3, total sur 9)

| Note | (a) Résultats de la chaîne (`channel-results.md`) | (b) Demande mesurée (`scripts/yt/keywords.py`, tableau « Demand per candidate subject ») | (c) Sécurité annonceurs (`monetisation-youtube.md` §5) |
|---|---|---|---|
| 3 | « Do Women Really Prefer [type d'hommes] ? » : le gabarit des deux vidéos longues les plus vues et du Short le plus vu ; l'audience est masculine à 92,6 % | 10 suggestions ou plus et médiane des 10 résultats les plus vus ≥ 100 000 vues | un trait neutre ou choisi (taille, humour, barbe, voix, métier), aucun groupe protégé, aucun mot du corps intime |
| 2 | « Do Men Really Prefer… ? » : même gabarit, jamais testé sur la chaîne | 5 suggestions ou plus, ou médiane ≥ 30 000 | touche l'âge, l'argent ou le physique : faisable, avec plus de soin dans les mots |
| 1 | même thème, autre forme de titre (1,1 à 6,8 % de clics) | au moins une suggestion | touche un groupe protégé (origine, religion, nationalité, handicap) : seulement sur demande écrite de l'utilisateur, sans jamais classer |
| 0 | autre format (« Why Evolution… » 0,3 à 3,6 %, « How Did Ancient Humans… » 2,3 à 3,7 %) | aucune suggestion | liste interdite ci-dessous : **éliminé**, quel que soit le total |

Les seuils de (b) sont des valeurs de départ posées le 11 novembre 2026 sans mesure : à recaler quand le journal de `channel-results.md` compte cinq vidéos (comparer la note b au nombre d'impressions à J+7).

Procédure :
1. Prendre 3 à 5 candidats dans la banque (§3) ou dans les demandes de l'utilisateur ; écarter ceux déjà publiés (`yt-dlp --flat-playlist --print title "https://www.youtube.com/@hiddenbargain/videos"`).
2. `python scripts/yt/keywords.py "do women prefer tall men" "do women prefer older men" … --out keywords.md` : une amorce par candidat, écrite comme on la tape (sans « really », sans « what the data says »).
3. **Chercher si le sujet existe déjà sur YouTube, avant de proposer quoi que ce soit** (consigne de l'utilisateur, 12 novembre 2026 : ne pas tomber sous la règle du contenu dupliqué). Le même `keywords.md` porte le tableau « 0 bis. Already on YouTube » : pour chaque amorce, les vidéos d'autres chaînes qui posent la même question, et parmi elles les « long data video » (8 min ou plus, un mot de données dans le titre : notre genre de vidéo). Lire les titres listés, le tri par mots ne comprend pas le sens.
   - « free » ou « asked, but no long data video found » : le candidat reste.
   - « a long data video exists » : ouvrir la vidéo citée (titre, chapitres, description). Le candidat ne reste que si l'on peut écrire en une ligne ce que la nôtre apporte (d'autres études, un autre angle, une autre réponse) ; sinon l'écarter. Jamais le même titre mot pour mot qu'une vidéo existante.
   - Ce que la règle de YouTube vise (`monetisation-youtube.md` §3) : le contenu repris d'autrui sans apport et les vidéos presque identiques en série. Un sujet déjà traité ailleurs n'est pas interdit ; une vidéo qui reprend le titre, le plan et les exemples d'une autre l'est. Le script reste donc écrit à partir des études lues, jamais à partir d'une vidéo existante.
4. Remplir le tableau candidat | a | b | c | **déjà sur YouTube (nombre, lien de la plus proche, ce que la nôtre apporte)** | total | une ligne de risque ; (c) = 0 élimine ; à égalité, la note (a) départage, puis (b), puis le nombre de suggestions (une amorce sans suggestion vaut 0 en (b), quelle que soit la médiane : ses résultats de recherche sont hors sujet, mesuré le 11 novembre 2026).
5. Vérifier le titre par code : `python scripts/yt/ypp_lint.py --title "Do Women Really Prefer Tall Men? What the Data Says"` (longueur, gabarit, mots à risque).
6. Montrer le tableau à l'utilisateur, avec la colonne « déjà sur YouTube », recommander le premier, attendre son choix. S'il veut un sujet noté 1 en (c) : lui montrer la règle, proposer la variante sûre, puis respecter son choix et l'écrire dans `brief.json` (`"risk_accepted"`).

## 2. Sujets interdits (note c = 0)

- Viol et violences sexuelles (« What Happened to Women After Rape? » : 23 % vus, publicité limitée, passée en privé le 11 novembre 2026).
- Pornographie et contenu adulte (« Does Watching Adult Content Hurt Relationships? » : 1,1 % de clics).
- Pratiques sexuelles, conseils et performances (« Orgasm » en titre : 6 vues).
- **Tout classement de groupes** : « which race / country / religion do women prefer », « ranked », « best », « worst ». Un sujet d'attirance porte sur un trait, pas sur une hiérarchie de personnes.
- Tout sujet qui implique des mineurs.

Un sujet d'attirance reste sur « ce que disent les données » : la vidéo rapporte des études, leurs limites et leurs contradictions ; elle ne défend jamais une thèse sur un groupe (`structure-ecriture.md` §3).

## 3. Banque de 15 sujets sûrs (titres comptés par code le 11 novembre 2026, tous ≤ 60 caractères)

La demande (b) n'est pas mesurée ici : la mesurer à l'étape 1 avec l'amorce indiquée. La colonne « où chercher » donne des familles de sources à vérifier par le fact-checker, pas des faits.

| # | Titre | Car. | a | c | Amorce pour `keywords.py` | Où chercher les données |
|---|---|---|---|---|---|---|
| 1 | Do Women Really Prefer Tall Men? What the Data Says | 51 | 3 | 3 | do women prefer tall men | enquêtes de préférences, données d'applis de rencontre, tailles des couples dans les recensements |
| 2 | Do Women Really Prefer Older Men? What the Data Says | 52 | 3 | 2 | do women prefer older men | écarts d'âge au mariage (recensements, Pew), préférences déclarées par âge sur les applis |
| 3 | Do Women Really Prefer Rich Men? What the Data Says | 51 | 3 | 2 | do women prefer rich men | revenus et mariage (recensements), expériences de speed dating, enquêtes interculturelles |
| 4 | Do Women Really Prefer Funny Men? What the Data Says | 52 | 3 | 3 | do women prefer funny men | psychologie de l'humour et de l'attirance, méta-analyses |
| 5 | Do Women Really Prefer Bearded Men? What the Data Says | 54 | 3 | 3 | do women prefer beards | expériences de notation de visages, effet de rareté |
| 6 | Do Women Really Prefer Muscular Men? What the Data Says | 55 | 3 | 2 | do women prefer muscular men | notations de silhouettes, écart entre ce que les hommes croient et ce que les femmes notent |
| 7 | Do Women Really Prefer Bad Boys? What the Data Says | 51 | 3 | 3 | do women prefer bad boys | traits de personnalité et relations courtes ou longues, études longitudinales |
| 8 | Do Women Really Prefer Confident Men? What the Data Says | 56 | 3 | 3 | do women prefer confident men | confiance, statut et attirance ; excès de confiance |
| 9 | Do Women Really Prefer Deep Voices? What the Data Says | 54 | 3 | 3 | do women prefer deep voices | hauteur de voix et attirance, études interculturelles |
| 10 | Do Women Really Prefer Men With Dogs? What the Data Says | 56 | 3 | 3 | do women like men with dogs | enquêtes d'applis de rencontre, expériences d'approche |
| 11 | Do Women Really Prefer Men Who Cook? What the Data Says | 55 | 3 | 3 | do women like men who cook | partage des tâches et satisfaction de couple, enquêtes d'emploi du temps |
| 12 | Do Women Really Prefer Men in Uniform? What the Data Says | 57 | 3 | 3 | do women like men in uniform | effet du vêtement et du statut perçu, expériences de notation |
| 13 | Do Men Really Prefer Blondes? What the Data Says | 48 | 2 | 3 | do men prefer blondes | expériences de terrain, notations de photos, données d'applis |
| 14 | Do Men Really Prefer Younger Women? What the Data Says | 54 | 2 | 2 | do men prefer younger women | âges recherchés et âges contactés sur les applis, écarts d'âge au mariage (adultes seulement) |
| 15 | Do Men Really Prefer Smart Women? What the Data Says | 52 | 2 | 3 | do men prefer smart women | speed dating et intelligence, diplôme et mariage |

Déjà publiés, à ne pas refaire sous le même titre : « Do Women Really Prefer Black Men? What the Data Says » (3:19 et 12:15), « Do Women Really Prefer Bald Men? What the Data Says » (12:06).
