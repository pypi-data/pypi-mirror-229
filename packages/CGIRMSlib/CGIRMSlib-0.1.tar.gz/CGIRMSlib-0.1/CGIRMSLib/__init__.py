from datetime import datetime
import pandas as pd

def get_events(dateTime_start, dateTime_end, powerplantId, assetId):
    dados = []
    try:
        dateTime_start = datetime.strptime(dateTime_start, "%Y-%m-%d")
        dateTime_end = datetime.strptime(dateTime_end, "%Y-%m-%d")

        if dateTime_start <= dateTime_end:
            dados.append(
                {"DataInicio": dateTime_start, "DataFim": dateTime_end,
                 "NomeParque": powerplantId, "Ventoinha": assetId})

            df = pd.DataFrame(dados)
            return df
        else:
            raise ValueError("A data inserida está inválida")
    except ValueError as e:
        raise e

def get_statistical_data(dateTime_start, dateTime_end, powerplantId, assetId, signalId):
    dados = []
    try:
        dateTime_start = datetime.strptime(dateTime_start, "%Y-%m-%d")
        dateTime_end = datetime.strptime(dateTime_end, "%Y-%m-%d")

        if dateTime_start <= dateTime_end:
            dados.append(
                {
                    "DataInicio": dateTime_start, "DataFim": dateTime_end,
                    "NomeParque": powerplantId, "Ventoinha": assetId, "Medida": signalId
                })

            df = pd.DataFrame(dados)
            return df
        else:
            raise ValueError("A data inserida está inválida")
    except ValueError as e:
        raise e

def get_plant_metadata(powerplantId):
    dados = [{"NomeParque": powerplantId}]
    df = pd.DataFrame(dados)
    return df

def get_asset_metadata(powerplantId, assetId):
    dados = [{"NomeParque": powerplantId, "Ventoinhas": assetId}]
    df = pd.DataFrame(dados)
    return df

def get_raw_data(dateTime_start, dateTime_end, powerplantId, assetId, signalId):
    dados = []
    try:
        dateTime_start = datetime.strptime(dateTime_start, "%Y-%m-%d")
        dateTime_end = datetime.strptime(dateTime_end, "%Y-%m-%d")

        if dateTime_start <= dateTime_end:
            dados.append(
                {
                    "DataInicio": dateTime_start, "DataFim": dateTime_end,
                    "NomeParque": powerplantId, "Ventoinha": assetId, "Medida": signalId
                })

            df = pd.DataFrame(dados)
            return df
        else:
            raise ValueError("A data inserida está inválida")
    except ValueError as e:
        raise e
