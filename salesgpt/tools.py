from langchain.agents import Tool
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
# use python3.10 & chromadb-0.3.29 to save yourselves trouble with sqlite


# from abc import ABC, abstractmethod
# from typing import Any, List
# from langchain.schema import Document
# from langchain.callbacks.manager import Callbacks



# class BaseRetriever(ABC):
#     def get_relevant_documents(
#         self, query: str, *, callbacks: Callbacks = None, **kwargs: Any
#     ) -> List[Document]:
#         """Retrieve documents relevant to a query.
#         Args:
#             query: string to find relevant documents for
#             callbacks: Callback manager or list of callbacks
#         Returns:
#             List of relevant documents
#         """
#         print(f"Retrieving documents relevant to query: {query} ::: ",callbacks,)
#         ...

#     async def aget_relevant_documents(
#         self, query: str, *, callbacks: Callbacks = None, **kwargs: Any
#     ) -> List[Document]:
#         """Asynchronously get documents relevant to a query.
#         Args:
#             query: string to find relevant documents for
#             callbacks: Callback manager or list of callbacks
#         Returns:
#             List of relevant documents
#         """
#         ...

def setup_knowledge_base(manifest: str = None):
    """
    We assume that the product catalog is simply a text string.
    """
    # load product catalog
    with open(manifest, "r") as f:
        manifest = f.read()

    text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
    texts = text_splitter.split_text(manifest)

    llm = OpenAI(temperature=0)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
        texts, embeddings, collection_name="ace-menu"
    )

    # def get_docs(*args,**kwargs):
    #     print(" ***************************************** ")
    #     print(" ************* GETTING DOCS ************** ")
    #     print(args,kwargs)
    #     print(" ***************************************** ")
    #     print(" ***************************************** ")
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
        # llm=llm, chain_type="stuff", retriever={"_get_relevant_documents":get_docs} # make custome retriever
        # llm=llm, chain_type="stuff", retriever={"_get_relevant_documents":get_docs}
        # llm=llm, chain_type="stuff", retriever=retriever
    )
    return knowledge_base


def EventTool(*args, **kwargs):
    print("@@@@@@@@@@!!!!!!!!!!!!!!!!!! EVENT TOOL!!!", args, kwargs)
    return {}

def get_tools(knowledge_base):
    # we only use one tool for now, but this is highly extensible!
    tools = [
        # Tool(
        #     name="EventTool",
        #     func=EventTool,
        #     description="You must use this tool once per turn to signal ",
        # ),
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            description="useful for when you need to answer questions about product information",
        )
    ]

    return tools
'''
TODO: Add more CUSTOM tools, call my own functions
Changes: Tool: System Events
'''