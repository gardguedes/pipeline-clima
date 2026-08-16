import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd

from sqlalchemy import create_engine
from config import POSTGRES_URL
from transformacao import executar_transformacao

# Configuração do logging
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Executa a transformação
df = executar_transformacao()

# Conferência dos tipos antes da carga
logger.info("Tipos antes da carga:\n%s", df.dtypes)

# Conexão com PostgreSQL
engine = create_engine(POSTGRES_URL)
df.to_sql("clima", engine, if_exists="replace", index=False)
conferencia = pd.read_sql("SELECT cidade, condicao, temperatura, data_coleta FROM clima LIMIT 5", engine)
logger.info("conferencia:\n%s", conferencia)