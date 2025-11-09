import os
import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from analyse import analyse_complete, COLONNE_CIBLE, separer_types

st.set_page_config(page_title="Qualité de l'air - EDA & Corrélations", layout="wide")
st.title("Analyse de la qualité de l'air")
st.caption("Institut Teccart — 420-1AA-TT — Automne 2025 — Par Benfriha Hichem")

# Barre latérale - source de données
st.sidebar.header("Source des données")
chemin_defaut = "pollution.csv"
fichier_televerse = st.sidebar.file_uploader("Charger un CSV", type=["csv"])

@st.cache_data(show_spinner=False)
def charger_depuis_source(fichier):
    if fichier is not None:
        df = pd.read_csv(fichier)
    else:
        df = pd.read_csv(chemin_defaut)
    return df

try:
    df = charger_depuis_source(fichier_televerse)
except Exception as e:
    st.error(f"Erreur de chargement du CSV: {e}")
    st.stop()

# Exécution de l'analyse complète
@st.cache_data(show_spinner=True)
def calculer_analyse(df_csv: pd.DataFrame):
    chemin_tmp = "_tmp_entree.csv"
    df_csv.to_csv(chemin_tmp, index=False)
    resultats = analyse_complete(chemin_tmp)
    try:
        os.remove(chemin_tmp)
    except Exception:
        pass
    return resultats

resultats = calculer_analyse(df)
df_brut = resultats["df_brut"]
df_net = resultats["df_net"]
info_avant = resultats["info_avant"]
info_apres = resultats["info_apres"]
correlations = resultats["correlations"]
importance_variables = resultats["importance_variables"]

with st.expander("Aperçu des données (brut)", expanded=False):
    st.write("Dimensions:", tuple(info_avant["dimensions"].iloc[0]))
    st.dataframe(df_brut.head(20))
    st.subheader("Types et valeurs manquantes")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(info_avant["types"]) 
    with col2:
        st.dataframe(info_avant["na"]) 
    st.subheader("Statistiques descriptives")
    st.dataframe(info_avant["statistiques"]) 

st.subheader("Données nettoyées")
st.write("Dimensions:", tuple(info_apres["dimensions"].iloc[0]))

# Filtres dynamiques sur df_net
colonnes_numeriques, colonnes_categorielles = separer_types(df_net)

with st.sidebar:
    st.header("Filtres")
    filtre = df_net.copy()
    # Filtre par qualité d'air (cible)
    if COLONNE_CIBLE in filtre.columns:
        niveaux = list(filtre[COLONNE_CIBLE].cat.categories if hasattr(filtre[COLONNE_CIBLE], "cat") else sorted(filtre[COLONNE_CIBLE].unique()))
        niveaux_sel = st.multiselect("Niveaux de qualité de l'air", niveaux, default=niveaux)
        filtre = filtre[filtre[COLONNE_CIBLE].astype(str).isin([str(v) for v in niveaux_sel])]

    # Curseurs numériques
    for c in colonnes_numeriques:
        cmin, cmax = float(filtre[c].min()), float(filtre[c].max())
        vmin, vmax = st.slider(c, cmin, cmax, (cmin, cmax))
        filtre = filtre[(filtre[c] >= vmin) & (filtre[c] <= vmax)]

st.write("Lignes après filtres:", len(filtre))
st.dataframe(filtre.head(20))

# Visualisations
st.header("Visualisations")

# 1) Histogrammes
st.subheader("Histogrammes des variables")
sel_hist = st.multiselect("Choisir des variables pour l'histogramme", colonnes_numeriques, default=[c for c in colonnes_numeriques if c in ["PM2.5", "PM10", "NO2", "SO2", "CO"]])
cols = st.columns(2)
for i, c in enumerate(sel_hist):
    with cols[i % 2]:
        fig = px.histogram(filtre, x=c, nbins=30, title=f"Distribution de {c}", marginal="box")
        st.plotly_chart(fig, use_container_width=True)

# 2) Boxplots par niveau de qualité
if COLONNE_CIBLE in filtre.columns:
    st.subheader("Boxplots par niveau de qualité de l'air")
    sel_box = st.multiselect("Choisir des variables pour boxplot", [c for c in colonnes_numeriques if c != COLONNE_CIBLE], default=["PM2.5", "PM10"])
    for c in sel_box:
        fig = px.box(filtre, x=COLONNE_CIBLE, y=c, points="outliers", title=f"{c} par {COLONNE_CIBLE}")
        st.plotly_chart(fig, use_container_width=True)

# 3) Heatmap des corrélations (Spearman)
st.subheader("Matrice de corrélations (Spearman)")
if "matrice_spearman" in correlations:
    matrice = correlations["matrice_spearman"].loc[colonnes_numeriques, colonnes_numeriques]
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrice, annot=False, cmap="RdBu_r", center=0, ax=ax)
    st.pyplot(fig, clear_figure=True)

# 4) Importance des variables vs Qualité de l'air
st.subheader("Variables les plus liées à la qualité de l'air")
if not importance_variables.empty:
    st.dataframe(importance_variables)
    fig = px.bar(importance_variables.head(15), x="variable", y="information_mutuelle", title="Top variables (Information Mutuelle)")
    st.plotly_chart(fig, use_container_width=True)

# 5) Nuages de points 2D
st.subheader("Nuages de points")
x_var = st.selectbox("Axe X", colonnes_numeriques, index=max(0, colonnes_numeriques.index("PM2.5")) if "PM2.5" in colonnes_numeriques else 0)
y_var = st.selectbox("Axe Y", colonnes_numeriques, index=max(0, colonnes_numeriques.index("PM10")) if "PM10" in colonnes_numeriques else 1)
color_var = COLONNE_CIBLE if COLONNE_CIBLE in df_net.columns else None
fig = px.scatter(filtre, x=x_var, y=y_var, color=color_var, title=f"{x_var} vs {y_var}", hover_data=filtre.columns)
st.plotly_chart(fig, use_container_width=True)

st.success("Analyse prête. Utilisez les filtres pour explorer et exportez les graphiques via les boutons natifs Plotly.")
