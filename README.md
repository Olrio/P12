# P12

Télécharger/cloner le dépôt P12 (branche master)

Créer un environnement virtuel dans le répertoire P12 créé localement : python -m venv env

activer l'environnement virtuel : source env/bin/activate (Linux) ou env\\Scripts\\activate.bat (terminal Windows) ou env\\Scripts\\activate.PS1 (Windows PowerShell)

installer les modules requis à partir du fichier requirements.txt : pip install -r requirements

Cette API utilise PostgreSQL pour la gestion de la base de données. 
PostgreSQL doit donc être installé localement.

Sous Windows :  
    - Télécharger l'installer via le site https://www.enterprisedb.com/downloads/postgres-postgresql-downloads  
    - Installer PostgreSQL en suivant les instructions de l'assistant 
d'installation

Se placer dans le dossier EpicEvent/

Lancer le serveur avec la commande python manage.py runserver