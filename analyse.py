import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from sklearn.feature_selection import mutual_info_classif, f_classif
from sklearn.preprocessing import MinMaxScaler


COLONNE_CIBLE = "Qualite_air"


def charger_donnees(chemin: str) -> pd.DataFrame:
    df = pd.read_csv(chemin)
    return df


def separer_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    colonnes_numeriques = [c for c in df.columns if c != COLONNE_CIBLE and pd.api.types.is_numeric_dtype(df[c])]
    colonnes_categorielles = [c for c in df.columns if c != COLONNE_CIBLE and not pd.api.types.is_numeric_dtype(df[c])]
    return colonnes_numeriques, colonnes_categorielles


def info_de_base(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    info = {
        "dimensions": pd.DataFrame([[df.shape[0], df.shape[1]]], columns=["lignes", "colonnes"]),
        "types": df.dtypes.astype(str).to_frame("type"),
        "na": df.isna().sum().to_frame("valeurs_manquantes"),
        "statistiques": df.describe(include="all").T,
    }
    return info


def nettoyer_donnees(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    df = df.copy()

    if COLONNE_CIBLE in df.columns:
        if pd.api.types.is_numeric_dtype(df[COLONNE_CIBLE]):
            df[COLONNE_CIBLE] = df[COLONNE_CIBLE].astype(int).astype("category")
        else:
            df[COLONNE_CIBLE] = df[COLONNE_CIBLE].astype("category")

    colonnes_non_negatives = ["PM2.5", "PM10", "NO2", "SO2", "CO", "Humidity", "Temperature"]
    for c in colonnes_non_negatives:
        if c in df.columns:
            df.loc[df[c] < 0, c] = np.nan

    colonnes_numeriques, colonnes_categorielles = separer_types(df)

    imputations_medianes: Dict[str, float] = {}
    for c in colonnes_numeriques:
        med = df[c].median()
        df[c] = df[c].fillna(med)
        imputations_medianes[c] = float(med) if pd.notna(med) else np.nan

    imputations_modes: Dict[str, float] = {}
    for c in colonnes_categorielles:
        if df[c].isna().any():
            mode_val = df[c].mode().iloc[0]
            df[c] = df[c].fillna(mode_val)
            imputations_modes[c] = mode_val

    plafonds: Dict[str, Dict[str, float]] = {}
    for c in colonnes_numeriques:
        q1, q3 = df[c].quantile([0.25, 0.75])
        iqr = q3 - q1
        bas = q1 - 1.5 * iqr
        haut = q3 + 1.5 * iqr
        df[c] = df[c].clip(lower=bas, upper=haut)
        plafonds[c] = {"bas": float(bas), "haut": float(haut)}

    meta = {"imputations_medianes": imputations_medianes, "imputations_modes": imputations_modes, "plafonds": plafonds}
    return df, meta


def calculer_correlations(df: pd.DataFrame) -> Dict[str, pd.Series]:
    colonnes_numeriques, _ = separer_types(df)
    matrice_spearman = df[colonnes_numeriques].corr(method="spearman").round(3)
    out = {"matrice_spearman": matrice_spearman}

    for cible_cont in ["PM2.5", "PM10"]:
        if cible_cont in df.columns:
            out[f"correlation_avec_{cible_cont}"] = matrice_spearman[cible_cont].sort_values(ascending=False)
    return out


def importance_variables(df: pd.DataFrame) -> pd.DataFrame:
    if COLONNE_CIBLE not in df.columns:
        return pd.DataFrame()

    X = df.drop(columns=[COLONNE_CIBLE]).copy()
    y = df[COLONNE_CIBLE].cat.codes if hasattr(df[COLONNE_CIBLE], "cat") else df[COLONNE_CIBLE]

    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype("category").cat.codes

    echelle = MinMaxScaler()
    X_echelle = echelle.fit_transform(X)

    mi = mutual_info_classif(X_echelle, y, random_state=0)
    f_vals, _ = f_classif(X_echelle, y)

    res = pd.DataFrame({"variable": X.columns, "information_mutuelle": mi, "anova_f": f_vals}).sort_values(
        by=["information_mutuelle", "anova_f"], ascending=False
    )
    return res


def analyse_complete(chemin: str) -> Dict[str, object]:
    df_brut = charger_donnees(chemin)
    info_avant = info_de_base(df_brut)
    df_net, meta = nettoyer_donnees(df_brut)
    info_apres = info_de_base(df_net)
    corrs = calculer_correlations(df_net)
    imp = importance_variables(df_net)

    return {
        "df_brut": df_brut,
        "df_net": df_net,
        "info_avant": info_avant,
        "info_apres": info_apres,
        "correlations": corrs,
        "importance_variables": imp,
        "meta": meta,
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="pollution.csv")
    args = p.parse_args()

    resultats = analyse_complete(args.csv)
    print("Lignes, Colonnes (brut):", tuple(resultats["info_avant"]["dimensions"].iloc[0]))
    print("Lignes, Colonnes (nettoyé):", tuple(resultats["info_apres"]["dimensions"].iloc[0]))
    if not resultats["importance_variables"].empty:
        print("Top variables vs Qualite_air (information_mutuelle):")
        print(resultats["importance_variables"].head(10).to_string(index=False))
    for k in ("PM2.5", "PM10"):
        cle = f"correlation_avec_{k}"
        if cle in resultats["correlations"]:
            print(f"Principales corrélations avec {k}:")
            print(resultats["correlations"][cle].head(10).to_string())
