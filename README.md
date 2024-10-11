# Begone — Listes de blocage :fr:

## Prérequis

Avant de commencer, assurez-vous d'avoir installé l'application
[Begone][begone-app] sur votre iPhone. Une fois l'application installée,
lancez-la et suivez les instructions pour l'activer en tant qu'application de
blocage d'appels sur iOS.

## Installation

Ouvrez [cette page](#installation) sur votre iPhone et suivez les instructions
ci-dessous :

1. Appuyez et maintenez le lien de la liste souhaitée ci-dessous et
   sélectionnez **Télécharger le fichier lié**.

   - [Liste complète][list-all]
   - [Numéros VOIP][list-voip]
     - [Numéros OnOff][list-onoff]
     - [Numéros Ubicentrex][list-ubicentrex]

2. Ouvrez l'application Begone et sélectionnez **Importer de nouveaux
   numéros**.

3. Sélectionnez **Fichiers**.

4. Importez le fichier que vous venez de télécharger.

## Contribution

### Configurer l'environnement de développement

1. Créez un nouvel environnement virtuel Python.

   ```bash
    python3 -m venv venv
   ```

2. Activez l'environnement virtuel.

   ```bash
    source venv/bin/activate
   ```

3. Installez les dépendances nécessaires.

   ```bash
   pip install -r requirements.txt
   ```

### Ajouter de nouveaux numéros à la liste de blocage

1. Mettez à jour le fichier `data/numbers.yaml` avec les nouveaux numéros que
   vous souhaitez bloquer.

2. Exécutez `make` pour générer les nouvelles listes dans le dossier `dist`.

[begone-app]: https://apps.apple.com/fr/app/id1596818195
[list-all]: https://raw.githubusercontent.com/danroc/begone-fr-list/refs/heads/main/dist/begone-fr-tout.xml
[list-voip]: https://raw.githubusercontent.com/danroc/begone-fr-list/refs/heads/main/dist/begone-fr-voip.xml
[list-onoff]: https://raw.githubusercontent.com/danroc/begone-fr-list/refs/heads/main/dist/begone-fr-onoff.xml
[list-ubicentrex]: https://raw.githubusercontent.com/danroc/begone-fr-list/refs/heads/main/dist/begone-fr-ubicentrex.xml
