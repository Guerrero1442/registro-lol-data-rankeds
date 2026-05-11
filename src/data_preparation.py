import pandas as pd


def preparations_match_data(df: pd.DataFrame) -> pd.DataFrame:
    # Aquí puedes realizar cualquier limpieza o transformación adicional que necesites
    # Por ejemplo, convertir tipos de datos, manejar valores faltantes, etc.
    
    # Convertir columnas numéricas a tipo numérico (si no se hizo antes)
    cols_numericas = [
        "f8_cs",
        "f8_rival_cs",
        "f14_cs",
        "f14_rival_cs",
        "f8_gold",
        "f8_rival_gold",
        "f14_gold",
        "f14_rival_gold",
        "f8_xp",
        "f8_rival_xp",
        "f14_xp",
        "f14_rival_xp",
    ]

    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Agregar columnas de diferencia entre jugador y rival
    df = df.assign(
        f8_cs_diff=lambda df_: df_["f8_cs"] - df_["f8_rival_cs"],
        f14_cs_diff=lambda df_: df_["f14_cs"] - df_["f14_rival_cs"],
        f8_gold_diff=lambda df_: df_["f8_gold"] - df_["f8_rival_gold"],
        f14_gold_diff=lambda df_: df_["f14_gold"] - df_["f14_rival_gold"],
        f8_xp_diff=lambda df_: df_["f8_xp"] - df_["f8_rival_xp"],
        f14_xp_diff=lambda df_: df_["f14_xp"] - df_["f14_rival_xp"],
    )
    
    return df