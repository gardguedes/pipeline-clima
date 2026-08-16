import json, logging
from pathlib import Path
import pandas as pd

RAW_DIR = Path("raw")

# Configuração do logging
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# normalização: achatar e selecionar
def listar_raws() -> list[Path]:
    return sorted(RAW_DIR.glob("*.json"))
def carregar_raw(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as arq:
        return json.load(arq)

# renomar, tipar, rastrear
def transformar(dados: dict, origem: str, data_coleta: pd.Timestamp) -> pd.DataFrame:
    """Transforma os dados brutos da API em um DataFrame limpo."""

    df = pd.DataFrame([{
        "cidade": dados["name"],
        "condicao": dados["weather"][0]["description"],
        "temperatura": dados["main"]["temp"],
        "umidade": dados["main"]["humidity"],
        "velocidade_vento": dados["wind"]["speed"],
        "data_coleta": data_coleta
    }])

    # Converte data_coleta para datetime
    df["data_coleta"] = pd.to_datetime(df["data_coleta"], utc=True)

    # Rastreabilidade
    df["arquivo_origem"] = origem

    return df

def validar (df: pd.DataFrame) -> None:
    """Valida o DataFrame. Levanta ValueError se algo não fizer sentido."""

    obrigatorias = ["cidade", "condicao", "temperatura",
                    "umidade", "velocidade_vento", "data_coleta"]
    for coluna in obrigatorias:
        if coluna not in df.columns:
            raise ValueError(f"Coluna ausente: {coluna}")
        if df[coluna].isna().any():
            raise ValueError(f"Coluna com nulo: {coluna}")

    if (df["temperatura"] < -100).any() or (df["temperatura"] > 60).any():
        raise ValueError("Temperatura fora do intervalo esperado: dado suspeito, carga abortada")

    logger.info("Validação ok: %d linhas íntegras", len(df))

def executar_transformacao() -> pd.DataFrame:
    """Executa a transformação de todos os raws e retorna o DataFrame final."""
    arquivos = listar_raws()
    if not arquivos:
        raise SystemExit("Nenhum raw: rode src/extracao.py antes")
    logger.info("%d arquivos raw encontrados", len(arquivos))

    tabelas = []
    for caminho in arquivos:
        dados = carregar_raw(caminho)

        # Recupera o timestamp do nome do arquivo
        timestamp_texto = caminho.name[:15]
        data_coleta = pd.to_datetime(timestamp_texto, format="%Y-%m-%d_%H%M", utc=True)
        df = transformar(dados, origem=caminho.name, data_coleta=data_coleta)
        tabelas.append(df)

    df = pd.concat(tabelas, ignore_index=True)
    validar(df)

    return df

if __name__ == "__main__":
    df = executar_transformacao()

    logger.info("Transformação concluída: %d linhas", len(df))
