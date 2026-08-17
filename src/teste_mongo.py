import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pymongo import MongoClient
from config import MONGO_URL
cliente = MongoClient(MONGO_URL) # o create_engine do Mongo
banco = cliente["pipeline_clima"]
colecao = banco["teste"] 
resultado = colecao.insert_one({
"quem": "Gardênia", "teste": "conexão com MongoDB Atlas",
"mensagem": "primeiro documento na nuvem"})
print(f"documento inserido com _id = {resultado.inserted_id}")
cliente.close()