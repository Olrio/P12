# P12

Télécharger/cloner le dépôt P12 (branche master)

Créer un environnement virtuel dans le répertoire P12 créé localement : python -m venv env

activer l'environnement virtuel : source env/bin/activate (Linux) ou env\\Scripts\\activate.bat (terminal Windows) ou env\\Scripts\\activate.PS1 (Windows PowerShell)

installer les modules requis à partir du fichier requirements.txt : pip install -r requirements

Cette API utilise PostgreSQL pour la gestion de la base de données. 
PostgreSQL doit donc être installé.

Sous Windows :  
&emsp;- Télécharger l'installer via le site https://www.enterprisedb.com/downloads/postgres-postgresql-downloads  
&emsp;- Installer PostgreSQL en suivant les instructions de l'assistant 
d'installation  
&emsp;- Créer la Database 'epicdb' et l'utilisateur principal 'olrio' (cf. 
la constante `DATABASE` du fichier `settings.py`)  
&emsp;&emsp;* lancer le SQL Shell (psql) en tapant psql dans la barre de 
recherche de Windows  
&emsp;&emsp;* taper ENTREE pour valider successivement les choix par défaut de 
`Server [localhost]`, `Database [postgres]`, `Port [5432]` et `Username 
[postgres]`  
&emsp;&emsp;* Entrer le mot de passe qui a été saisi lors de l'installation de 
Postgres  
  
Sous Linux :  
&emsp;- Dans le terminal, saisir `sudo apt-get install postgresql`  
&emsp;- Lancer le Shell de PostgreSQL au moyen de la commande `sudo -u postgres psql`  

Etape suivante - création de la base de données:  
&emsp;- L'invite de commande `postgres=#` est affichée   
&emsp;- Saisir `CREATE USER <user> WITH PASSWORD <password>;` pour créer 
l'utilisateur principal  
&emsp;- Saisir `CREATE DATABASE <database> OWNER <user>;` pour créer la base de données
&emsp;- Quitter le Shell en tapant `exit`  


Se placer dans le dossier EpicEvent/

Y copier le fichier .env contenant la SECRET_KEY nécessaire au projet
Ce fichier comporte également les informations nécessaires à l'association des applications avec la base de données:  
- nom de la base de données PostgreSQL <database>
- nom de l'utilisateur principal de la base de données <user>
- mot de passe de cet utilisateur <password>

Effectuer les migrations avec la commande `python manage.py migrate`

Créer un superutilisateur qui pourra se connecter au site Django admin : 
`python manage.py createsuperuser` en fournissant son `username`et son 
`password` 

Lancer le serveur avec la commande `python manage.py runserver`  

Se logger avec les `username` et `password` du superutilisateur juste créé.


Seuls les membres de l'équipe de gestion peuvent utiliser cette interface.  
Elle leur permet de créer les autres utilisateurs de l'entreprise relevant des équipes de vente et de support.  
Les membres de l'équipe de vente et de l'équipe de support se voient attribuer un identifiant (username) et un mot de passe.  
Ils peuvent envoyer des requêtes à l'API REST CRM via le logiciel **Postman** (https://www.postman.com/)  

Tout d'abord, il convient de récupérer un Token d'identification.  
Pour ce faire, envoyer une requête POST à http://127.0.0.1:8000/crm/login/ en renseignant dans le Body les champs `username` et `password`  

Si la requête réussit, la réponse retournera un Token de rafraichissement et un Token d'accès.  

**Le Token d'accès doit être inclus dans toute requête effectuée à l'API.**  
Pour Postman, il faut cliquer sur `Authorization` et sélectionner `Bearer Token` comme `Type`  
Puis copier la valeur du Token d'accès dans le champ `Token` à droite. 

Si le Token d'accès a expiré, il convient de le rafraichir.  
Envoyer une requête POST à http://127.0.0.1:8000/crm/token/refresh/ en renseignant dans le Body le champs `refresh` qui prend comme valeur le Token de rafraichissement obtenu lors du `login`  
Veiller à ce que l'onglet `Authorization` soit bien configuré sur `No Auth` (à ce moment là, l'utilisateur ne dispose plus de Token d'accès valide)  

Exemples de requêtes pouvant être faites à l'API :  
&emsp;- Récupérer la liste des clients : requête GET à http://127.0.0.1:8000/crm/clients/  
&emsp;- Créer un nouveau client : requête POST à http://127.0.0.1:8000/crm/clients/  
&emsp; Le Body doit comprendre les champs nécessaires à la création du Client, à savoir `first_name`, `last_name`, `email`, `phone`, `mobile` et `company_name`  

Noter que les erreurs et exceptions sont consignées dans le fichier CRM/log/debug.log
L'historique des connexions au site administrateur et à l'API est conservé dans le fichier CRM/log/login.log



