# Modèles et licences

Auteur : Soufiane Lemqari. Les trois modèles ci-dessous sont exécutés par le code original MIT ; aucun poids externe. Python utilise sa propre licence PSF.

| Modèle | Ajustement et entrée | Statut |
|---|---|---|
| Zéro effet | Δ prédit = 0 | Exécuté, baseline |
| Moyenne train | Moyenne des six Δ train par pli | Exécuté, baseline |
| Ridge α=1 | x=activité témoin/100 ; pente=Σ(x−xm)(y−ym)/(Σ(x−xm)²+1) ; prédiction=ym+pente(x−xm) | Exécuté ; intercept non pénalisé, α fixé, aucun tuning |

Aucun meilleur modèle sélectionné sur ces sept cas. La ridge prédit conditionnellement à un dosage témoin préalable ; elle ne prédit pas la réponse depuis une séquence.

ESM n'est ni installé, ni téléchargé, ni exécuté, et aucune performance ESM n'est revendiquée. `configs/study.json` porte un état `not_executed_not_admitted`, révision et empreinte nulles. Conditions nécessaires pour une future interface : référence PAH vérifiée contre une séquence versionnée, identifiant du modèle, commit immuable, SHA-256/taille des poids, licences code/poids, procédure de téléchargement et extraction, ressources mesurées et risque de présence de PAH dans le préentraînement. Tant que ces champs sont absents, aucun embedding n'est admissible. L'adaptation n'est pas implémentée dans cette version.

La cible « activité traitée − activité témoin » et la covariable témoin partagent le terme témoin. Les erreurs de mesure de ce terme peuvent induire une association artificielle. Cette réserve méthodologique ne constitue pas une fuite constatée et ne modifie pas les scores. Son examen futur nécessite les mesures brutes et une validation externe.
