
from pathlib import Path

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


def sheet_connection(file_json: Path, spreadsheet_id: str, sheet_name: str) -> gspread.Worksheet:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_json, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    return sheet


def insert_dataframe(sheet: gspread.Worksheet, df: pd.DataFrame, mapping: dict, start_row: int = 0) -> None:
    """
    Inserta un DataFrame en Google Sheets usando un mapeo de columnas.

    Args:
        sheet: Objeto worksheet de gspread.
        df: DataFrame de pandas con los datos.
        mapping: Diccionario {Columna_Sheet: Columna_Pandas}
                 Ej: {'D': 'my_champ', 'F': 'win_loss', 'H': 'rival'}
        start_row: Fila inicial. Si es None, busca la siguiente vacía en 'D'.
    """
    if start_row is None:
        # Buscamos la primera fila vacía basándonos en la columna D
        start_row = len(sheet.col_values(4)) + 1

    payload = []

    # Convertimos DF a lista de diccionarios para iteración eficiente
    records = df.to_dict("records")

    for i, row_data in enumerate(records):
        current_row = start_row + i

        for sheet_col, df_col in mapping.items():
            if df_col in row_data:
                val = row_data[df_col]

                # Agregamos cada celda al lote de actualización
                payload.append(
                    {"range": f"{sheet_col}{current_row}", "values": [[val]]}
                )

    # Ejecución en una sola transacción para optimizar cuota de API
    if payload:
        sheet.batch_update(payload, value_input_option="USER_ENTERED")
        print(f"✅ Se insertaron {len(records)} filas exitosamente.")
    else :
        print("⚠️ No se encontraron datos para insertar.")
