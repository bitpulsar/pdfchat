# app.py
import streamlit as st
from init_collection import get_client, create_collection
# can separate into multiple functions for cleaner code.
from unstructured.partition.pdf import partition_pdf

# Connect to Weaviate
client = get_client()
create_collection(client)  # Ensure the collection is created

def insert_chunks_from_file(pdf_path):
    partitions = partition_pdf(pdf_path)
    chunks = [str(part) for part in partitions]
    data_objects = [{"content": chunk, "source": pdf_path} for chunk in chunks]
    
    for data_object in data_objects:
       client.batch.add_data_object(data_object, "Document")

    # Flush the batch to ensure all data is written
    client.batch.flush()

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

st.header("Załaduj i przetwórz PDF")
uploaded_file = st.file_uploader("Wybierz plik PDF", type="pdf")
if uploaded_file:
  save_path = f"/tmp/{uploaded_file.name}"
  with open(save_path, "wb") as f:
    f.write(uploaded_file.getbuffer())
  insert_chunks_from_file(save_path)
  client.close()
  st.success(f"Inserted chunks from {uploaded_file.name}") 

st.header("Przeszukaj dokument PDF")
query = st.text_input("Wpisz swoje zapytanie")
prompt = st.text_input("Wpisz prompt, któgo poszukujesz")

if st.button("Szukaj"):
  if query and prompt:
    search_results = perform_search(query, prompt)
    st.write("Wyniki wyszukiwania:")
    st.write(search_results.generated)
else:
  st.error("Prosze podać zapytanie oraz promt.")