'''
- **[Streamlit Documentation](https://docs.streamlit.io/)**: Used for creating the interactive web application interface.
- **[LangChain Documentation](https://docs.langchain.com/)**: Referenced for implementing the Retrieval Augmented Generation (RAG) pipeline and working with retrieval-based QA systems.
- **[FAISS Documentation](https://github.com/facebookresearch/faiss)**: Utilized for building and querying the vector store for text embeddings.
- **[Groq Documentation](https://groq.com/)**: Used as the backend for efficient embedding generation and inference.
- **[Pandas Documentation](https://pandas.pydata.org/docs/)**: Used for loading and preprocessing data in various file formats.- **[Dotenv Documentation](https://pypi.org/project/python-dotenv/)**: Used for managing environment variables securely.
- **[Tiktoken Documentation](https://github.com/openai/tiktoken)**: Referenced for tokenization and embedding purposes (alternative setups can use Groq or Hugging Face).
- **[Hugging Face Transformers](https://huggingface.co/transformers/)**: A potential resource for LLM-based operations and inference.
- Various **Python community tutorials and GitHub repositories** contributed to understanding RAG concepts and implementation best practices.
'''

import streamlit as st
from utils import load_data, create_vector_store, create_rag_pipeline
import os
from dotenv import load_dotenv

#Load environment variable from .env file
load_dotenv()

#App Configuration
st.set_page_config(
    page_title= "RAG Chatbot",
    page_icon= "🤖",
    layout = "wide",
    initial_sidebar_state="expanded",
)

try:
    st.sidebar.title("Settings")
    st.sidebar.markdown("Configure your chatbot settings below:")

    #Allow model customization (Optional for advanced users)
    model_name = st.sidebar.selectbox("Select LLM Model:", ["mixtral-8x7b-32768", "llama2-70b-4096"], index=0)
    st.sidebar.write("Using: ", model_name)

    # Allowing file upload
    uploaded_file = st.sidebar.file_uploader("Upload a dataset (CSV, JSON, txt):", type=["csv","json","txt"])

    # History for tracking Q&A
    if "history" not in st.session_state:
        st.session_state.history = []

    # Title
    st.title("Retrieval Augmentation Generation (RAG) Chatbot")
    st.markdown(
        '''
        Upload your file in CSV,JSON or txt format to get started...
        '''
    )

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ API key not found. PLease set the GROQ_API_KEY environment variable")
        st.stop()

    if uploaded_file:
        try:
            # Step1: Load the dataset
            with st.spinner("Loading Dataset..."):
                data = load_data(uploaded_file, uploaded_file.name.split(".")[-1])
                st.success("Dataset loaded successfully!")

            #Step2: Create a vector store
            with st.spinner("Creating vector Store"):
                vector_store = create_vector_store(data)
                st.success("Vector store created successfully!")

            #Step3: Initializing the RAG pipeline
            with st.spinner("Setting up the Chatbot Pipeline..."):
                qa_chain = create_rag_pipeline(vector_store, model_name, groq_api_key)
                st.success("Chatbot is ready to answer your questions")

            #Step4: Chat Interface
            st.header("Chat with the bot")
            with st.form("chat_form"):
                user_query = st.text_input("Enter your question:")
                submit_button = st.form_submit_button("Submit")

            if submit_button and user_query:
                with st.spinner("Generating response..."):
                    response = qa_chain.run(user_query)
                    st.write("Chatbot's response")
                    st.write(response)

                    # Append to session state history
                    st.session_state.history.append({"Question":user_query, "Response":response})

            #Display chat history
            if st.session_state.history:
                st.subheader("Chathistory")
                for idx, item in enumerate(st.session_state.history[::-1]):
                    st.write(f"Q{len(st.session_state.history)-idx}: {item['Question']}")
                    st.write(f"A{len(st.session_state.history)-idx}: {item['Response']}")

            #Export Chat history
            if st.button("Download Chat History"):
                os.makedirs("response", exist_ok=True)
                history_path = os.path.join("response","chat_history.txt")

                with open(history_path, "w", encoding="utf-8") as f:
                    for idx, item in enumerate(st.session_state.history):
                        f.write(f"Q{idx + 1}:{item['Question']}\n")
                        f.write(f"A{idx + 1}:{item['Response']}\n\n")
                st.success(f"Chat history saved to {history_path}")

        except Exception as e:
            st.error(f"Error:{str(e)}")
    else:
        st.info("Please upload a file to proceed")

except Exception as e:
    st.error(f"An unexpected error occured: {str(e)}")
    raise e














