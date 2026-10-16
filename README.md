# Phénylcétonurie (PKU) : un banc d’essai de recherche reproductible

La phénylcétonurie (PKU) est le sujet de ce prototype : comparer des observations publiées sur l’enzyme PAH et préparer des hypothèses de recherche traçables.

Le paquet apporte 14 observations, sept variants, trois modèles de référence, leurs résultats et une procédure de restauration. La ridge ne dépasse pas les références dans ce pilote. Ces calculs sur une publication ne démontrent aucun bénéfice clinique ni généralisation. Le scénario Généthon est hypothétique, sans partenariat.

[Article français](https://www.generativschool.com/pku-banc-essai-ouvert.html) · [Tutoriel français](https://www.generativschool.com/pku-banc-essai-ouvert-tutoriel.html) · [Documentation complète](pku-v1.0.1/README.md)

## Démarrer

Python ≥3.9 ; parcours vérifié sur macOS arm64/Python 3.9.6. Linux non vérifié ; mesure des ressources incompatible avec Windows natif. Aucun service, clé ou dépendance d’exécution externe.

Télécharger [pku-v1.0.1.zip](pku-v1.0.1.zip), vérifier son [SHA-256](pku-v1.0.1.zip.sha256), puis :

```sh
unzip pku-v1.0.1.zip
cd pku-v1.0.1
python3 -m venv .venv
.venv/bin/python -m pip install --no-index evidence/generativschool_pku_public-1.0.1-py3-none-any.whl
.venv/bin/python -c "import pku_public; print(pku_public.__version__)"
```

Suivre ensuite le [tutoriel](pku-v1.0.1/TUTORIAL.md) pour auditer, comparer et restaurer. Le dossier de sortie choisi doit être neuf. Pour vérifier le paquet complet, avec setuptools ≥58 et wheel ≥0.37 déjà présents : `python3 scripts/verify.py --out /tmp/pku-verification-neuve` depuis `pku-v1.0.1/`.

## Preuves, droits et statut

Prototype de recherche, non validé biologiquement. [Résultats conservés](pku-v1.0.1/evidence/run/report.json), [provenance](pku-v1.0.1/PROVENANCE.md), [modèles et limites](pku-v1.0.1/MODELS.md). Code/tests MIT ; textes originaux réservés ; sources et adaptations tierces selon leurs attributions. [Notice](pku-v1.0.1/NOTICE.md) : la publicité du dépôt ne change aucune licence.

## Migration et références stables

Migration du 16 octobre 2026 depuis [generativschool-experiments au commit source](https://github.com/soufianelemqariMain/generativschool-experiments/tree/c89f8ec517a4a5bb340efb06b4f26d5ad2529bae). Les fichiers du paquet et son ZIP sont inchangés octet pour octet. Les chemins versionnés internes restent conservés pour la reproductibilité ; le nom du dépôt ne contient pas de version. Le dépôt historique et ses liens immuables restent accessibles.

[Inventaire SHA-256](MANIFEST.json). Auteur : Soufiane Lemqari (`soufianelemqariMain`).
