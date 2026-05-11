
import pandas as pd
from riotwatcher import LolWatcher, RiotWatcher

from src.config.settings import settings
from src.extract_data_api import (
    obtener_partidas_pendientes,
    obtener_puuid,
    process_toplane_matches,
)
from src.spreadsheet_operations import insert_dataframe, sheet_connection


def main():
    
    
    sheet = sheet_connection(settings.credentials_file, settings.spreadsheet_id, settings.sheet_name)

    API_KEY = settings.api_key
    
    watcher = LolWatcher(API_KEY)
    riot_watcher = RiotWatcher(API_KEY)
    region_route = settings.region_route
    
    
    my_puuid = obtener_puuid(riot_watcher, settings.game_name, settings.tag_line, settings.region_route)
    
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
