# P12

## Télécharger/cloner le dépôt P12 (branche master)

Créer un environnement virtuel dans le répertoire P12 créé localement : `python -m venv env`

activer l'environnement virtuel :  
`source env/bin/activate` (Linux)  
ou `env\\Scripts\\activate.bat` (terminal Windows)  
ou `env\\Scripts\\activate.PS1` (Windows PowerShell)

installer les modules requis à partir du fichier requirements.txt : `pip install -r requirements`

Cette API utilise PostgreSQL pour la gestion de la base de données. 
PostgreSQL doit donc être installé.

## Installation de PostgreSQL

Comme utilisateur principal (`<user>`), il est recommandé d'utiliser votre nom d'utilisateur de session Linux, Windows ou Mac.  


**Sous Windows :**  
&emsp;- Télécharger l'_installer_ via le site https://www.enterprisedb.com/downloads/postgres-postgresql-downloads  
&emsp;- Installer PostgreSQL en suivant les instructions de l'assistant 
d'installation  
&emsp;- Créer la Database `<database>` et l'utilisateur principal `<user>`  
&emsp;&emsp;* lancer le SQL Shell (psql) en tapant `psql` dans la barre de 
recherche de Windows  
&emsp;&emsp;* taper `ENTREE` pour valider successivement les choix par défaut de 
`Server [localhost]`, `Database [postgres]`, `Port [5432]` et `Username 
[postgres]`  
&emsp;&emsp;* Entrer le mot de passe qui a été saisi lors de l'installation de 
Postgres  
  
**Sous Linux :**  
&emsp;- Dans le terminal, saisir `sudo apt-get install postgresql`  
&emsp;- Lancer le Shell de PostgreSQL au moyen de la commande `sudo -u postgres psql`  

Etape suivante - création de la base de données:  
&emsp;- L'invite de commande `postgres=#` est affichée   
&emsp;- Saisir `CREATE USER <user> WITH PASSWORD <password>;` pour créer 
l'utilisateur principal. ATTENTION utiliser des simples guillemets `'` et non `"`
&emsp;- Saisir `CREATE DATABASE <database> OWNER <user>;` pour créer la base de données
&emsp;- Quitter le Shell en tapant `exit`  

## Configuration des applications
Se placer dans le dossier EpicEvent

Y copier le fichier .env contenant la SECRET_KEY nécessaire au projet.  
Ce fichier comporte également les informations nécessaires à l'association des applications avec la base de données:  
- nom de la base de données PostgreSQL `<database>`
- nom de l'utilisateur principal de la base de données `<user>`
- mot de passe de cet utilisateur `<password>`

Effectuer les migrations avec les commandes  
`python manage.py makemigrations authentication`  
`python manage.py makemigrations CRM`  
`python manage.py migrate`  

Créer un superutilisateur qui pourra se connecter au site Django admin : 
`python manage.py createsuperuser` en fournissant son `username`et son 
`password` 


## Utilisation du site d'administration
Lancer le serveur avec la commande `python manage.py runserver --insecure`
Ouvrir un navigateur à l'adresse `http://127.0.0.1:8000/admin/login/`
Se logger avec les `username` et `password` du superutilisateur juste créé.


Seuls les membres de l'équipe de gestion peuvent utiliser cette interface.  
Elle leur permet de créer les autres utilisateurs de l'entreprise relevant des équipes de vente et de support.  

## Utilisation de l'API CRM

Les membres de l'équipe de vente et de l'équipe de support se voient attribuer un identifiant (username) et un mot de passe.  
Ils peuvent envoyer des requêtes à l'API REST CRM via le logiciel **Postman** (https://www.postman.com/)  

Tout d'abord, il convient de récupérer un Token d'identification.  
Pour ce faire, envoyer une requête POST à http://127.0.0.1:8000/crm/login/ en renseignant dans le Body les champs `username` et `password`  
Exemples JSON: 
```json 
{
  "username":"myusername", 
  "password":"mypassword"
}
```

Si la requête réussit, la réponse retournera un Token de rafraichissement et un Token d'accès.  
```json 
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NzQwMjAwMywiaWF0IjoxNjc3MzE1NjAzLCJqdGkiOiJhY2Q2MTJhOTQ0NmQ0ZmI1OTVlY2M5OTMwMmQ4ZTM3ZSIsInVzZXJfaWQiOjE2fQ.ivBzmZfoJpLgsz3kenOVZvQbq_IjqpurkitRe18y-hU",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3MzE5MjAzLCJpYXQiOjE2NzczMTU2MDMsImp0aSI6ImI0NDcyNzJjYThjMTQzMTk4MWFjMDk4ZjhhNTI3YWFmIiwidXNlcl9pZCI6MTZ9.QdkturB4OHwOtL0SBP6bYPKuQ8Q_MSL1qdtBps1Aug0"
}
```

**Le Token d'accès doit être inclus dans toute requête effectuée à l'API.**  
Pour Postman, il faut cliquer sur `Authorization` et sélectionner `Bearer Token` comme `Type`  
Puis copier la valeur du Token d'accès dans le champ `Token` à droite. 
![img.png](img.png)

Si le Token d'accès a expiré, il convient de le rafraichir.  
Envoyer une requête POST à http://127.0.0.1:8000/crm/token/refresh/ en renseignant dans le Body le champs `refresh` qui prend comme valeur le Token de rafraichissement obtenu lors du `login`  
Veiller à ce que l'onglet `Authorization` soit bien configuré sur `No Auth` (à ce moment là, l'utilisateur ne dispose plus de Token d'accès valide)  
![img_1.png](img_1.png)

Requête :
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NzQwMjAwMywiaWF0IjoxNjc3MzE1NjAzLCJqdGkiOiJhY2Q2MTJhOTQ0NmQ0ZmI1OTVlY2M5OTMwMmQ4ZTM3ZSIsInVzZXJfaWQiOjE2fQ.ivBzmZfoJpLgsz3kenOVZvQbq_IjqpurkitRe18y-hU"
}
```

Réponse:
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3MzE5NzgwLCJpYXQiOjE2NzczMTU2MDMsImp0aSI6IjcxNDhiNjAzZTYxYTRhNTliYTI0YmVjZjQwNjAzZTdkIiwidXNlcl9pZCI6MTZ9.l-fQZof07h6vaJHMBp-Bxd5zsW7VKEdvIspDyNsHQsc"
}
```


Exemples de requêtes pouvant être faites à l'API :  
&emsp;- Récupérer la liste des clients : requête GET à http://127.0.0.1:8000/crm/clients/  
Il est possible d'utiliser le filtre `?last_name__icontains=xxx` dans l'url pour récupérer tous les clients dont le nom (last_name) contient 'xxx'.  
Par exemple :  
Envoyer une requête GET à `http://127.0.0.1:8000/crm/clients/?last_name__icontains=vad`  
Retournera  
```json
[
    {
        "pk": 25,
        "first_name": "Leopold",
        "last_name": "Chevadon",
        "email": "popold@web.com",
        "company_name": "Chez Popold",
        "sales_contact": [
            {
                "id": 5,
                "last_name": "Skivol",
                "first_name": "Yvan"
            }
        ]
    },
    {
        "pk": 1,
        "first_name": "Dark",
        "last_name": "Vador",
        "email": "star@wars.com",
        "company_name": "Skywalker",
        "sales_contact": [
            {
                "id": 3,
                "last_name": "Antou",
                "first_name": "Yves"
            }
        ]
    }
]
```
&emsp;- Créer un nouveau client : requête POST à http://127.0.0.1:8000/crm/clients/  
&emsp; Le Body doit comprendre les champs nécessaires à la création du Client, à savoir `first_name`, `last_name`, `email`, `phone`, `mobile` et `company_name`  

Requête :
```json
{
    "first_name": "Billy",
    "last_name": "Zekid",
    "email": "cowbow@west.com",
    "phone": "8889845",
    "mobile": "11254589",
    "company_name": "Westernity"
}
```

Réponse (succès):
```json
{
    "pk": 38,
    "first_name": "Billy",
    "last_name": "Zekid",
    "email": "cowbow@west.com",
    "phone": "8889845",
    "mobile": "11254589",
    "company_name": "Westernity",
    "sales_contact": [
        {
            "id": 3,
            "last_name": "Antou",
            "first_name": "Yves"
        }
    ],
    "date_created": "2023/02/25 18:21",
    "date_updated": "2023/02/25 18:21"
}
```

La documentation complète de l'API peut être consultée à l'adresse : https://documenter.getpostman.com/view/19438945/2s93CSpB3L


## Journalisation
Noter que les erreurs et exceptions sont consignées dans le fichier CRM/log/debug.log  
L'historique des connexions au site administrateur et à l'API est conservé dans le fichier CRM/log/login.log

## Testing
L'ensemble des applications a été testé.  
La commande à effectuer est : `coverage run manage.py test`  
Le taux de couverture des tests est de 100 %.  
Un rapport html des tests peut être obtenu via la commande `coverage html` qui génère un fichier `index.html` dans le répertoire `htmlcov`.  

## Conformité PEP8
La conformité des scripts aux recommandations de la PEP8 peut être vérifiée au moyen de la commande `flake8 --exclude=*migration*`  
