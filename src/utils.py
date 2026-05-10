from datetime import datetime

import pytz


def formatear_fecha(timestamp_ms: int) -> str:
    # Convertir ms a segundos
    fecha_utc = datetime.fromtimestamp(timestamp_ms / 1000, tz=pytz.utc)
    # Localizar a Bogotá
    zona_bogota = pytz.timezone("America/Bogota")
    fecha_local = fecha_utc.astimezone(zona_bogota)
    return fecha_local.strftime("%Y-%m-%d %H:%M:%S")