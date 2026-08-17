import logging
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from extracao import main as executar_extracao
from transformacao import executar_transformacao
from carga import carregar_postgres
from carga_mongo import carregar_mongo_derivado

# Configuração global de logging para todo o pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def extract() -> None:
    """Etapa de Extração: Coleta dados da API pública e salva o JSON bruto na pasta raw/."""
    logger.info("--- Iniciando etapa: EXTRACT ---")
    executar_extracao()

def transform() -> pd.DataFrame:
    """Etapa de Transformação: Consolida os arquivos raw, achata o JSON, trata, deduplica e valida."""
    logger.info("--- Iniciando etapa: TRANSFORM ---")
    df_tratado = executar_transformacao()
    return df_tratado

def load(df: pd.DataFrame) -> None:
    """Etapa de Carga: Salva a tabela no PostgreSQL e a visão derivada no MongoDB Atlas."""
    logger.info("--- Iniciando etapa: LOAD ---")
    carregar_postgres(df)
    carregar_mongo_derivado(df)

def main() -> None:
    logger.info("==== PIPELINE INICIADO ====")

    extract()
    df_tratado = transform()
    load(df_tratado)

    logger.info("==== PIPELINE CONCLUÍDO COM SUCESSO ====")

if __name__ == "__main__":
    main()