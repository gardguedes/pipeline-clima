import logging
import sys
from pathlib import Path
import pandas as pd
import pymongo

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import MONGO_URL

logger = logging.getLogger(__name__)

def carregar_mongo_derivado(
    df: pd.DataFrame, 
    db_name: str = "pipeline_clima", 
    collection_name: str = "resumo_clima_atual"
) -> None:
    """Cria e atualiza uma coleção derivada no MongoDB Atlas (apenas a medição mais recente por cidade)."""
    if df.empty:
        logger.warning("DataFrame vazio. Nenhum dado enviado para o MongoDB.")
        return

    # Visão derivada: Seleciona o registro mais recente por cidade
    df_mais_recente = (
        df.sort_values("data_coleta")
        .groupby("cidade")
        .last()
        .reset_index()
    )

    # Converte timestamp para string para correta serialização BSON
    df_mais_recente["data_coleta"] = df_mais_recente["data_coleta"].astype(str)
    
    documentos = df_mais_recente[["cidade", "condicao", "temperatura", "data_coleta"]].to_dict(orient="records")

    client = pymongo.MongoClient(MONGO_URL)
    db = client[db_name]
    colecao = db[collection_name]

    # Atualiza o snapshot mais recente
    colecao.delete_many({})
    if documentos:
        colecao.insert_many(documentos)
    
    logger.info("Carga MongoDB Atlas concluída: %d documentos na coleção derivada '%s'.", len(documentos), collection_name)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    from transformacao import executar_transformacao
    
    df_tratado = executar_transformacao()
    carregar_mongo_derivado(df_tratado)
