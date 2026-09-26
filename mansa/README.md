# MANSA — interface web locale

Une interface de discussion qui tourne sur ta machine et parle au **même agent**
que le terminal Claude Code : mêmes règles, même mémoire, mêmes outils.

## Démarrer

Double-clic sur **`MANSA.bat`**.

Le navigateur s'ouvre sur <http://127.0.0.1:8765>. Les dépendances s'installent
toutes seules au premier lancement.

Pour arrêter : `Ctrl+C` dans la fenêtre noire, ou ferme-la.

## Ce qui est branché

| Source | Chargement | Contenu |
|---|---|---|
| `CLAUDE.md` | à chaque conversation | objectif, règles non négociables, devoir de contradiction, format des recommandations |
| Mémoire projet | à chaque conversation | 8 fiches dans `~/.claude/projects/c--Users-Yanick-Desktop-BRVM/memory/` |
| MCP `brvm-server` | à la demande | cours, RSI, volumes, screener, historique temps réel |
| Fichiers du dossier BRVM | à la demande | Excel, scripts, données, `brvm-data-public` |
| Web | à la demande | Sikafinance, BRVM, Madis Invest |

Le panneau de gauche affiche en direct ce qui est réellement chargé. Si une
ligne passe au rouge, l'agent travaille sans cette source.

## Ce que tu vois pendant qu'il répond

Chaque appel d'outil s'affiche : `BRVM · get_indicators BICC`, `Recherche web`,
`Lecture CLAUDE.md`. Le point passe au vert quand l'outil a répondu. C'est
volontaire : tu dois pouvoir vérifier qu'il a bien rafraîchi les données avant
de te recommander quoi que ce soit.

Le coût de chaque réponse et le cumul de la session s'affichent sous celle-ci.

## L'interface

| Endroit | À quoi ça sert |
|---|---|
| **Conversations** | `Nouvelle conversation` en tête, puis les conversations ouvertes. La croix apparaît au survol et en supprime une |
| **Espaces** | Portefeuille, Watchlist, Étude bénéfices. Un clic envoie la question, ou `Ctrl 1` à `Ctrl 3` |
| Pastilles sous la saisie | Scanner le marché, Actualité, Déployer du cash |
| Trombone | liste ton dossier BRVM, un clic insère le nom dans la question |
| Icône à côté du bouton d'envoi | les six questions types, à modifier avant d'envoyer |
| Ligne du bas | ce qui est réellement chargé. C'est le garde-fou, elle reste visible en permanence |
| **Thème** | bascule clair/sombre, ton choix est retenu |
| **Aide** | rappel des raccourcis |

Raccourcis clavier : `Entrée` envoie, `Maj+Entrée` fait un retour à la ligne,
`Ctrl K` ramène le curseur dans la saisie, `Ctrl 1` à `Ctrl 3` ouvrent un espace,
`Échap` ferme les menus.

Le thème suit celui de Windows au premier lancement.

## Garde-fous

L'agent peut lire et écrire dans le dossier BRVM sans demander. C'est
nécessaire pour qu'il tienne le portefeuille et la mémoire à jour.

Les commandes shell destructrices sont bloquées côté serveur : `rm -rf`,
`format`, `del /s`, `shutdown`, `git push --force`, entre autres. La liste est
dans `BASH_INTERDIT` au début de `server.py`. Si une commande est bloquée,
l'agent te dit ce qu'il voulait faire et tu décides.

## Réglages

Modifiables par variable d'environnement avant lancement :

```
MANSA_PORT=8765            port d'écoute
MANSA_MODEL=claude-opus-5  modèle
MANSA_HOST=127.0.0.1       n'écoute que la machine locale
```

`MANSA_HOST` reste sur `127.0.0.1`. L'interface n'a pas d'authentification :
si tu l'exposes sur le réseau, n'importe qui sur ce réseau peut lire tes
fichiers et ton portefeuille à travers l'agent.

## Fichiers

```
mansa/
  MANSA.bat            lanceur
  server.py            serveur + pont vers le Claude Agent SDK
  static/index.html    interface
  requirements.txt     dépendances
  server.log           journal du dernier lancement
```

## En cas de problème

**« Address already in use »** : une instance tourne déjà. Ferme la fenêtre
noire précédente, ou change `MANSA_PORT`.

**Le panneau de gauche affiche « Serveur injoignable »** : le serveur s'est
arrêté. Regarde `server.log`.

**Une ligne rouge sur `CLAUDE.md` ou `MCP`** : vérifie que `CLAUDE.md` est bien
à la racine de `Desktop\BRVM`, et que `brvm-server` figure dans
`~/.claude.json`.

**L'agent donne des positions périmées** : `CLAUDE.md` fait foi. S'il contient
un vieux snapshot du portefeuille, l'agent le croira. Mets-le à jour.