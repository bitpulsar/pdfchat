# init_collection.py
import os
import weaviate
import streamlit as st
import weaviate.classes.config as wc

def get_client():

    openai_key = st.secrets["default"]["OPENAI_API_KEY"]
    wcd_api_key = st.secrets["default"]["WCD_API_KEY"]
    wcd_url = st.secrets["default"]["WCD_URL"]

    # Connect to Weaviate
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=wcd_url,
        auth_credentials=weaviate.auth.AuthApiKey(wcd_api_key),
        headers={
            "X-OpenAI-Api-Key": openai_key
        }
    )
    return client

# Function to create collection
def create_collection(client):
    if not client.collections.exists("Document"):
        collection_of_docs = client.collections.create(
            name="Document",
            properties=[
                wc.Property(name="content", data_type=wc.DataType.TEXT),
                wc.Property(name="source", data_type=wc.DataType.TEXT, skip_vectorization=True)
            ],
            vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
            generative_config=wc.Configure.Generative.openai()
        )
        return collection_of_docs
    else:
        return client.collections.get("Document")
    # This script initializes the Weaviate client and defines the schema for the document collection. 
    # The get_client function connects to Weaviate using the provided URL and API keys. 
    # The create_collection function defines the schema for our documents, specifying that each document will have a 
    # content property (the text of the document) and a source property (the source of the document).