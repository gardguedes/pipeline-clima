import json, logging
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.append(str(Path(__file__).resolve().parent.parent))
import requests

from config import OPENWEATHER_API_KEY

# cidades que serão consultadas
CIDADES = ["Recife,BR", "Sao Paulo,BR", "Rio Branco,BR", "Brasilia,BR", "Porto Alegre,BR"]

# Configuração do logging
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def consultar_clima(cidade: str) -> dict | None:
    """Consulta o clima atual de uma cidade no OpenWeatherMap. Devolve dict ou None se falhar."""

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": cidade, "appid": OPENWEATHER_API_KEY,
              "units": "metric", "lang": "pt_br"}

    try:
        logger.info("Consultando clima de %s", cidade)
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()
        logger.info("Consulta realizada com sucesso: %s",cidade)

        return resposta.json()

    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar clima de %s", cidade)
        return None

    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexão ao consultar clima de %s", cidade)
        return None

    except requests.exceptions.HTTPError as erro:
        logger.error("Erro HTTP ao consultar clima de %s", cidade)
        return None

def salvar_raw(dados: dict, cidade: str) -> Path:
    """Salva a resposta bruta com timestamp UTC no nome."""
    logger.info("Salvando dados brutos para %s", cidade)

    RAW_DIR = Path("raw")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    data_coleta = datetime.now(timezone.utc)
    carimbo = data_coleta.strftime("%Y%m%dT%H%M%SZ")

    # Inclui a data da coleta dentro do JSON
    dados["data_coleta"] = data_coleta.strftime("%Y-%m-%d %H:%M:%S")

    caminho = RAW_DIR / f"clima_{cidade.replace(',', '_')}_{carimbo}.json"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    logger.info("Dados brutos salvos em: %s", caminho)
    return caminho

def main():
    """Percorre a lista de cidades e salva os dados brutos em arquivos separados"""

    logger.info("Iniciando extração para %d cidades", len(CIDADES))
    for cidade in CIDADES:
        clima = consultar_clima(cidade)
        if clima is not None:
            caminho = salvar_raw(clima, cidade)
            logger.info("Dados salvos em: %s", caminho)
        else:
             logger.warning("Não foi possível obter os dados para %s", cidade)

if __name__ == "__main__":
    main()
