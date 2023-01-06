# P12

Télécharger/cloner le dépôt P12 (branche master)

Créer un environnement virtuel dans le répertoire P12 créé localement : python -m venv env

activer l'environnement virtuel : source env/bin/activate (Linux) ou env\\Scripts\\activate.bat (terminal Windows) ou env\\Scripts\\activate.PS1 (Windows PowerShell)

installer les modules requis à partir du fichier requirements.txt : pip install -r requirements

Cette API utilise PostgreSQL pour la gestion de la base de données. 
PostgreSQL doit donc être installé localement.

Sous Windows :  
&emsp;- Télécharger l'installer via le site https://www.enterprisedb.
com/downloads/postgres-postgresql-downloads  
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
&emsp;- L'invite de commande `postgres=#` est affichée   
&emsp;- Saisir `CREATE USER olrio WITH PASSWORD 'toto123';` pour créer 
l'utilisateur principal  
&emsp;- Saisir `CREATE DATABASE epicdb OWNER olrio;` pour créer la base de données


Se placer dans le dossier EpicEvent/

Effectuer les migrations avec la commande `python manage.py migrate`

Créer un superutilisateur qui pourra se connecter au site Django admin : 
`python manage.py createsuperuser` en fournissant son `username`et son 
`password` 

Lancer le serveur avec la commande `python manage.py runserver`  

Se logger avec les `username` et `password` du superutilisateur juste créé.
