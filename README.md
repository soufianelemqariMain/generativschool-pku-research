# Phénylcétonurie (PKU) : comparer des observations publiées sur PAH

La phénylcétonurie (PKU) est le sujet de ce banc d’essai : une personne qui développe une méthode de recherche sur PAH peut partir de données traçables, comparer son idée à des références simples et restaurer exactement un résultat.

**Ce que vous obtenez :** 14 observations publiées, sept paires de variants, trois modèles de référence, deux scénarios pour un désaccord dans la source et une fiche d’hypothèse à examiner. Le parcours ci-dessous produit les données auditées, un rapport JSON et une copie restaurée identique, sans clé ni service externe.

**Statut : prototype de recherche.** Le calcul porte sur de la PAH purifiée issue d’E. coli, avec ou sans co-expression GroEL/ES. La ridge ne dépasse pas les références dans ce pilote. Il ne s’agit ni de données de patients, ni d’un outil de choix thérapeutique. Le scénario Généthon est hypothétique, sans affiliation ni partenariat.

[Article français](https://www.generativschool.com/pku-banc-essai-ouvert.html) · [Tutoriel illustré](https://www.generativschool.com/pku-banc-essai-ouvert-tutoriel.html) · [Archive autonome](pku-v1.0.1.zip)

## Sommaire

- [Un exemple concret](#exemple)
- [Installer depuis ce dépôt](#installation)
- [Aller des données au résultat](#parcours)
- [Lire les résultats et leurs limites](#resultats)
- [Architecture et contrats](#architecture)
- [Adapter à une autre étude](#extension)
- [Dépannage](#depannage)
- [Sources, droits et ressources](#sources)
- [Migration et archives](#migration)

<a id="exemple"></a>
## Un exemple concret

Pour Ala342Pro, les observations publiées conservent un témoin non détecté (limite inconnue) et une activité traitée de **9,9 ±0,7 % WT**. La différence arithmétique vaut **9,9 points WT**. Ce contraste peut servir à formuler une question de reproductibilité dans le même système ; il ne prouve pas une restauration chez une personne.

Après l’installation, `pku-public evaluate` calcule les comparaisons et `pku-public export` produit une fiche d’hypothèse. Cette fiche conserve l’origine de l’observation et propose les informations à recueillir pour une étude ultérieure. La collecte et les essais sont **non exécutés**. Les résultats de référence sont déjà consultables dans [le rapport livré](pku-v1.0.1/evidence/run/report.json) et [la fiche Ala342Pro](pku-v1.0.1/evidence/hypothesis-plan.json).

<a id="installation"></a>
## Installer depuis ce dépôt

Prérequis : Git, Python ≥3.9 avec `venv` et pip. Environnement effectivement vérifié : CPython 3.9.6, macOS 26.2 arm64. Cette version décrit la reproduction, pas une recommandation de version de production. Linux non vérifié ; Windows natif n’est pas pris en charge par la mesure `resource`. Le paquet utilise uniquement la bibliothèque standard. La roue fournie évite d’installer des outils de construction.

Depuis un répertoire de travail où le dépôt n’existe pas encore :

```sh
git clone https://github.com/soufianelemqariMain/generativschool-pku-research.git
cd generativschool-pku-research/pku-v1.0.1
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps evidence/generativschool_pku_public-1.0.1-py3-none-any.whl
.venv/bin/python -c 'import pku_public; print(pku_public.__version__)'
```

La dernière commande affiche `1.0.1`. Après le clone, l’installation et le parcours ne demandent aucun accès réseau. Alternative sans Git : extraire `pku-v1.0.1.zip` téléchargé depuis ce dépôt, entrer dans `pku-v1.0.1/`, puis reprendre à `python3 --version`. Son SHA-256 est `4b1c2484b43eca04ffbd2bf7dd313517fb8fc7568ceb7173ff7f8afa61229e34`.

<a id="parcours"></a>
## Aller des données au résultat

Rester dans `pku-v1.0.1/`. Les destinations ci-dessous doivent être inexistantes. `ingest` copie le lot D01 inclus, `audit` contrôle ses sources et données, `evaluate` exécute les comparaisons, `compare` confronte le résultat à la référence, `export` prépare la fiche, `restore` recalcule à partir du snapshot.

```sh
.venv/bin/pku-public ingest --out inputs
.venv/bin/pku-public audit --bundle inputs --out audit.json
.venv/bin/pku-public evaluate --bundle inputs --out run
.venv/bin/pku-public compare --run run --out comparison.json
.venv/bin/pku-public export --run run --out hypothesis.json
.venv/bin/pku-public restore --run run --out restored
.venv/bin/python -m json.tool comparison.json
.venv/bin/python -m json.tool hypothesis.json
```

Les preuves livrées constatent `status: ok`, **14 observations**, **7 variants**, une comparaison `passed` sur **68 comparaisons numériques**, un écart maximal **0.0** (tolérance `1e-10`) et une restauration `report_identical: true`. Ces sorties servent à vérifier une reproduction logicielle, pas la validité biologique d’une hypothèse.

Fichiers utiles : `audit.json` contient les admissions ; `run/report.json` les paires, paramètres et prédictions ; `comparison.json` la comparaison ; `hypothesis.json` la conception d’étude ; `restored/report.json` le rapport restauré. Afficher le rapport et vérifier son identité :

```sh
.venv/bin/python -m json.tool run/report.json
.venv/bin/python -c "from pathlib import Path; print(Path('run/report.json').read_bytes() == Path('restored/report.json').read_bytes())"
```

La dernière sortie attendue est `True`. Pour reproduire aussi la construction et les tests, Python, setuptools ≥58 et wheel ≥0.37 doivent être **déjà présents** dans l’environnement de construction ; ce parcours n’installe rien depuis Internet :

```sh
python3 scripts/verify.py --out /tmp/pku-verification-neuve
```

Choisir un autre chemin neuf si celui-ci existe. Le vérificateur construit une roue hors index, crée un environnement neuf, importe le module hors des sources, exécute **17 tests** et contrôle la CLI. L’audit d’un CSV volontairement altéré doit sortir avec le **code 2** : c’est le rejet attendu. Les [commandes et sorties conservées](pku-v1.0.1/evidence/commands.json) décrivent la preuve de référence.

<a id="resultats"></a>
## Lire les résultats et leurs limites


| Scénario | Modèle | MAE (points WT) | RMSE (points WT) |
|---|---|---:|---:|
| table3 | zero_effect | 4.942857142857 | 6.374502781730 |
| table3 | train_mean | 5.823809523810 | 7.277133135148 |
| table3 | ridge_activity_alpha1 | 6.732752897751 | 8.117432288710 |
| section3.3_Ile406Met | zero_effect | 5.128571428571 | 6.582335668829 |
| section3.3_Ile406Met | train_mean | 5.947619047619 | 7.565675412311 |
| section3.3_Ile406Met | ridge_activity_alpha1 | 6.890344251705 | 8.387384354747 |

Aucun modèle sélectionné. Les résultats négatifs et contre-performances sont conservés : Δ Ile406Met = −6,6 (tableau), −7,9 (texte). Ne pas convertir ces comparaisons d'erreur en preuve de traitement. La ridge n'apporte pas d'amélioration sur les deux baselines dans ce petit pilote.

La sortie `report.json` contient, pour chaque scénario, les sept paires avec activité témoin et traitée absolue, SD publiés, conflit et incertitude de Δ inconnue ; chaque prédiction contient six variants train et les paramètres ajustés. Le journal `admission.json` conserve source et décisions. Les résultats sont des calculs sur des moyennes publiées, pas des expériences biologiques réalisées ici.


La cible est l’activité traitée moins l’activité témoin, en points de pourcentage WT. Trois modèles sont effectivement exécutés : effet nul, moyenne des six variants d’entraînement, et ridge α=1 utilisant l’activité témoin/100. Chaque variant est exclu entièrement à son tour ; aucun réglage d’hyperparamètre ni sélection de modèle. L’adaptateur ESM est une piste non exécutée.

Sept variants d’une seule publication ne permettent pas de conclure à une généralisation. Les SD publiés ne donnent pas l’incertitude de la différence sans covariance. Zéro signifie non détecté avec limite non rapportée ; la normalisation WT reste ambiguë et les fractions de purification limitent la comparabilité. Aucun réplicat individuel ni intervalle calibré n’est reconstruit.

<a id="architecture"></a>
## Architecture et contrats

```text
pku-v1.0.1/
  src/pku_public/core.py     extraction, audit, paires et modèles
  src/pku_public/cli.py      commandes, snapshots et ressources
  src/pku_public/bundle/     CSV, XML source, notices et verrous
  tests/                    invariants et erreurs attendues
  scripts/verify.py          construction et reproduction complète
  evidence/                 roue et preuves de référence
  SHA256SUMS                intégrité de la distribution
```


`core.py` extrait le tableau XML, charge le CSV, valide les observations, constitue les paires, ajuste les modèles et compare le pilote. `cli.py` orchestre les commandes, snapshots et mesures. `bundle/` contient données, article source, notices, configuration et référence numérique. `tests/` couvre les erreurs métier et les invariants de séparation. `scripts/verify.py` vérifie l'installation indépendante. Le socle historique reste intact, à côté de ce projet.

Identité d'une observation : (source_id, source_locator, protein_ref, variant, system, intervention, endpoint). Pas d'identifiant patient. `value`/`sd` sont des pourcentages WT ; `tetramer_pct`/`tetramer_sd` sont des proportions de préparation, jamais des labels d'activité. Vide CSV devient `None`, les zéros restent explicites. Effectifs : trois purifications, neuf dosages au total, sans présumer neuf réplicats biologiques. Référence protéique NP_000268.1 et transcript NM_000277.2 conservés ; aucune conversion implicite.

Une paire relie deux conditions de même variant/source/système/endpoint. L'unité de cible est le point WT ; les deux activités absolues sont conservées. Une validation rejette paire incomplète, doublon, valeur non finie, unité inconnue, source/droits/contexte incompatibles et conflit perdu. Les splits excluent tous les enregistrements du variant test. Les paramètres (moyennes train, pente, intercept, α et échelle) figurent dans chaque prédiction. Toute préparation statistique utilise uniquement le train ; l'échelle 100 est une conversion d'unité fixée.

L'adaptateur courant est volontairement verrouillé à D01 : 14 observations, sept variants, extraction identique au XML, empreintes exactes. `audit` expose toutes les admissions ou la première cause de rejet bloquante ; il n'écarte jamais silencieusement une ligne pour poursuivre. `ingest` copie un bundle admis. `evaluate` réaudite, exécute et compare. `compare` recontrôle une exécution. `export` produit une fiche de conception. `restore` vérifie intégrité et code, copie puis recalcule le rapport, exigé identique.

Les manifestes SHA-256 couvrent données, contexte, configuration, référence et code. Le verrou de comparaison provient du paquet installé, pas du bundle candidat. Le snapshot inclut entrées, journal et résultats. Les hashes sont non signés et ne protègent pas contre une personne qui modifie simultanément code et verrous ; ils détectent la dérive accidentelle, pas une falsification hostile. Timestamps/ressources sont séparés du rapport déterministe. Refus des destinations existantes. Un arrêt peut laisser un dossier partiel, à inspecter et renommer avant nouvelle exécution.

Bibliothèque standard uniquement. Mesure RSS maximum du processus, durée murale et CPU de la commande d'évaluation, pas consommation électrique ni coût. Le parcours de vérification journalise aussi chaque durée externe. Pas d'API réseau dans le paquet, pas de poids IA, pas d'interface médicale. Les scores ne sont jamais transformés en recommandation.

<a id="extension"></a>
## Adapter à une autre étude

Cette version admet exclusivement D01 ; déposer un nouveau CSV dans le bundle actuel sera refusé. Étendre le framework implique une nouvelle version du contrat et un adaptateur spécifique, testés et relus, pas le remplacement silencieux du verrou.

1. Conserver la source primaire, DOI/URL, date de récupération, version, SHA-256 et section/table. Vérifier les droits de redistribution de chaque fichier et conserver attribution, notice et transformations. Accès gratuit ne signifie pas droit de redistribution. Exclure les données sans droits établis.
2. Définir les clés d'observation et un `context_id` stable pour chaque combinaison système, construction, intervention, méthode, normalisation, fraction et endpoint. Conserver références protéiques/transcripts versionnées. Repérer les mêmes mesures recopiées par plusieurs articles afin de ne pas les compter deux fois.
3. Ajouter un adaptateur qui produit les mêmes champs numériques et sémantiques, avec identifiants d'observation uniques. Traiter zéro/non-détecté/valeur inconnue séparément ; préserver SD, effectifs, limite de détection et réplicats bruts s'ils existent. Ne jamais fabriquer de réplication à partir de moyenne/SD.
4. Une paire exige mêmes source, variant, système, endpoint, unité et contexte analytique, seules les conditions d'intervention diffèrent comme déclaré. Une activité enzymatique HPLC en %WT ne se mélange pas avec abondance HepG2, génotype clinique ou endpoint séquence. Des unités convertibles exigent une conversion explicite, versionnée et testée. Des normalisations WT ambiguës restent séparées jusqu'à résolution.
5. Pour la première extension compatible, évaluer chaque étude/contexte séparément ; ne pas concaténer avec D01 sous les paramètres de cette version. Si plusieurs contextes par variant sont ultérieurement regroupés, l'exclusion doit porter sur le variant entier dans tous les contextes, et un test d'étude externe est nécessaire. Définir cette politique avant calcul et éviter les doublons de source primaire.
6. Ajouter fixtures provenant de la nouvelle source et tests d'extraction/unité, paires incomplètes, doublons, fuite par variant, droits absents, fichier altéré et conflits source. Ajouter un résultat de référence inspectable et figer les nouvelles empreintes seulement après relecture humaine. Réexécuter le parcours dans un venv neuf, conserver son archive et demander la revue du paquet figé.

L'interface de modèle est la fonction `fit(train, held_out)` : elle reçoit uniquement les paires train, retourne ses paramètres, puis la prédiction exploite la covariable témoin du variant test. Un futur modèle doit suivre cette séparation, sérialiser version et paramètres et interdire l'accès aux cibles test. Aucun choix d'hyperparamètre ne doit utiliser les plis test ; une procédure imbriquée exige davantage de données.

Le plan exporté propose Ala342Pro comme exemple de question à réfuter car le contraste publié est traçable. Ce n'est pas un choix de traitement ni la sélection automatique du plus grand score. L'effectif, le seuil de pertinence et les modalités expérimentales doivent être préenregistrés par l'équipe scientifique compétente ; cette livraison n'exécute aucun essai biologique.

La prochaine expérience utile est d’admettre une seconde étude compatible sous un contrat distinct, puis d’évaluer la généralisation entre études. Ce dépôt ne réalise pas encore cette étape. Pour une méthode nouvelle, commencer par une branche et les tests de séparation, conserver les références actuelles, puis publier une nouvelle version du paquet avec ses résultats et notices.

<a id="depannage"></a>
## Dépannage

| Symptôme | Action |
|---|---|
| Destination existante | Inspecter et conserver le dossier ; choisir un nouveau chemin de sortie. |
| `venv` ou pip absent | Préparer un Python disposant de ces composants ; ne pas installer le paquet dans le Python système. |
| `resource` absent | Utiliser l’environnement Unix vérifié ; Windows natif n’est pas pris en charge. |
| Nouveau CSV refusé | Le contrat D01 est verrouillé ; suivre la démarche d’adaptateur, sans changer les empreintes pour masquer le rejet. |
| Empreinte ou restauration différente | Comparer au manifeste et aux preuves, conserver le journal d’échec ; ne pas écraser la référence. |
| setuptools/wheel absents | Utiliser la roue incluse pour le parcours principal ; préparer séparément les outils avant la construction complète. |

<a id="sources"></a>
## Sources, droits et ressources

Source primaire : Pecimonova et al. (2019), [DOI 10.3390/genes10060459](https://doi.org/10.3390/genes10060459), tableau 3 et section 3.3. La copie XML, le relevé de téléchargement et le CSV adapté sont inclus. [Provenance détaillée](pku-v1.0.1/PROVENANCE.md). Le conflit Ile406Met est conservé dans deux scénarios, sans correction arbitraire.

- **Code et tests originaux : MIT**, copyright Soufiane Lemqari ; [licence](pku-v1.0.1/LICENSE).
- **Article source et données adaptées : CC BY 4.0**, avec attribution et transformations conservées dans [la notice du bundle](pku-v1.0.1/src/pku_public/bundle/NOTICE.md).
- **README, documentation technique et textes éditoriaux originaux : droits réservés**, aucune licence de réutilisation accordée. La publicité du dépôt ne modifie pas ces droits ; [portée des licences](pku-v1.0.1/NOTICE.md).

La preuve technique historique mesure 12 commandes en 6,678687 s murales cumulées ; l’évaluation y mesure environ 0,035 s murale interne, 0,029 s CPU et 23,7 Mo RSS maximum. Ce sont des mesures locales conservées, pas une promesse de performance. Aucun GPU, poids de modèle, API ou calcul cloud nécessaire. Coût réel global (agent, machine, énergie) inconnu.

<a id="migration"></a>
## Migration et archives

Le paquet `pku-v1.0.1/` et son ZIP sont conservés octet pour octet depuis [le dépôt historique au commit source](https://github.com/soufianelemqariMain/generativschool-experiments/tree/c89f8ec517a4a5bb340efb06b4f26d5ad2529bae/pku-v1.0.1). Le dossier versionné préserve les chemins ; le nom du dépôt reste sans version. Les anciens liens immuables restent accessibles. [Manifeste de ce dépôt](MANIFEST.json).

Pour approfondir : [architecture](pku-v1.0.1/ARCHITECTURE.md), [modèles](pku-v1.0.1/MODELS.md), [extension](pku-v1.0.1/EXTENSION.md), [article](https://www.generativschool.com/pku-banc-essai-ouvert.html) et [tutoriel](https://www.generativschool.com/pku-banc-essai-ouvert-tutoriel.html).

Auteur : Soufiane Lemqari (`soufianelemqariMain`).
