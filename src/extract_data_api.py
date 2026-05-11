import time
from datetime import datetime

import gspread
import pytz
from riotwatcher import ApiError, LolWatcher, RiotWatcher

from src.utils import formatear_fecha


def obtener_puuid(riot_client: RiotWatcher, game_name: str, tag_line: str, continental_route: str ="americas") -> str:
    try:
        # Petición obligatoria a través de la instancia de RiotWatcher
        account_data = riot_client.account.by_riot_id(
            region=continental_route, game_name=game_name, tag_line=tag_line
        )
        return account_data["puuid"]

    except ApiError as err:
        if err.response.status_code == 404:
            print("Error: Riot ID no encontrado. Verifique la ortografía y el tagLine.")
        elif err.response.status_code == 403:
            print("Error: Clave de API inválida o expirada.")
        else:
            print(f"Error de API: {err}")
        return None

def obtener_partidas_pendientes(sheet: gspread.Worksheet, puuid: str, lol_watcher: LolWatcher, region: str ="americas" ) -> list[str]:
    registrados = set(sheet.col_values(3))

    try:
        ultima_fecha_str = sheet.col_values(4)[-1]
        ultima_fecha_dt = datetime.strptime(ultima_fecha_str, "%Y-%m-%d %H:%M:%S")
        # Convertir a epoch segundos (Riot usa segundos para startTime, no ms)
        start_time_epoch = int(ultima_fecha_dt.timestamp())
    except (IndexError, ValueError):
        start_time_epoch = int(datetime(2026, 1, 1, tzinfo=pytz.utc).timestamp())
        print(
            f"Hoja vacía o dato inválido. Iniciando ingesta desde 2026-01-01 (epoch: {start_time_epoch})"
        )

    # 3. Consultar Riot API con filtro de tiempo
    nuevos_ids = lol_watcher.match.matchlist_by_puuid(
        region=region,
        puuid=puuid,
        start_time=start_time_epoch,
        count=100,  # Aumentar rango ya que el filtrado por tiempo es eficiente
        type="ranked",
    )

    # 4. Deduplicación final en memoria
    pendientes = [m_id for m_id in nuevos_ids if m_id not in registrados]

    return pendientes

def process_toplane_matches(match_list: list[str], puuid: str, watcher: LolWatcher, region_route: str ="americas") -> list[dict]:
    datos_partidas = []

    for match_id in match_list:
        try:
            # 1. Consulta inicial del resumen de la partida
            match = watcher.match.by_id(region_route, match_id)

            if match["info"].get("gameDuration", 0) < 600:
                print(f"Partida {match_id} omitida: Duracion Insuficiente")
                continue

            # 2. Identificación del participante y validación del rol
            me_data = next(
                p for p in match["info"]["participants"] if p["puuid"] == puuid
            )

            # Salida temprana si no es Toplane
            if me_data["teamPosition"] != "TOP":
                continue

            # 3. Consulta del timeline (Solo se ejecuta si el rol es TOP)
            timeline = watcher.match.timeline_by_match(region_route, match_id)
            me_id = me_data["participantId"]

            # 4. Identificación del Rival (Toplaner enemigo)
            try:
                rival_data = next(
                    p
                    for p in match["info"]["participants"]
                    if p["teamPosition"] == "TOP" and p["puuid"] != puuid
                )
                rival_id = rival_data["participantId"]
            except StopIteration:
                # Manejo de casos atípicos (AFK desde el inicio, roles mal asignados por la API)
                rival_data = {"championName": "Desconocido/AFK"}
                rival_id = None

            def get_frame_stats(frame_idx, p_id):
                # Validación de longitud del timeline (Surrenders tempranos)
                if frame_idx >= len(timeline["info"]["frames"]):
                    return {"cs": 0, "gold": 0, "xp": 0}

                frame = timeline["info"]["frames"][frame_idx]["participantFrames"][
                    str(p_id)
                ]
                return {
                    "cs": frame["minionsKilled"] + frame["jungleMinionsKilled"],
                    "gold": frame["totalGold"],
                    "xp": frame["xp"],
                }

            # Extracción de mis métricas
            f8_me = get_frame_stats(8, me_id)
            f14_me = get_frame_stats(14, me_id)

            # Extracción de métricas del rival (Si existe)
            if rival_id:
                f8_rival = get_frame_stats(8, rival_id)
                f14_rival = get_frame_stats(14, rival_id)

            kda_str = f"{me_data['kills']}/{me_data['deaths']}/{me_data['assists']}"
            game_length_min = (
                max(
                    1,
                    me_data["challenges"].get(
                        "gameLength", me_data.get("gameDuration", 1)
                    ),
                )
                / 60
            )

            row = [
                match_id,
                formatear_fecha(match["info"]["gameStartTimestamp"]),
                "Solo/Duo" if match["info"]["queueId"] == 420 else "Flex",
                me_data["championName"],
                rival_data["championName"],
                "W" if me_data["win"] else "L",
                kda_str,
                round(
                    (me_data["totalMinionsKilled"] + me_data["neutralMinionsKilled"])
                    / game_length_min,
                    2,
                ),
                f8_me["cs"],
                f14_me["cs"],
                f8_rival["cs"] if rival_id else "N/A",
                f14_rival["cs"] if rival_id else "N/A",
                f8_me["gold"],
                f14_me["gold"],
                f8_rival["gold"] if rival_id else "N/A",
                f14_rival["gold"] if rival_id else "N/A",
                f8_me["xp"],
                f14_me["xp"],
                f8_rival["xp"] if rival_id else "N/A",
                f14_rival["xp"] if rival_id else "N/A",
                me_data["damageDealtToTurrets"],
            ]
            datos_partidas.append(row)

            # Control de Rate Limit básico (Requerido para procesos secuenciales)
            time.sleep(1.5)

        except ApiError as err:
            if err.response.status_code == 429:
                print(
                    f"Rate limit excedido en la partida {match_id}. Implementar backoff."
                )
                break
            else:
                print(f"Error en la partida {match_id}: {err}")
                continue

    return datos_partidas
