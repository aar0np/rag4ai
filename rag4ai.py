import openai
#import numpy
#import pandas as pd
#import time
import os

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

ASTRA_DB_TOKEN_BASED_PASSWORD = os.environ['ASTRA_DB_APPLICATION_TOKEN']
openai_api_key = os.environ['OPENAI_API_KEY']
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

customer_input = """
        when was the college of engineering in the University
        of Notre Dame established?
    """

while customer_input != "exit":

    embedding = openai.Embedding.create(input=customer_input,
            model=model_id)['data'][0]['embedding']

    #print(embedding)

    query = SimpleStatement(f"""
        SELECT *
        FROM squad
        ORDER BY title_context_embedding ANN OF {embedding} LIMIT 3;
        """)
    #print(query)

    results = session.execute(query)

    top_3_results = results._current_rows

    #for row in top_3_results:
    #    print(f"""{row.context}\n""")

    message_objects = []

    message_objects.append({"role":"system",
            "content":"You're a chatbot helping customers with questions."})

    message_objects.append({"role":"user", "content": customer_input})

    answers_list = []

    for row in top_3_results:
        brand_dict = {'role': "assistant", "content": f"{row.context}"}
        answers_list.append(brand_dict)

    message_objects.extend(answers_list)
    message_objects.append({"role": "assistant", "content":"Here's my answer to your question."})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_objects
    )

    print(completion.choices[0].message['content'] + "\n")

    customer_input  = input('Next question? ')

print("Exiting...")
