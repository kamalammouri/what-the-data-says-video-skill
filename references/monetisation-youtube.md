# Monétisation YouTube (Programme Partenaire, AdSense) : ce que la vidéo doit respecter

Règles lues sur les pages officielles le 11 novembre 2026. Les relire avant une demande d'adhésion : elles changent. Sources en bas.

## 1. Les seuils (ce qu'il faut atteindre)

| Palier | Abonnés | Et l'un de ces critères | Donne |
|---|---|---|---|
| Financement par les fans | 500, plus 3 vidéos publiques en 90 jours | 3 000 h de visionnage qualifiées en 365 jours, ou 3 M de vues de Shorts en 90 jours | souscriptions, Supers, Shopping (pas de publicité) |
| Publicité (AdSense) | 1 000 | 4 000 h qualifiées en 12 mois, ou 10 M de vues de Shorts en 90 jours | revenus publicitaires |

- **À partir du 1er février 2027** (blog YouTube, 10 août 2026) : les nouveaux candidats devront avoir **8 000 h qualifiées en 365 jours ou 20 M de vues de Shorts en 90 jours**, toujours avec 1 000 abonnés. Les chaînes déjà admises ne sont pas touchées.
- **Heures qualifiées** : seulement les vidéos longues publiques. Ne comptent pas : les Shorts, les vidéos privées, non répertoriées ou supprimées, les vues achetées en publicité. Masquer ou supprimer une vidéo retire donc ses heures.
- **Autres conditions** : validation en deux étapes activée sur le compte Google, aucun avertissement actif pour non-respect du règlement, un compte AdSense pour YouTube relié, pays éligible, fonctionnalités avancées activées.
- Examen : environ un mois. Refus : appel sous 21 jours, nouvelle demande après 30 jours (90 après un second refus).
- Une chaîne sans mise en ligne ni post pendant 6 mois peut perdre la monétisation.

## 2. Ce que l'examinateur regarde

Il juge **la chaîne entière**, pas une vidéo : le thème principal, les vidéos les plus vues, les plus récentes, celles qui font le plus de durée de visionnage, les métadonnées (titres, miniatures, descriptions) et la page « À propos ». Une seule vidéo à problème parmi les plus vues suffit à faire refuser la chaîne.

## 3. Contenu « générique ou répétitif » (ex-« inauthentique ») : le risque de ce format

Refusé : un contenu « qui semble fait avec un gabarit » ou qui « paraît répétitif après plusieurs vidéos à la suite » ; les **diaporamas d'images, les récits à gabarit ou le texte défilant avec peu ou pas de narration, de commentaire ou de valeur éducative** ; le contenu généré par IA « avec des gabarits génériques » qui « donne une impression de production de masse ».
Accepté : la même intro et la même outro si le reste change ; une série où chaque vidéo a « un récit, un sujet ou un concept distinct » ; l'IA pour « visualiser un personnage et un récit que vous avez inventés » ou pour illustrer.

Ce format est un diaporama d'images générées avec une voix de synthèse : il passe seulement s'il est clairement un récit éducatif original. Donc, pour chaque vidéo :
1. **Un récit distinct.** Aucune phrase de 6 mots ou plus reprise mot pour mot d'un script déjà publié sur la chaîne, et aucune dans les 10 premières lignes. Les formules de la chaîne de référence (« You will be shocked by a terrifying truth », « To understand the scale of this nightmare… », les transitions du §3 du `SKILL.md`) sont des modèles de ton : on les **réécrit** à chaque vidéo. `ypp_lint.py` le vérifie.
2. **Une valeur éducative visible.** 3 à 6 sources nommées et datées dans la voix et dans la description, des chiffres à l'écran, un fact-check écrit (`facts.md`).
3. **Une narration dense et continue** (ratio parole ≥ 0,92 avec le lit musical), des plans en mouvement, des sous-titres : jamais d'image fixe sans voix.
4. **Pas de production de masse.** Une vidéo longue tous les 2 ou 3 jours au plus, aucun doublon, aucune vidéo republiée. 28 vidéos en 13 jours avec des doublons, c'est le profil que la règle vise.
5. **Un seul thème de chaîne** et un seul univers de miniatures.

## 4. Contenu réutilisé

Refusé : reprendre un contenu déjà en ligne « sans commentaire original significatif ni modification substantielle ». Pour ce format : ne jamais traduire ni paraphraser le script d'une vidéo d'une autre chaîne, ne jamais reprendre ses images, sa miniature ou son personnage. Refaire un **sujet** est permis ; le récit, les faits vérifiés, les images et le titre sont les nôtres. Musique : libre de droits avec sa licence gardée (`credits.csv`).

## 5. Contenu adapté aux annonceurs (titre, miniature, sujet)

- **Publicité complète** : romance, baisers, « discussions sur les relations amoureuses ou la sexualité sans référence aux rapports sexuels », éducation sexuelle non explicite.
- **Publicité limitée** : « titres ou miniatures à thème sexualisé (y compris les signaux trompeurs) », gros plan sur des parties du corps.
- **Aucune publicité** : miniature à contenu sexuel, discussion de pratiques sexuelles (fétiches, conseils, expériences), titre racoleur trompeur.
- Groupes protégés (origine, religion, sexe…) : en parler sans blesser reste monétisable ; dénigrer ou humilier un groupe ne l'est pas.
- Violences sexuelles : seul un traitement journalistique ou éducatif non explicite reste monétisable, et il est souvent limité.

Règles du format qui en découlent :
1. **Aucun mot sexuel ou de violence sexuelle dans le titre, le titre du Short, le texte de miniature ni les tags** (sex, rape, porn, orgasm, nude, naked, fetish, adult content…). `ypp_lint.py` bloque.
2. **Miniature** : personnages couverts, aucune pose suggestive (à genoux, penchée, décolleté, jambes nues), aucune promesse que la vidéo ne tient pas, aucun personnage en silhouette entièrement noire pour figurer une personne noire, aucun personnage copié d'une autre chaîne.
3. **Sujets à ne pas choisir sur une chaîne qui vise la monétisation** : viol et violences sexuelles, pornographie, pratiques sexuelles. Les sujets intimes (règles, attirance, corps) se traitent de loin, avec des données, sans le mot dans le titre.
4. **La promesse du titre est tenue dans la vidéo**, avec la première donnée avant 1:00.

## 6. Contenu modifié ou synthétique (case à cocher dans Studio)

À déclarer : un contenu **réaliste** fabriqué ou modifié (une vraie personne qui dit ou fait ce qu'elle n'a pas fait, un vrai lieu ou événement modifié, une scène réaliste qui n'a pas eu lieu). Pas nécessaire : une animation clairement irréaliste, l'aide de l'IA pour le script, la miniature, le titre, les sous-titres. Ce format (dessin animé, bonshommes bâton) n'y est pas obligé ; cocher « oui » ne réduit ni l'audience ni la monétisation, et l'omission répétée expose à une suspension. Garder « oui ». Ne jamais dessiner une personne réelle reconnaissable (les Loving : silhouettes de dos).

## 7. Atteindre les heures : ce que les chiffres de la chaîne disent

Studio, The Hidden Bargain, 26 oct. au 9 nov. 2026 : 55 h de visionnage au total, 27 h qualifiées, 12 abonnés.
- Heures par vidéo : la version 3:19 de « Black Men » a fait 22,3 h avec 5 426 impressions ; la version 12:15, 10,6 h avec environ 1 500 impressions ; « Soap » (12:31), 6,5 h en 24 h avec 97 vues, soit 4 min par vue. À impressions égales, une vidéo de 12 min qui retient rapporte plus d'heures ; une vidéo de 12 min qui ne retient pas (Privacy : 19 % vus, Bald : 24 %) n'est plus proposée.
- Ce qui a fait chuter la rétention : la promesse du titre repoussée après 1:00 (chute à 1:58 puis à 4:00 sur « Black Men » 12 min, les données n'arrivaient qu'à 8:45).
- Titre : 52 caractères et une question, 9,3 % de clics ; 75 à 91 caractères en deux questions, 3,3 à 7,2 %.
- Les Shorts amènent des vues (1 329 et 1 157) mais leurs heures ne comptent pas : ils servent à envoyer vers la vidéo longue (« Vidéo associée »).

## Sources
- YouTube Help, « YouTube Partner Program overview & eligibility » : https://support.google.com/youtube/answer/72851?hl=en
- YouTube Help, « YouTube channel monetization policies » : https://support.google.com/youtube/answer/1311392?hl=en
- YouTube Help, « Advertiser-friendly content guidelines » : https://support.google.com/youtube/answer/6162278?hl=en (sections Hateful, Controversial et Shocking lues seulement en résumé : à relire avant de traiter un tel sujet)
- YouTube Help, « Disclosing use of altered or synthetic content » : https://support.google.com/youtube/answer/14328491?hl=en
- YouTube Blog, 10 août 2026, « New opportunities to earn and changes to the YouTube Partner Program » : https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/
- YouTube Studio, onglet Revenus de la chaîne (seuils du palier « fans » : 500 abonnés, 3 000 h, 3 M de vues de Shorts), lu le 11 novembre 2026
