aperho
======

*Gestion des groupes d'AP*

Le but de l'application web AP-Rho consiste à faciliter la gestion des
groupes d'accompagnement personnalisé, telle qu'on la pratique au
lycée Jean Bart de Dunkerque. Cette gestion repose sur l'usage d'un
serveur WIMS, selon un protocole mis au point par Benoît Markey, et
mis en œuvre par lui-même et Gérard Dessingué durant les années
2013-2018.

La récolte des choix de groupes d'Accompagnement Personnalisé (AP) que
font les élèves s'effectue quelques semaines avant le démarrage des
nouveaux groupes. Cette « récolte » consistait initialement en une
copie des résultats d'un sondage supporté par la plate-forme WIMS du
lycée, puis du traitement des listes, le plus souvent en les imprimant
et en annotant à la main. Ensuite, quand les listes étaient décidées
par l'équipe pédagogique, il faut les communiquer aux conseillers
principaux d'éducation et les afficher aux élèves. Cette dernière
étape nécessite une remise en forme et de multiples vérifications, et
pour tout dire, elle constitue une « double saisie ».

Le but de l'application AP-Rho est d'éviter cette double saisie, et
idéalement, de permettre un fonctionnement sans papier superflu. Les
changements de groupes des élèves, le traitement des non-inscrits se
fait sur un écran. On peut imaginer de projeter cet écran pour un
travail collaboratif.

Quand le travail de constitution des groupes d'AP est fini,
l'application permet d'exporter les groupes dans un fichier de
traitement de texte au format ODF (Open Document Format), qui est une
norme ISO que l'on doit utiliser de préférence pour tous nos documents
pérennes.

Le fichier db.sqlite3.sample contient une base de données vide, qui permet
de se connecter la première fois avec login/passe = admin/administrator

L'administrateur doit d'abord créer une barrette, puis une période d'AP,
puis inscrire des profs pour la barrette, et jeter un coup d'œil aux
"cours d'AP", ce qui crée des cours par défaut, comme effet de bord.

Ensuite chaque prof peut se loger, modifier ses cours d'AP en temps et 
en heure.

Quand la période d'AP est en cours d'ouverture, les élèves peuvent s'inscrire.


