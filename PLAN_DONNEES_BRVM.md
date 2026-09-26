# Plan — reconstruire la chaîne de données BRVM

> ## État au 26/09/2026
>
> | Phase | État |
> |---|---|
> | 0 — Décisions | **fait** — dépôt `balletyanick/brvm-data`, **public** |
> | 1 — Scraper, cours | **fait** — 49 actions, jusqu'à 28 ans d'historique |
> | 2 — Indicateurs | **fait** — 32 colonnes, RSI vérifié au centième |
> | 3 — GitHub | **fait** — workflow en place, un run manuel réussi |
> | 4 — Rebrancher le MCP | **fait** — recette passée, 6 tests sur 6 |
> | 5 — Maintenance | garde-fous posés ; reste le 26 octobre à surveiller |
>
> **Points bloquants du plan, résolus :**
> - `BRVMC` en 404 → les indices ont **leur propre endpoint**,
>   `indice-donnees?alias_indice=BRVM-COMPOSITE`. Composite depuis 1998,
>   6 651 séances. Beta calculable.
> - Nombre d'actions → relevé sur la **fiche société** de richbourse, pas
>   déduit. La déduction donnait 8 119 714 titres pour SAFC contre 11 869 750
>   en réalité.
>
> **Reste à faire, côté Ballet :** lancer le workflow une fois à la main
> (Actions → *Mise a jour des donnees BRVM* → *Run workflow*) pour valider les
> trois nouvelles étapes depuis le runner. La collecte des cours, elle, a déjà
> tourné depuis GitHub sans être bloquée.

Objectif : ne plus dépendre du dépôt d'un tiers. Produire nos propres CSV,
les héberger sur notre GitHub, les rafraîchir tous les jours automatiquement,
et rebrancher le serveur MCP dessus.

---

## Rappel du problème

Le serveur MCP `brvm-mcp/server.py` lisait des CSV hébergés sur
`Fredysessie/brvm-data-public`. **Ce dépôt a été supprimé.** Quatre outils sur
cinq sont morts. Le code du serveur est intact : seule la source manque.

Point important découvert le 26/09 : **le serveur MCP ne calcule rien.** Il
recopie des CSV déjà remplis. Les 32 champs d'indicateurs étaient fabriqués par
une chaîne privée de l'auteur, jamais publiée. Il faut donc la refaire.

---

## Ce qui est déjà validé

### L'endpoint de données

```
GET https://www.richbourse.com/common/mouvements/technique-donnees
    ?symbole={TICKER}&complet=1

En-têtes obligatoires :
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    X-Requested-With: XMLHttpRequest
    Referer: https://www.richbourse.com/common/mouvements/technique/{TICKER}
```

Réponse `application/json` :

```json
{
  "ohlc":    [[timestamp_ms, ouverture, haut, bas, cloture], ...],
  "volume":  [[timestamp_ms, volume_titres], ...],
  "complet": true
}
```

Pour les **indices**, la clé est `cours` au lieu de `ohlc`, avec 2 cases par
ligne au lieu de 5.

**Sans `&complet=1`, l'endpoint ne renvoie que 5 ans.** Avec, il renvoie tout.

### Testé le 26/09/2026, 8 tickers sur 9

| Ticker | Séances | Depuis |
|---|---|---|
| SNTS | 6 515 | 1998 |
| SHEC | 4 945 | 1998 |
| ETIT | 4 857 | 2006 |
| BOABF | 3 441 | 2011 |
| BOAS | 2 912 | 2014 |
| NSBC | 2 155 | 2017 |
| BICB | 352 | 2025 |
| BBGC | 2 | 24/09/2026 |

**Échec : `BRVMC`** (indice Composite) renvoie 404. Les indices utilisent un
identifiant différent, à trouver.

---

## Phase 0 — Décisions à prendre

- [ ] Nom du dépôt. Proposition : **`brvm-data`**
- [ ] Public ou privé ?
  - **Public** : le MCP lit sans authentification, plus simple
  - **Privé** : le MCP doit envoyer un jeton, plus prudent vis-à-vis des
    conditions d'utilisation de richbourse
- [ ] Vérifier les conditions d'utilisation de richbourse.com avant de publier
      un dépôt public

---

## Phase 1 — Le scraper, cours seulement

**But** : produire les 5 fichiers de cours par ticker, comme avant.

### 1.1 Liste des tickers

Reprendre `STOCK_TICKERS` de `brvm-mcp/server.py` (48 tickers) et
**ajouter `BBGC`** (Bridge Bank, cotée depuis le 24/09/2026). La liste est
écrite en dur dans le serveur, il faudra la mettre à jour aussi.

### 1.2 Table ticker → pays

Extraire le champ `URL_Ticker` des anciens CSV locaux
(`brvm-data-public/data/*/*.indicator.csv`). 66 tickers, 7 suffixes :
`.ci` (35), `.bj` (3), `.bf` (3), `.sn` (3), `.tg` (2), `.ml` (1), `.ne` (1).

Le figer dans un fichier `tickers.json` versionné.

### 1.3 Fichiers à produire

Par ticker, dans `data/{TICKER}/` :

| Fichier | Contenu |
|---|---|
| `{T}.daily.csv` | Date,Open,High,Low,Close,Volume — une ligne par séance |
| `{T}.weekly.csv` | agrégé depuis daily |
| `{T}.monthly.csv` | agrégé |
| `{T}.quarterly.csv` | agrégé |
| `{T}.yearly.csv` | agrégé |

**Règle d'agrégation** : Open = première séance de la période, High = max,
Low = min, Close = dernière séance, Volume = somme. Date = dernier jour de la
période (c'est ce que faisaient les anciens fichiers).

### 1.4 Robustesse

- Pause de 0,4 à 1 seconde entre deux tickers, pour ne pas marteler le site
- Un échec sur un ticker ne doit pas arrêter le lot
- **Ne jamais écraser un CSV existant par un fichier vide** : si la réponse est
  vide ou invalide, garder l'ancien et journaliser l'erreur

### 1.5 Vérification

Lancer sur les 49 tickers, compter les succès, comparer les dernières lignes
avec brvm.org pour 3 ou 4 titres.

---

## Phase 2 — Les indicateurs, calculés

**But** : produire `{T}.indicator.csv`, 32 colonnes, une seule ligne.

### 2.1 Les 32 colonnes, et d'où elles viennent

| Colonne | Origine | Format attendu |
|---|---|---|
| `Ticker` | constante | `NSBC` |
| `URL_Ticker` | table `tickers.json` | `NSBC.ci` |
| `Cours_Actuel` | dernière clôture | `22500.0` |
| `Variation_Cours` | (clôture − veille) / veille | **`+0,71%`** chaîne |
| `Volume_Titres` | dernier volume | `811.0` |
| `Volume_XOF` | volume × clôture | `11439000.0` |
| `Ouverture` | dernière ouverture | `20500.0` |
| `Plus_Haut` | dernier haut | `21880.0` |
| `Plus_Bas` | dernier bas | `20000.0` |
| `Cloture_Veille` | avant-dernière clôture | `20815.0` |
| `Beta_1_An` | **calcul, voir 2.3** | `1.09` |
| `RSI` | **calcul, voir 2.2** | `48.4` |
| `Capital_Echange` | volume ÷ nombre d'actions | `0.0001` |
| `Valorisation` | nb actions × clôture | `348757000000.0` |
| `1_Semaine_Plus_Haut` / `_Plus_Bas` | max / min sur la fenêtre | nombre |
| `1_Semaine_Variation` | (dernier / premier) − 1 | **décimal** `-0.0136` |
| idem pour `1_Mois_`, `1er_Janvier_`, `1_An_`, `3_Ans_`, `5_Ans_` | | |

> ⚠️ **Deux formats différents, à ne pas mélanger.**
> `Variation_Cours` est une **chaîne avec % et virgule** (`+0,71%`) : c'est
> comme ça que `get_market_overview` compte les hausses et les baisses.
> Les six `*_Variation` de période sont des **décimaux** (`-0.0136`) : c'est
> comme ça que `screen_market` filtre. Se tromper casse le filtrage
> silencieusement.

Fenêtres : 1 semaine = 5 séances, 1 mois = 21, 1 an = 252, 3 ans = 756,
5 ans = 1260. `1er_Janvier` = depuis la première séance de l'année en cours.

### 2.2 RSI 14 jours, méthode Wilder

```
variation[i]   = close[i] − close[i−1]
gain[i]        = max(variation, 0)
perte[i]       = max(−variation, 0)

moyenne initiale sur les 14 premières valeurs (moyenne simple)
puis lissage de Wilder :
    moy_gain[i]  = (moy_gain[i−1] × 13 + gain[i]) / 14
    moy_perte[i] = (moy_perte[i−1] × 13 + perte[i]) / 14

RS  = moy_gain / moy_perte
RSI = 100 − 100 / (1 + RS)
```

**Ne pas utiliser une moyenne mobile simple**, le résultat diffère et ne
correspondra pas aux RSI affichés ailleurs.

Contrôle : richbourse affiche le RSI dans l'attribut `title` d'un bloc
`rb-visible-stat` de la page technique. **À utiliser uniquement pour vérifier
notre calcul, jamais comme source.**

### 2.3 Beta 1 an

```
r_titre[i]  = rendement quotidien du titre
r_indice[i] = rendement quotidien du BRVM Composite
Beta = covariance(r_titre, r_indice) / variance(r_indice)
```

sur les 252 dernières séances communes.

**Dépendance** : il faut la série de l'indice Composite.
→ **Résolu le 26/09.** Ce n'était pas un identifiant à trouver mais un
endpoint différent :

```
GET /common/mouvements/indice-donnees?alias_indice=BRVM-COMPOSITE&complet=1
    Referer: /common/mouvements/indice/BRVM-COMPOSITE
```

L'alias est le nom long, pas le ticker court. Réponse `{ "cours": [[ts, v]] }`.
6 651 séances depuis le 16/09/1998. Les 18 indices sont collectés, la table de
correspondance ticker → alias est dans `scraper/indices.json`.

`Beta_1_An` est laissé **vide** quand le titre ne cote plus : un Beta « 1 an »
calculé sur 2019 pour un titre radié serait un chiffre faux présenté comme
frais.

### 2.4 Nombre d'actions

Table statique de 49 nombres, dans `actions.json`, nécessaire pour
`Valorisation` et `Capital_Echange`.

→ **Résolu le 26/09.** Relevé sur
`richbourse.com/common/apprendre/details-societe/{TICKER}`, champ
« Nombre de titres », par `scraper/faire_actions.py`. Relancé chaque jour par
le workflow, ce qui rattrapera le fractionnement Sonatel tout seul.

La déduction `capitalisation ÷ cours` a été essayée d'abord : elle donnait
8 119 714 titres pour SAFC contre **11 869 750** en réalité — une augmentation
de capital que les anciennes capitalisations ignoraient.

**À mettre à jour en cas d'augmentation de capital ou de fractionnement.**
→ **Sonatel passe de 100 millions à 1 milliard d'actions le 26 octobre 2026.**

---

## Phase 3 — GitHub

### 3.1 Créer le dépôt

Compte `Yanick005`, dépôt `brvm-data`.

```
brvm-data/
├── .github/workflows/maj.yml     ← le cron
├── scraper/
│   ├── collecte.py               ← phase 1
│   ├── indicateurs.py            ← phase 2
│   ├── tickers.json
│   └── actions.json
├── data/
│   ├── NSBC/
│   │   ├── NSBC.daily.csv
│   │   ├── NSBC.weekly.csv
│   │   ├── NSBC.monthly.csv
│   │   ├── NSBC.quarterly.csv
│   │   ├── NSBC.yearly.csv
│   │   └── NSBC.indicator.csv
│   └── ... (49 dossiers)
└── README.md
```

**Amorçage** : copier `brvm-data-public/data/` comme base, puis laisser le
scraper compléter. L'endpoint renvoyant tout l'historique, on peut aussi
repartir de zéro — plus propre, pas de mélange de deux sources.

### 3.2 Le workflow

`.github/workflows/maj.yml` :

```yaml
name: Mise a jour des donnees BRVM
on:
  schedule:
    - cron: "30 16 * * 1-5"    # 16h30 UTC, apres la cloture de 15h
  workflow_dispatch:            # bouton manuel
jobs:
  maj:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r scraper/requirements.txt
      - run: python scraper/collecte.py
      - run: python scraper/indicateurs.py
      - name: Commit
        run: |
          git config user.name "brvm-bot"
          git config user.email "bot@users.noreply.github.com"
          git add data/
          git diff --staged --quiet || git commit -m "Donnees du $(date +%F)"
          git push
```

GitHub Actions est **gratuit sur dépôt public**, et offre 2 000 minutes par
mois sur dépôt privé — un scraper de 49 tickers en consomme quelques minutes
par jour.

### 3.3 Sécurité

Le workflow a besoin du droit d'écriture :
Settings → Actions → General → Workflow permissions → **Read and write**.

---

## Phase 4 — Rebrancher le MCP

### 4.1 Une ligne à changer

Dans `brvm-mcp/server.py`, ligne 11 :

```python
BASE_URL = "https://raw.githubusercontent.com/Yanick005/brvm-data/main/data"
```

### 4.2 Ajouter BBGC

Ligne 13, `STOCK_TICKERS` : ajouter `"BBGC"`. Sans ça, Bridge Bank n'apparaît
ni dans le screener ni dans l'aperçu du marché.

### 4.3 Corriger le défaut d'origine

`screen_market` et `get_market_overview` **avalent les erreurs en silence** et
renvoient une liste vide. C'est ce qui a fait croire, le 16 septembre, qu'aucun
titre ne passait le filtre alors qu'il n'y avait aucune donnée.

À corriger : si **plus de la moitié** des tickers échouent, renvoyer une erreur
explicite au lieu d'un résultat vide.

### 4.4 Tests de recette

- [ ] `get_all_tickers` → 49 actions
- [ ] `get_indicators("NSBC")` → 32 champs, cours du jour correct
- [ ] `get_ticker_data("NSBC", "daily", 5)` → 5 dernières séances
- [ ] `screen_market(rsi_max=40)` → liste non vide, RSI cohérents
- [ ] `get_market_overview()` → hausses + baisses + stables = 49
- [ ] Comparer 3 cours avec brvm.org le même jour

---

## Phase 5 — Maintenance

### Ce qu'il faudra surveiller

| Événement | Action |
|---|---|
| **26 octobre 2026** | Fractionnement Sonatel 1→10. Mettre `actions.json` à 1 milliard. L'historique des cours sera-t-il rétroactivement ajusté par richbourse ? À vérifier ce jour-là |
| Nouvelle société cotée | Ajouter à `tickers.json`, `actions.json` et `STOCK_TICKERS` |
| Augmentation de capital | Mettre à jour `actions.json` |
| richbourse change son endpoint | Le workflow échouera. Mettre une alerte par email sur échec du job |

### Signal d'alarme

Ajouter au workflow un contrôle : **si la dernière date des CSV n'a pas changé
depuis 3 jours ouvrés, faire échouer le job.** C'est ce qui aurait signalé la
panne dès le premier jour au lieu de me laisser travailler sur des données
figées au 11 septembre pendant une semaine.

---

## Ordre d'exécution recommandé

| Étape | Ce qu'on gagne |
|---|---|
| **1.** Phase 1 + Phase 3, cours seulement | `get_ticker_data` remarche. Le montage est validé de bout en bout |
| **2.** Phase 2, indicateurs calculés | `get_indicators`, `screen_market`, `get_market_overview` reviennent |
| **3.** Beta et capitalisation | Les 2 derniers champs |
| **4.** Phase 4.3 et 5, garde-fous | On ne se refait plus avoir en silence |

Chaque étape laisse quelque chose qui fonctionne. Pas de grand chantier
inutilisable tant qu'il n'est pas fini.
