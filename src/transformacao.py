import json, logging
from pathlib import Path
import pandas as pd

RAW_DIR = Path("raw")
TRATADA_DIR = Path("docs/tratada")

# Configuração do logging
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# normalização: achatar e selecionar
def listar_raws() -> list[Path]:
    return sorted(RAW_DIR.glob("clima_*.json"))
def carregar_raw(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as arq:
        return json.load(arq)

# renomar, tipar, rastrear
def transformar(dados: dict, origem: str) -> pd.DataFrame:
    """Transforma os dados brutos da API em um DataFrame limpo."""

    df = pd.DataFrame([{
        "cidade": dados["name"],
        "condicao": dados["weather"][0]["description"],
        "temperatura": dados["main"]["temp"],
        "umidade": dados["main"]["humidity"],
        "velocidade_vento": dados["wind"]["speed"],
        "data_coleta": dados["data_coleta"]
    }])

    # Converte data_coleta de texto para datetime
    df["data_coleta"] = pd.to_datetime(df["data_coleta"])

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

if __name__ == "__main__":
    arquivos = listar_raws()
    if not arquivos:
        raise SystemExit("Nenhum raw: rode src/extracao.py antes")
    logger.info("%d arquivos raw encontrados", len(arquivos))
    tabelas = []
    for caminho in arquivos:
        dados = carregar_raw(caminho)
        tabelas.append(transformar(dados, origem=caminho.name))
    df = pd.concat(tabelas, ignore_index=True)
    validar(df)
    TRATADA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRATADA_DIR / "clima.csv", index=False)
    logger.info("tratada gravada (%d linhas)", len(df))