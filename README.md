````markdown
# Pipeline de Dados Climáticos

Pipeline de dados desenvolvido em Python para coletar informações climáticas atuais de cidades brasileiras por meio da API pública da **OpenWeatherMap**, armazenar os dados brutos, realizar transformação e validação com Pandas e disponibilizar os dados tratados em dois destinos: PostgreSQL e MongoDB Atlas.

O projeto foi desenvolvido como desafio prático do módulo de **Engenharia de Dados do curso NExT Dados 2026.1 (CESAR School)**, contemplando as etapas de **extração, armazenamento da camada raw, transformação, validação e carga em bancos de dados relacionais e não relacionais**.

## Arquitetura

O pipeline segue o fluxo:

**OpenWeatherMap → Extração → Camada Raw → Transformação e Validação → PostgreSQL + MongoDB Atlas**

O diagrama abaixo representa a arquitetura completa do projeto:

![Diagrama de arquitetura](docs/arquitetura.png)

## 1. Objetivo do projeto

O objetivo deste projeto é construir um pipeline de dados de ponta a ponta que demonstre, de forma prática, as principais etapas de um fluxo de Engenharia de Dados:

1. Coleta de dados de uma API pública;
2. Armazenamento dos dados brutos;
3. Transformação e organização dos dados;
4. Validação da qualidade dos dados;
5. Carga em um banco de dados relacional;
6. Criação de uma visão derivada em um banco NoSQL;
7. Registro das etapas por meio de logging.

O pipeline foi estruturado de forma modular, separando as responsabilidades de extração, transformação, carga e orquestração.

## 2. Fonte dos dados

A fonte utilizada é a **OpenWeatherMap**, uma API pública que disponibiliza informações meteorológicas atuais.

A API foi escolhida porque fornece dados climáticos estruturados em JSON, permitindo trabalhar na prática com:

- consumo de API REST;
- tratamento de respostas JSON;
- armazenamento de dados brutos;
- transformação de estruturas aninhadas;
- tratamento e validação de dados;
- persistência em diferentes bancos de dados.

As cidades utilizadas neste projeto são:

- Recife;
- São Paulo;
- Rio Branco;
- Brasília;
- Porto Alegre.

Para cada cidade são coletadas informações como temperatura, condição climática, umidade e velocidade do vento.

## 3. Tecnologias utilizadas

- **Python** — linguagem principal do pipeline
- **Requests** — consumo da API
- **Pandas** — transformação e validação dos dados
- **SQLAlchemy** — conexão com PostgreSQL
- **PostgreSQL** — armazenamento dos dados tratados
- **PyMongo** — conexão com MongoDB Atlas
- **MongoDB Atlas** — armazenamento da visão derivada
- **Logging** — acompanhamento da execução do pipeline
- **Git/GitHub** — versionamento e disponibilização do projeto

## 4. Estrutura do projeto

```text
pipeline-clima/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── config.py
│
├── raw/
│   ├── YYYY-MM-DD_HHMM_nome.json
│   └── ...
│
├── src/
│   ├── extracao.py
│   ├── transformacao.py
│   ├── carga.py
│   ├── carga_mongo.py
│   ├── pipeline.py
│   └── ...
│
└── docs/
    ├── arquitetura.png
    └── evidencias/
        ├── postgresql.png
        └── mongodb.png
````

> **Observação:** o arquivo `config.py` contém credenciais locais e está incluído no `.gitignore`. Ele não deve ser enviado ao GitHub.

## 5. Como executar o projeto

### 5.1. Pré-requisitos

Antes de executar o pipeline, é necessário possuir:

* Python 3 instalado;
* PostgreSQL configurado;
* uma conta no MongoDB Atlas;
* uma chave de acesso da OpenWeatherMap;
* credenciais para conexão com PostgreSQL e MongoDB Atlas.

### 5.2. Clonar o repositório

```bash
git clone https://github.com/gardguedes/pipeline-clima.git
cd pipeline-clima
```

### 5.3. Criar o ambiente virtual

No Windows:

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
.venv\Scripts\activate
```

### 5.4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5.5. Configurar as credenciais

As credenciais não ficam armazenadas no GitHub.

O projeto utiliza um arquivo local chamado `config.py`, que está incluído no `.gitignore`.

Crie o arquivo `config.py` na raiz do projeto:

```python
OPENWEATHER_API_KEY = "SUA_API_KEY"

POSTGRES_URL = "postgresql+psycopg2://USUARIO:SENHA@HOST:5432/NOME_DO_BANCO"

MONGO_URL = "SUA_CONNECTION_STRING_MONGODB"
```

Substitua os valores pelos dados da sua própria configuração local.

**Nunca adicione o arquivo `config.py` ao GitHub.**

### 5.6. Executar o pipeline

A execução completa pode ser feita com:

```bash
python src/pipeline.py
```

O arquivo `pipeline.py` orquestra as principais etapas:

```text
EXTRACT → TRANSFORM → LOAD
```

Durante a execução, as etapas são registradas utilizando `logging`.

## 6. Etapa de extração

A extração é realizada no arquivo:

```text
src/extracao.py
```

A função de consulta utiliza a biblioteca `requests` e implementa mecanismos de coleta defensiva.

São utilizados:

* `timeout`;
* `raise_for_status()`;
* tratamento de `Timeout`;
* tratamento de erros de conexão;
* tratamento de erros HTTP;
* `try/except`;
* logging das operações.

Quando uma consulta é realizada com sucesso, a resposta JSON é preservada como dado bruto.

Os arquivos são armazenados na pasta `raw/` com timestamp no nome:

```text
raw/AAAA-MM-DD_HHMM_nome.json
```

Exemplo:

```text
raw/2026-08-16_1720_Recife_BR.json
```

A camada raw preserva a resposta original da API para possibilitar rastreabilidade e reprocessamento.

O repositório contém múltiplas coletas reais realizadas em diferentes horários.

## 7. Etapa de transformação

A transformação é realizada em:

```text
src/transformacao.py
```

Os arquivos JSON presentes na camada raw são lidos e transformados em um DataFrame do Pandas.

A transformação realiza:

* leitura dos arquivos JSON;
* seleção dos campos relevantes;
* achatamento dos dados aninhados da resposta;
* renomeação dos campos;
* conversão da data de coleta para `datetime`;
* inclusão do nome do arquivo de origem;
* consolidação dos arquivos em um único DataFrame;
* remoção de registros duplicados;
* validação dos dados antes da carga.

Os principais campos tratados são:

```text
cidade
condicao
temperatura
umidade
velocidade_vento
data_coleta
arquivo_origem
```

### Validações

Antes da carga, o pipeline verifica se:

* todas as colunas obrigatórias existem;
* não existem valores nulos nas colunas obrigatórias;
* a temperatura está dentro de um intervalo considerado plausível.

Caso alguma dessas validações falhe, um `ValueError` é gerado e o dado não segue para a etapa de carga.

A decisão de interromper o pipeline diante de dados inválidos evita que registros suspeitos sejam persistidos nos bancos de destino.

## 8. Deduplicação

A deduplicação ocorre durante a transformação.

Os registros são considerados duplicados quando possuem a mesma combinação de:

```text
cidade + data_coleta
```

Isso evita que a mesma coleta seja carregada mais de uma vez durante o processamento dos arquivos raw.

## 9. Carga no PostgreSQL

A carga relacional é realizada em:

```text
src/carga.py
```

O DataFrame tratado é carregado no PostgreSQL utilizando:

* SQLAlchemy;
* Pandas `to_sql()`.

A tabela utilizada é:

```text
clima
```

A estratégia escolhida foi:

```python
if_exists="replace"
```

### Por que `replace`?

A escolha de `replace` foi feita para garantir a **idempotência da execução do pipeline** dentro da proposta deste projeto.

A cada execução, os dados tratados são considerados a fonte completa para reconstrução da tabela. Dessa forma, a tabela existente é substituída pelo resultado atual do processamento, evitando que uma nova execução simplesmente acrescente novamente os mesmos registros.

Assim, executar o pipeline mais de uma vez não faz com que os mesmos registros sejam acumulados indefinidamente na tabela PostgreSQL.

Essa decisão é adequada para este projeto porque o objetivo é manter uma tabela consolidada a partir dos arquivos existentes na camada raw.

## 10. Carga derivada no MongoDB Atlas

A carga no MongoDB é realizada em:

```text
src/carga_mongo.py
```

A coleção utilizada é:

```text
resumo_clima_atual
```

dentro do banco:

```text
pipeline_clima
```

A coleção **não é uma cópia da tabela PostgreSQL**.

Foi criada uma visão derivada contendo somente o registro mais recente de cada cidade.

O processo consiste em:

1. ordenar os dados pela data de coleta;
2. agrupar os registros por cidade;
3. selecionar o registro mais recente de cada cidade;
4. selecionar apenas os campos necessários;
5. gravar o resultado no MongoDB Atlas.

A coleção contém informações resumidas como:

```text
cidade
condicao
temperatura
data_coleta
```

Dessa forma, enquanto o PostgreSQL mantém o conjunto tratado das coletas processadas, o MongoDB funciona como uma visão resumida do estado climático mais recente de cada cidade.

A coleção é atualizada a cada execução para representar o snapshot mais recente dos dados.

## 11. Logging

O projeto utiliza o módulo `logging` em vez de `print()`.

As mensagens registram informações como:

* início das etapas;
* cidade consultada;
* sucesso ou falha na coleta;
* arquivos raw salvos;
* quantidade de arquivos encontrados;
* resultado das validações;
* quantidade de registros carregados no PostgreSQL;
* quantidade de documentos carregados no MongoDB;
* conclusão do pipeline.

Isso facilita o acompanhamento da execução e a identificação de problemas.

## 12. Segurança das credenciais

Nenhuma senha, API key ou connection string real é armazenada no repositório.

As credenciais são mantidas localmente no arquivo:

```text
config.py
```

Esse arquivo está incluído no `.gitignore` e não deve ser enviado ao GitHub.

O repositório contém apenas a estrutura necessária para que outro usuário configure suas próprias credenciais.

## 13. Evidências

As evidências da execução do pipeline estão organizadas em:

```text
docs/evidencias/
```

Nesta pasta devem ser incluídos os registros visuais das cargas realizadas.

### PostgreSQL

Print da tabela `clima` contendo os dados tratados após a execução do pipeline.

Arquivo:

```text
docs/evidencias/postgresql.png
```

### MongoDB Atlas

Print da coleção `resumo_clima_atual` contendo os registros derivados.

Arquivo:

```text
docs/evidencias/mongodb.png
```

As evidências demonstram que os dados foram efetivamente carregados nos dois destinos.

## 14. Teste de idempotência

Um dos testes realizados consiste em executar o pipeline mais de uma vez.

A expectativa é que:

* novos arquivos raw sejam gerados para novas coletas;
* a transformação consolide e deduplicate os dados;
* a tabela PostgreSQL seja reconstruída utilizando `if_exists="replace"`;
* a coleção derivada do MongoDB seja atualizada para representar o registro mais recente de cada cidade.

Dessa forma, uma segunda execução não deve simplesmente duplicar os mesmos registros na tabela PostgreSQL.

## 15. Considerações finais

Este projeto demonstra um pipeline completo de Engenharia de Dados, desde a coleta de uma API pública até a disponibilização dos dados tratados em diferentes tecnologias de armazenamento.

A arquitetura foi construída separando as responsabilidades de:

```text
Extração
   ↓
Camada Raw
   ↓
Transformação
   ↓
Validação
   ↓
PostgreSQL
   ↓
MongoDB — visão derivada
```

A utilização de uma camada raw permite preservar os dados originais, enquanto a transformação e as validações garantem que somente dados considerados válidos avancem para as etapas de persistência.

A utilização de PostgreSQL e MongoDB no mesmo projeto permite demonstrar diferentes estratégias de armazenamento: uma tabela relacional com os dados tratados e uma coleção NoSQL derivada para consulta do estado mais recente por cidade.

## 16. Autor

**Gardênia Guedes**

Projeto desenvolvido como atividade prática do módulo de Engenharia de Dados.
```
```