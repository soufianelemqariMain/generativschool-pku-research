# Tutoriel exécuté — version 1.0.1

Auteur : Soufiane Lemqari. Exécution locale le 16 octobre 2026, Python 3.9.6, macOS 26.2 arm64.

Depuis la racine du projet, choisir des destinations inexistantes :

```sh
python3 -m venv /tmp/pku-env
/tmp/pku-env/bin/python -m pip install --no-index --no-deps evidence/generativschool_pku_public-1.0.1-py3-none-any.whl
/tmp/pku-env/bin/python -c 'import pku_public; print(pku_public.__version__)'
/tmp/pku-env/bin/pku-public ingest --out /tmp/pku-inputs
/tmp/pku-env/bin/pku-public audit --bundle /tmp/pku-inputs --out /tmp/pku-audit.json
/tmp/pku-env/bin/pku-public evaluate --bundle /tmp/pku-inputs --out /tmp/pku-run
/tmp/pku-env/bin/pku-public compare --run /tmp/pku-run --out /tmp/pku-comparison.json
/tmp/pku-env/bin/pku-public export --run /tmp/pku-run --out /tmp/pku-hypothesis.json
/tmp/pku-env/bin/pku-public restore --run /tmp/pku-run --out /tmp/pku-restored
```

Ces opérations ont été exécutées par `scripts/verify.py` dans un environnement temporaire neuf, depuis un répertoire extérieur aux sources. Les chemins ci-dessus sont des équivalents lisibles ; `evidence/commands.json` conserve les arguments et sorties réels avec chemins temporaires anonymisés.

Sorties constatées : import `1.0.1` depuis le venv ; ingest/audit/evaluate `status: ok`, `observations: 14`, `variants: 7` ; comparaison `passed`, 68 comparaisons numériques, écart maximal **0.0** pour tolérance **1e-10** ; restauration `report_identical: true`. **17 tests réussis** depuis le paquet installé. L'audit du CSV volontairement altéré rejette avec code 2 et journal conservé dans `evidence/rejected.json`. Les autres commandes du parcours final ont le code attendu 0.

## Résultats numériques réellement recalculés

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

## Exemple exporté

Ala342Pro : témoin non détecté (limite inconnue), activité traitée publiée 9,9 ±0,7 %WT, différence arithmétique 9,9 points. La fiche demande si le contraste est reproductible dans le même système ; elle prévoit contrôles WT, variant, blancs et purification, et des critères d'échec de reproductibilité/comparabilité. Elle demande préenregistrement de précision/effectif, mesures brutes, limite de détection et normalisation. Le plan est une **conception non exécutée**, sans recette thérapeutique, sans classement des traitements.

## Ressources mesurées et limites

12 commandes, durée murale cumulée 6.678687 s. Commande d'évaluation : 0.035131833 s murales internes, 0.028522000 s CPU, RSS maximum du processus 23740416 octets. Les chronométrages externes sont dans le journal, différents de la mesure interne. Il s'agit d'un petit calcul CPU local, pas d'un benchmark généralisable. Aucun GPU ou service cloud ; coût total réel inconnu.

Pour reproduire tests et parcours complet avec construction hors index : `python3 scripts/verify.py --out /tmp/pku-new-proof`. Python/setuptools/wheel doivent déjà être présents ; la vérification n'installe rien depuis Internet. Les snapshots ne sont pas signés, la licence est vérifiée sur la copie XML, et aucune revue scientifique indépendante n'est prétendue. Pas de preuve de portabilité hors macOS dans cette livraison.

Les preuves livrées sont celles de la nouvelle exécution v1.0.1 via `scripts/verify.py`. Les commandes unitaires ci-dessus décrivent le parcours équivalent. Les journaux publics remplacent les chemins locaux par `<PROJECT>`, `<TEMP>`, `<OUTPUT>`, `<PYTHON>` et `<PRIVATE_PATH>`. Le journal brut de cette livraison est conservé dans le stockage interne de tâche, hors archive ; les preuves v1 restent intactes. Pour conserver votre propre original : ajouter `--raw-log <chemin-interne>/commands.json` à la vérification.
