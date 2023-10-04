import openai
import numpy
import pandas as pd
import time
import os
from getpass import getpass
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from cassandra.query import SimpleStatement
from datasets import load_dataset

ASTRA_DB_TOKEN_BASED_PASSWORD = getpass('Your Astra DB Token ("AstraCS:..."): ')
openai_api_key = getpass('Enter your OpenAI API key: ')
my_ks = input('Your Astra Keyspace name: ')
openai.api_key = openai_api_key
cass_user = 'token'
cass_pw = ASTRA_DB_TOKEN_BASED_PASSWORD

# specify secure bundle
scb_path = os.environ['ASTRA_SCB_PATH']

model_id = "text-embedding-ada-002"

cloud_config= {
    'secure_connect_bundle': scb_path
}
auth_provider = PlainTextAuthProvider(cass_user, cass_pw)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider,
        protocol_version=4)
session = cluster.connect()
session.set_keyspace(my_ks)

session.execute(f"""CREATE TABLE IF NOT EXISTS squad
    (id text,
     title text,
     context text,
     question text,
     answers map<text,text>,
     title_context_embedding vector<float, 1536>,
     PRIMARY KEY (id,title))""")

session.execute("""
    CREATE CUSTOM INDEX IF NOT EXISTS title_context_desc
    ON squad (title_context_embedding)
    USING 'org.apache.cassandra.index.sai.StorageAttachedIndex'
    WITH OPTIONS = {'similarity_function' : 'dot_product'}
""")

data = load_dataset('squad', split='train')

data = data.to_pandas()
data.head()

data.drop_duplicates(subset='context', keep='first', inplace=True)
data.head()

counter = 0
total = 0

for id, row in data.iterrows():

    converted_answers = dict()
    converted_answers['text'] = row.answers['text'][0]
    converted_answers['answer_start'] = str(row.answers['answer_start'][0])

    full_chunk = f"{row.context} {row.title}"
    embedding = openai.Embedding.create(input=full_chunk, 
            model=model_id)['data'][0]['embedding']

    query = SimpleStatement(f"""
            INSERT INTO squad
            (id, title, context, question, answers, title_context_embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
        """)

    session.execute(query, (row.id, row.title, row.context, row.question, 
        converted_answers, embedding))

    counter += 1
    total += 1

    if(total >= 300):
        break

    if (counter >= 60):
        counter = 0
        time.sleep(60)
#end of loop
