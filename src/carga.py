import logging
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import POSTGRES_URL

logger = logging.getLogger(__name__)

def carregar_postgres(df: pd.DataFrame, tabela: str = "clima") -> None:
    """Carrega o DataFrame consolidado no banco relacional PostgreSQL."""
    engine = create_engine(POSTGRES_URL)
    
    df.to_sql(tabela, engine, if_exists="replace", index=False)
    logger.info("Carga PostgreSQL concluída: %d registros gravados na tabela '%s'.", len(df), tabela)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    from transformacao import executar_transformacao
    
    df_tratado = executar_transformacao()
    carregar_postgres(df_tratado)