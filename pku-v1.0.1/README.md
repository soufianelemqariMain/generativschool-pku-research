# PAH : comparer une réponse fonctionnelle publiée et préparer la prochaine étude

Auteur du framework : Soufiane Lemqari. Version 1.0.1, 16 octobre 2026. Code/tests MIT ; données et article scientifique tiers sous CC BY 4.0. Documentation technique et éditoriale originale réservée, aucune licence de réutilisation accordée ; voir NOTICE.md. Projet autonome Python ≥3.9, sans dépendance d'exécution. Testé sur macOS arm64/Python 3.9.6 ; Linux non vérifié, Windows non pris en charge par la mesure `resource`.

Le chercheur obtient une extraction auditée de 14 observations publiées, sept paires par variant, une comparaison hors pli de trois modèles, leurs paramètres, un journal d'admission et une fiche de conception d'essais. Chaque résultat peut être restauré avec les mêmes données et le même code. L'extension visée est une collection de paires variant/intervention/contexte documentées.

Le démonstrateur est borné à **PAH purifiée issue d'E. coli avec ou sans co-expression GroEL/ES**, Pecimonova et al. 2019. Ce n'est ni une mesure de réponse humaine ni un classement de traitements. Le scénario Généthon est hypothétique, sans affiliation. Le prototype n’est pas validé biologiquement.

## Parcours rapide hors réseau

Depuis ce dossier, avec Python, setuptools ≥58 et wheel ≥0.37 déjà disponibles pour construire :

```sh
python3 scripts/verify.py --out /tmp/pku-public-proof
```

Choisir un dossier inexistant. Cette commande construit une roue sans index, crée un venv neuf sans paquets système, installe la roue, importe le paquet hors du code source, exécute les tests et toute la CLI. Un audit volontairement altéré doit sortir avec code 2. Elle conserve les commandes, sorties, durées et ressources dans le dossier demandé. Aucun téléchargement ni cloud nécessaire. Une roue déjà construite figure dans `evidence/` ; elle permet l'installation sans outils de construction.

Voir [TUTORIAL.md](TUTORIAL.md) pour les commandes unitaires et résultats réellement obtenus. Les données, sources et références sont incluses dans la roue : aucune dépendance à un chemin privé ou au dossier de recherche historique.

## Ce que les calculs disent

La cible est activité traitée moins activité témoin, en **points de pourcentage WT** ; l'activité traitée absolue reste conservée. La ridge utilise uniquement l'activité témoin/100, connue avant intervention. Les sept variants sont successivement exclus en entier. Zéro effet, moyenne des six variants d'entraînement et ridge α=1 sont évalués sans recherche d'hyperparamètres ni sélection de modèle.

Le tableau 3 et le texte divergent pour Ile406Met : les deux scénarios sont calculés et signalés. Les moyennes/SD publiés restent des agrégats ; aucune reconstruction de réplicats ou intervalle calibré n'est effectuée. Les SD ne permettent pas de calculer une incertitude de différence sans covariance. Un zéro signifie « non détecté, limite non rapportée », jamais « inconnu ». La normalisation WT conditionnelle reste ambiguë. La sélection des fractions de purification varie selon la présence de tétramères et limite la comparabilité.

Les erreurs de la ridge ne démontrent pas une amélioration sur les baselines dans ce pilote. Les écarts et signes négatifs sont conservés. Sept variants d'une publication ne permettent pas d'estimer une généralisation à une autre étude, une autre intervention ou un patient.

## Documentation et réutilisation

- [ARCHITECTURE.md](ARCHITECTURE.md) : modules, modèle de données, intégrité et limites.
- [EXTENSION.md](EXTENSION.md) : admission d'une nouvelle étude et contrôles de compatibilité.
- [PROVENANCE.md](PROVENANCE.md) : relecture de source, unités et droits.
- [MODELS.md](MODELS.md) : modèles exécutés, interface future ESM non admise.
- `evidence/run/report.json` : paires, prédictions hors pli, paramètres et métriques.
- `evidence/hypothesis-plan.json` : exemple réel Ala342Pro et plan de collecte au niveau conception, non exécuté.

Le coût total réel, incluant agent, machine et énergie, est inconnu ; aucun achat ni calcul cloud commandé.

## Dossier français

[Article](https://www.generativschool.com/pku-banc-essai-ouvert.html) · [Tutoriel français](https://www.generativschool.com/pku-banc-essai-ouvert-tutoriel.html).

Les preuves techniques incluses sont celles du paquet source public-v2, version 1.0.1. Leurs résultats et leur provenance sont conservés. Le manifeste SHA256SUMS décrit cette distribution sélectionnée.
