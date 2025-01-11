import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

def load_data(file, file_type):
    """
    Load the file into pandas dataframe based on the filetype
    :param file: Uploaded file
    :param file_type: Type of file (csv, json, txt)
    :return: Pandas DataFrame
    """
    if file_type == "csv":
        return pd.read_csv(file)
    elif file_type == "json":
        return pd.read_json(file)
    elif file_type == "txt":
        # Assuming each line in the txt file is a seperated record
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return pd.DataFrame({"text": [line.strip() for line in lines]})
    else:
        raise ValueError(f"Unsupported file type:{file_type}")

def create_vector_store(data):
    """
    Create a FAISS vector store from the dataset using Hugging face embeddings
    """
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        if "text" in data.columns:
            texts = data["text"].tolist()
        else:
            documents = data.to_dict(orient="records")
            texts = [str(doc) for doc in documents]
        vector_store = FAISS.from_texts(texts,embeddings)
        return vector_store
    except Exception as e:
        raise Exception(f"Error creating vector store: {str(e)}")

def create_rag_pipeline(vector_store, model_name, groq_api_key):
    """
    Set up the RAG pipeline using langchain with a selected LLM Model
    """
    try:
        retriever = vector_store.as_retriever()
        llm = ChatGroq(
            groq_api_key = groq_api_key,
            model_name = model_name
        )
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        return qa_chain
    except Exception as e:
        raise Exception(f"Error creating RAG pipeline: {str(e)}")
