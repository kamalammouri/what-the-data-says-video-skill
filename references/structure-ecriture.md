# Structure de 12 minutes et règles d'écriture

Le script est en anglais américain, une phrase par ligne. Tout ce qui suit est vérifié par `python scripts/yt/script_lint.py script.md` (0 erreur avant la voix), sauf les lignes marquées « relecture ».

## 1. Pourquoi cette structure

Sur « Black Men » 12:15 (Studio, 8 novembre 2026), le titre promettait des données et la vidéo partait dans la préhistoire : chute à 1:58, nouvelle chute à 4:00, données à 8:45, 33 % vus. La version de 3:19, qui donne les chiffres tout de suite, a fait 58 %. La structure ci-dessous donne donc **un morceau de réponse dans la première minute, puis un chiffre nouveau toutes les 80 à 110 secondes**, et garde la réponse complète pour 9:30 : le spectateur a toujours reçu quelque chose et attend toujours quelque chose.

## 2. Le plan (≈ 2 000 mots, 1 920 à 2 160 ; 170 mots par minute)

| Chapitre de `script.md` | Temps | Mots | Contenu | Vérifié par le lint |
|---|---|---|---|---|
| 1. L'ouverture | 0:00–0:15 | ≤ 42 | Une scène concrète à la 2ᵉ personne (un bar, une appli, un mariage) qui se termine par **la question du titre, mot pour mot** | question finie avant 0:15 |
| | 0:15–1:00 | ≤ 118 | **Le premier chiffre qui répond en partie** (l'étude la plus parlante, nommée et datée), ce qu'il semble prouver, puis le virage : « But that number hides something. » | un chiffre après la question ; une des 2 dernières lignes commence par « But » ; chapitre ≤ 160 mots (c'est aussi le Short) |
| 2 à 7. Six blocs | 1:00–9:30 | 225–315 chacun | Un bloc = **une étude ou un jeu de données** (détail §2.1) | 80 à 110 s ; un chiffre par bloc |
| dont le bloc 4 | vers 6:00 | | **Le renversement** : le jeu de données qui contredit la croyance de départ | relecture |
| 8. La réponse honnête | 9:30–11:00 | ≈ 255 | La réponse en **une phrase**, puis ce qui relève de la préférence individuelle et ce qui relève du biais social (ce que l'on voit, ce que l'on croit devoir vouloir) ; ce que les données ne permettent pas de dire | début entre 9:00 et 10:00 |
| 9. Le retour | 11:00–12:00 | ≈ 170 | **Retour à la scène d'ouverture**, relue avec ce que l'on sait maintenant ; dernière ligne = **une question au spectateur** | dernière ligne finit par « ? » |

Sur toute la vidéo : **une relance toutes les 60 à 90 s** (une ligne qui finit par « ? » ou qui commence par « But ») ; le lint refuse 90 s sans relance.

### 2.1 Un bloc (80 à 110 s)

1. **L'affirmation** (2 ou 3 lignes) : ce que les gens croient, ou la question que l'étude a posée. Formulée comme une croyance (« the claim », « you have heard »), jamais comme un fait.
2. **L'étude** (3 ou 4 lignes) : qui, quand, combien de personnes, comment. Nom et année dits dans la voix.
3. **Le chiffre** (1 ou 2 lignes) : un seul nombre, en lettres dans le script, **affiché à l'écran** par un insert (`D(...)` dans `make_shots.py`).
4. **Ce que le chiffre ne dit pas** (3 à 5 lignes) : la limite de l'échantillon, ce qui est déclaré contre ce qui est fait, la moyenne qui cache la dispersion.
5. **La boucle ouverte** (1 ligne) : la question que ce bloc laisse et que le suivant traite (« So what happens when nobody is watching? »).

Ordre conseillé des six blocs : ce que les gens **disent** vouloir (enquêtes) ; ce qu'ils **font** (applis, speed dating) ; ce qu'ils **épousent** (recensements) ; **le renversement** ; **pourquoi** on y croit (médias, biais de disponibilité) ; **ce que cela fait** aux personnes concernées.

### 2.2 L'histoire ancienne

Une preuve courte, jamais un décor : **30 s au plus par passage (85 mots), dans 2 blocs au plus**. Jamais une chaîne de civilisations (tribu, Rome, Égypte, Moyen Âge) : c'est ce qui a fait partir les spectateurs à 1:58.

## 3. Écriture

- **2ᵉ personne** : la scène d'ouverture, le retour et au moins une ligne par bloc parlent à « you » (2 « you » ou plus pour 100 mots).
- **Phrases de 11 à 13 mots en moyenne, jamais plus de 25** : une ligne = un clip de voix = une image.
- **Formulations sûres** : « on average », « in this data set », « the women in this study », « seven in ten said ». Jamais « women prefer… », « men always want… » sans cette précaution : le lint refuse toute généralisation nue sur un groupe. La croyance se cite comme croyance (« the claim that… »).
- **4 à 7 sources nommées et datées**, dites dans la voix (« In twenty seventeen, the Pew Research Center… ») et listées sous `## Sources` (`- Nom, année, titre, lien`). Le lint vérifie que chaque nom de la liste est prononcé.
- **Chiffres en lettres** dans les lignes dites ; les chiffres en chiffres vont dans les inserts.
- **Aucune phrase reprise** d'un script déjà publié (`ypp_lint.py` compare avec `../*/script.md`) ni des formules de l'ancienne chaîne de référence (« You will be shocked by a terrifying truth », « To understand the scale of this nightmare »… : liste `FORMULAS` de `script_lint.py`). YouTube refuse le « contenu à gabarit » (`monetisation-youtube.md` §3).
- **Aucun mot à risque** (sex, rape, porn, orgasm, nude, naked, fetish, adult content…) dans le titre, le texte de miniature et les tags ; dans la voix, parler d'attirance, de couple, de rencontre.
- Pas de « in this video », pas d'appel à s'abonner dans la voix : l'écran de fin et le commentaire épinglé s'en chargent.
- Public : des hommes américains de 25 à 65 ans (29 % ont 55 ans ou plus). Ton posé, unités et orthographe américaines, pas d'argot de génération.
- Aucune personne réelle vivante décrite physiquement ; les chercheurs sont nommés, pas dessinés.

## 4. Gabarit de `script.md`

```
# Do Women Really Prefer Tall Men? What the Data Says

## Chapter 1 — <nom du chapitre YouTube, 3 à 5 mots>
<scène, 2 ou 3 lignes>
So, do women really prefer tall men?
<étude nommée et datée, premier chiffre>
<ce qu'il semble prouver>
But that number hides something.

## Chapter 2 — <bloc 1>
…
## Chapter 8 — <la réponse honnête>
## Chapter 9 — <le retour à la scène>
<dernière ligne : une question au spectateur>

## Sources
- Pew Research Center, 2017, Intermarriage in the U.S. 50 Years After Loving v. Virginia, <lien>
```

Exemple miniature de 12 lignes (chiffres inventés, pour tester les scripts seulement) : `assets/example/script.md`.
