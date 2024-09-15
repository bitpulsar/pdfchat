# app.py
import streamlit as st
from init_collection import get_client, create_collection
# can separate into multiple functions for cleaner code.
from unstructured.partition.pdf import partition_pdf
def insert_chunks_from_file(pdf_path):
    partitions = partition_pdf(pdf_path)
    chunks = [str(part) for part in partitions]
    data_objects = [{"content": chunk, "source": pdf_path} for chunk in chunks]
    
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for data_object in data_objects:
            batch.add_data_object(data_object, "Document")

# def perform_search(query, prompt):
#     response = client.query.get("Document", ["content", "source"]) \
#         .with_near_text({"concepts": [query]}) \
#         .with_additional("generate(single_prompt: $prompt)") \
#         .with_limit(2) \
#         .do()
#     return response


#Performing search using Weaviate generative search. Can use single task too.
def perform_search(query, prompt):
    collection_of_docs = client.collections.get("Document")
    response = collection_of_docs.generate.near_text(
        query=query,
        grouped_task=prompt,
        limit=2
    )
    return response

# Load environment variables
openai_key = st.secrets["default"]["OPENAI_API_KEY"]
wcd_api_key = st.secrets["default"]["WCD_API_KEY"]
wcd_url = st.secrets["default"]["WCD_URL"]

# Connect to Weaviate
client = get_client()
create_collection(client)  # Ensure the collection is created

st.header("Upload and Process PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file:
  save_path = f"/tmp/{uploaded_file.name}"
  with open(save_path, "wb") as f:
    f.write(uploaded_file.getbuffer())
  insert_chunks_from_file(save_path)
  st.success(f"Inserted chunks from {uploaded_file.name}")

 

st.header("Search Your Documents")
query = st.text_input("Enter your search query")
prompt = st.text_input("Enter your search prompt")

if st.button("Perform Search"):
  if query and prompt:
    search_results = perform_search(query, prompt)
    st.write("Search Results:")
    st.write(search_results.generated)
else:
  st.error("Please enter both query and prompt.")