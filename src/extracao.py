import json
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.append(str(Path(__file__).resolve().parent.parent))
import requests

from config import OPENWEATHER_API_KEY

# cidades que serão consultadas
CIDADES = ["Recife,BR", "Sao Paulo,BR", "Rio Branco,BR", "Brasilia,BR", "Porto Alegre,BR"]

def consultar_clima(cidade: str) -> dict | None:
    """Consulta o clima atual de uma cidade no OpenWeatherMap. Devolve dict ou None se falhar."""

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": cidade, "appid": OPENWEATHER_API_KEY,
              "units": "metric", "lang": "pt_br"}

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()

        return resposta.json()

    except requests.exceptions.Timeout:
        print(f"[erro] OpenWeatherMap demorou demais (cidade={cidade})")
        return None

    except requests.exceptions.ConnectionError:
        print("[erro] Sem conexão ou servidor fora do ar")
        return None

    except requests.exceptions.HTTPError as erro:
        print(f"[erro] HTTP {resposta.status_code}: {erro}")
        return None

def salvar_raw(dados: dict, cidade: str) -> Path:
    """Salva a resposta bruta com timestamp UTC no nome."""
    RAW_DIR = Path("raw")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    data_coleta = datetime.now(timezone.utc)
    carimbo = data_coleta.strftime("%Y%m%dT%H%M%SZ")

    # Inclui a data da coleta dentro do JSON
    dados["data_coleta"] = data_coleta.isoformat()

    caminho = RAW_DIR / f"clima_{cidade.replace(',', '_')}_{carimbo}.json"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    return caminho

def main():
    for cidade in CIDADES:
        clima = consultar_clima(cidade)
        if clima is not None:
            caminho = salvar_raw(clima, cidade)
            print(f"{cidade}: dados salvos em: {caminho}")
        else:

            print(f"{cidade}: não foi possível obter os dados")

if __name__ == "__main__":
    main()
