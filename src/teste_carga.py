import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy import create_engine, text
from config import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
with engine.connect() as conexao:
    print(conexao.execute(text("SELECT 1")).scalar())