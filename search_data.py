
'''
Load OPENAI KEY
'''
import os
 # import your OpenAI key (put in your .env file)
with open('.env','r') as f:
    env_file = f.readlines()

envs_dict = {key.strip("'") :value.strip("\n") for key, value in [(i.split('=')) for i in env_file]}
os.environ['OPENAI_API_KEY'] = envs_dict['OPENAI_API_KEY']#

'''
%pip install redis pandas 
%pip install -U sentence-transformers
%pip install openai
%pip install langchain
'''

import numpy as np
import pandas as pd
import time
from redis.commands.search.field import VectorField
from redis.commands.search.field import TextField
from redis.commands.search.field import TagField
from redis.commands.search.query import Query
import redis
import time

# redis_conn = redis.Redis(
#   host='redis-18975.c300.eu-central-1-1.ec2.cloud.redislabs.com',
#   port=18975,
#   password='xxxxxxxxxxx')


from atom import xo

redis_conn = xo._redis

MAX_TEXT_LENGTH=512
NUMBER_PRODUCTS=1000

def auto_truncate(val):
    return val[:MAX_TEXT_LENGTH]

#Load Product data and truncate long text fields
all_prods_df = pd.read_csv("product_data.csv", converters={'bullet_point': auto_truncate,'item_keywords':auto_truncate,'item_name':auto_truncate})
all_prods_df['primary_key'] = all_prods_df['item_id'] + '-' + all_prods_df['domain_name']
all_prods_df['item_keywords'].replace('', np.nan, inplace=True)
all_prods_df.dropna(subset=['item_keywords'], inplace=True)
all_prods_df.reset_index(drop=True,inplace=True)

#get the first 1000 products with non-empty item keywords
product_metadata = all_prods_df.head(NUMBER_PRODUCTS).to_dict(orient='index')

all_prods_df.head()

###############################
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')


item_keywords =  [product_metadata[i]['item_keywords']  for i in product_metadata.keys()]
item_keywords_vectors = [ model.encode(sentence) for sentence in item_keywords]

###############################
len(item_keywords_vectors)
len(product_metadata)
# Check one of the products
product_metadata[0]
###############################
def load_vectors(client, product_metadata, vector_dict, vector_field_name):
    p = client.pipeline(transaction=False)
    for index in product_metadata.keys():    
        #hash key
        key='product:'+ str(index)+ ':' + product_metadata[index]['primary_key']
        
        #hash values
        item_metadata = product_metadata[index]
        item_keywords_vector = vector_dict[index].astype(np.float32).tobytes()
        item_metadata[vector_field_name]=item_keywords_vector
        
        # HSET
        p.hset(key,mapping=item_metadata)
            
    p.execute()

def create_flat_index (redis_conn,vector_field_name,number_of_vectors, vector_dimensions=512, distance_metric='L2'):
    redis_conn.ft().create_index([
        VectorField(vector_field_name, "FLAT", {"TYPE": "FLOAT32", "DIM": vector_dimensions, "DISTANCE_METRIC": distance_metric, "INITIAL_CAP": number_of_vectors, "BLOCK_SIZE":number_of_vectors }),
        TagField("product_type"),
        TextField("item_name"),
        TextField("item_keywords"),
        TagField("country")        
    ]) 
###############################
ITEM_KEYWORD_EMBEDDING_FIELD='item_keyword_vector'
TEXT_EMBEDDING_DIMENSION=768
NUMBER_PRODUCTS=1000

print ('Loading and Indexing + ' +  str(NUMBER_PRODUCTS) + ' products')

#flush all data
redis_conn.flushall()

#create flat index & load vectors
create_flat_index(redis_conn, ITEM_KEYWORD_EMBEDDING_FIELD,NUMBER_PRODUCTS,TEXT_EMBEDDING_DIMENSION,'COSINE')
load_vectors(redis_conn,product_metadata,item_keywords_vectors,ITEM_KEYWORD_EMBEDDING_FIELD)
###############################
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key="sk-....")
prompt = PromptTemplate(
    input_variables=["product_description"],
    template="Create comma seperated product keywords to perform a query on a amazon dataset for this user input: {product_description}",
)

from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt, verbose = True)

userinput = input("Hey im a E-commerce Chatbot, how can i help you today? ")
print("User:", userinput)
# Run the chain only specifying the input variable.
keywords = chain.run(userinput)


topK=3
#vectorize the query
query_vector = model.encode(keywords).astype(np.float32).tobytes()

#prepare the query
q = Query(f'*=>[KNN {topK} @{ITEM_KEYWORD_EMBEDDING_FIELD} $vec_param AS vector_score]').sort_by('vector_score').paging(0,topK).return_fields('vector_score','item_name','item_id','item_keywords').dialect(2)
params_dict = {"vec_param": query_vector}

#Execute the query
results = redis_conn.ft().search(q, query_params = params_dict)

full_result_string = ''
for product in results.docs:
    full_result_string += product.item_name + ' ' + product.item_keywords + ' ' + product.item_id + "\n\n\n"


from langchain.memory import ConversationBufferMemory

template = """You are a chatbot. Be kind, detailed and nice. Present the given queried search result in a nice way as answer to the user input. dont ask questions back! just take the given context

{chat_history}
Human: {user_msg}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "user_msg"], 
    template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")
llm_chain = LLMChain(
    llm=OpenAI(model_name="gpt-3.5-turbo", temperature=0.8, openai_api_key="sk-...."), 
    prompt=prompt, 
    verbose=True, 
    memory=memory,
)

answer = llm_chain.predict(user_msg= f"{full_result_string} ---\n\n {userinput}")
print("Bot:", answer)
time.sleep(0.5)
###############################

while True:
    follow_up = input("Anything else you want to ask about this topic?")
    print("User:", follow_up)
    answer = llm_chain.predict(
        user_msg=follow_up
    )
    print("Bot:", answer)
    time.sleep(0.5)

###############################