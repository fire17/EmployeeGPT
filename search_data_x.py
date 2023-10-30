import os
 # import your OpenAI key (put in your .env file)
with open('.env','r') as f:
    env_file = f.readlines()

envs_dict = {key.strip("'") :value.strip("\n") for key, value in [(i.split('=')) for i in env_file]}
os.environ['OPENAI_API_KEY'] = envs_dict['OPENAI_API_KEY']#


from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Define a document schema
class MovieDoc(BaseDoc):
    title: str
    description: str
    embedding: NdArray[1536]


movies = [
    {"title": "The Great Quest", "description": "an wholesome movie about the future of humanity, year: 1999"},
    {"title": "#Wishes and Contracts", "description": "The tale of Akeyo, how the world was changed, year: 2001"},
]

# Embed `description` and create documents
docs = DocList[MovieDoc](
    MovieDoc(embedding=embeddings.embed_query(str(movie)), **movie)
    for movie in movies
)



from docarray.index import (
    InMemoryExactNNIndex,
)

# Select a suitable backend and initialize it with data
db = InMemoryExactNNIndex[MovieDoc](docs)


from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import DocArrayRetriever


# Create a retriever
retriever = DocArrayRetriever(
    index=db,
    embeddings=embeddings,
    search_field="embedding",
    content_field="description",
)

# Use the retriever in your chain
model = ChatOpenAI()
qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever, verbose=True)
conv = []
res = qa.run(question="Which movie came out in 2001?",chat_history=conv)
print(res)

