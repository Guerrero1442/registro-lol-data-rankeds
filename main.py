import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from riotwatcher import LolWatcher, RiotWatcher

from src.extract_data_api import (
    obtener_partidas_pendientes,
    obtener_puuid,
    process_toplane_matches,
)
from src.spreadsheet_operations import insert_dataframe, sheet_connection


def main():
    
    
    file_json = Path('credentials.json')
    
    spreadsheet_id = "1_mDRZEKVEVdwC96vS_Kkktn2aGP7I8LUZynwxXLP31s"
    
    sheet_name = "Camilo Arias"
    
    sheet = sheet_connection(file_json, spreadsheet_id, sheet_name)



    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    
    watcher = LolWatcher(API_KEY)
    riot_watcher = RiotWatcher(API_KEY)
    region_route = "americas"
    platform_route = "la1"
    
    
    my_puuid = obtener_puuid(riot_watcher, "Camilo Arias", "LAN")
    
    matches = obtener_partidas_pendientes(sheet, my_puuid, region_route)


    matches_data = process_toplane_matches(
    matches,
    my_puuid,
    watcher,
)
    
    schema_toplane_data = {
    "match_id": "string",
    "fecha_partida": "string",
    "queue_type": "string",
    "my_champion": "string",
    "rival_champion": "string",
    "result": "string",
    "kda": "string",
    "cspm": "float",
    "f8_cs": "int",
    "f14_cs": "int",
    "f8_rival_cs": "int",
    "f14_rival_cs": "int",
    "f8_gold": "int",
    "f14_gold": "int",
    "f8_rival_gold": "int",
    "f14_rival_gold": "int",
    "f8_xp": "int",
    "f14_xp": "int",
    "f8_rival_xp": "int",
    "f14_rival_xp": "int",
    "damage_to_turrets": "int",
}
        
    df_toplane = pd.DataFrame(matches_data, columns=schema_toplane_data.keys())
    
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
        df_toplane[col] = pd.to_numeric(df_toplane[col], errors="coerce")
        
    df_toplane = df_toplane.assign(
    f8_cs_diff=lambda df_: df_["f8_cs"] - df_["f8_rival_cs"],
    f14_cs_diff=lambda df_: df_["f14_cs"] - df_["f14_rival_cs"],
    f8_gold_diff=lambda df_: df_["f8_gold"] - df_["f8_rival_gold"],
    f14_gold_diff=lambda df_: df_["f14_gold"] - df_["f14_rival_gold"],
    f8_xp_diff=lambda df_: df_["f8_xp"] - df_["f8_rival_xp"],
    f14_xp_diff=lambda df_: df_["f14_xp"] - df_["f14_rival_xp"],
    kda="'"
    + df_toplane["kda"].astype(
        str
    ),  # evitar que google sheet lo identifique como fecha
    ).sort_values(by="fecha_partida", ascending=True)
    
    config_mapeo = {
    "C": "match_id",
    "D": "fecha_partida",
    "E": "queue_type",
    "G": "my_champion",
    "J": "rival_champion",
    "M": "result",
    "N": "kda",
    "O": "cspm",
    "P": "f8_cs_diff",
    "Q": "f14_cs_diff",
    "R": "f8_gold_diff",
    "S": "f14_gold_diff",
    "T": "f8_xp_diff",
    "U": "f14_xp_diff",
    "V": "damage_to_turrets",
    }

    insert_dataframe(sheet, df_toplane, config_mapeo)

if __name__ == "__main__":
    main()
