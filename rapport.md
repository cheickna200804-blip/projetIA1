# Analyse de la qualité de l'air

Institut Teccart — 420-1AA-TT — Automne 2025  
Auteur: Benfriha Hichem

## 1. Introduction
Ce rapport présente l’exploration d’un jeu de données sur la qualité de l’air à partir de facteurs environnementaux et démographiques, l’identification des relations et corrélations clés, et une application Streamlit interactive pour la visualisation.

## 2. Données et variables
- Temperature (°C)
- Humidity (%)
- PM2.5 (µg/m³)
- PM10 (µg/m³)
- NO2 (ppb)
- SO2 (ppb)
- CO (ppm)
- Proximite_zones_industrielles (km)
- Densite_population (hab./km²)
- Qualite_air (cible catégorielle: 0=Bonne, 1=Modérée, 2=Mauvaise, 3=Dangereuse)

## 3. Méthodologie
- Nettoyage: imputation médiane pour variables numériques, mode pour catégorielles, capping IQR (1.5×IQR) pour atténuer valeurs aberrantes; valeurs négatives invalides mises à NaN avant imputation.
- Analyses descriptives: moyenne, médiane, écart-type, quartiles.
- Corrélations: matrice Spearman entre variables numériques; focus sur relations avec PM2.5/PM10.
- Lien variables→Qualité: Information Mutuelle et ANOVA F contre `Qualite_air`.

## 4. Résultats (à compléter après exécution)
Exécutez:
```
python analyse.py --csv pollution.csv
```
Puis renseignez ci-dessous les principaux résultats:

- Dimensions (brut → nettoyé): ... → ...
- Variables les plus corrélées avec PM2.5: ...
- Variables les plus corrélées avec PM10: ...
- Top variables liées à `Qualite_air` (Information Mutuelle): ...
- Observations sur distributions (histogrammes/boxplots): ...

## 5. Visualisations interactives
Lancez l’application Streamlit:
```
streamlit run application.py
```
Fonctionnalités:
- Filtres par `Qualite_air` et plages numériques.
- Histogrammes, boxplots par niveau de qualité, heatmap des corrélations, nuages de points.
- Tableau d’importance des variables (Information Mutuelle, ANOVA F).

## 6. Interprétation et discussion
- Relation attendue: hausse PM2.5/PM10, NO2, SO2, CO → qualité de l’air plus dégradée.
- Rôles contextuels: humidité/température peuvent moduler les concentrations; densité de population et proximité industrielle influent sur les pics de pollution.
- Limites: valeurs manquantes, mesures extrêmes, corrélation ≠ causalité.

## 7. Recommandations
- Surveillance renforcée des zones proches d’industries et à forte densité.
- Politiques de réduction des émissions (trafic, sources fixes NOx/SOx/PM).
- Avertissements publics lors de niveaux élevés de PM2.5/PM10 et NO2.
- Collecte de données additionnelles (vent, précipitations, heures/jours) pour modèles prédictifs.

## 8. Conclusion
Synthèse des tendances principales observées et prochaines étapes pour l’amélioration de la qualité de l’air et le suivi opérationnel.
