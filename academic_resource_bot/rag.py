import pymupdf4llm
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
def text_extract(path):
    try:
        md = pymupdf4llm.to_markdown(path)
    except Exception as e:
        print(f"Error processing PDF {path}: {e}")
        return None

    pdf_filename = os.path.basename(path)
    
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""], # Try to keep paragraphs together
        chunk_size=1000,
        chunk_overlap=100
    )
    
    # Wrap the Markdown string in a list of Documents for the splitter
    temp_doc = [Document(page_content=md, metadata={"source": pdf_filename})]
    
    documents = splitter.split_documents(temp_doc)

    for i, doc in enumerate(documents):
        doc.metadata["chunk_id"] = f"chunk_{i}"
        doc.metadata["type"] = "text"
        
    return documents

def storing_in_db(documents):

    try:
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        #embedding_model = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1",model_kwargs={'device': 'cpu'})
        db = Chroma.from_documents(documents,embedding_model,persist_directory="chroma_store")
        return "sucessfully stored"
    except Exception as e:
        print(e)
        return "unsucessfull"

def retriever(query):

    #embedding_model = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1", model_kwargs={'device': 'cpu'})
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="chroma_store", embedding_function=embedding_model)

    retriever = db.as_retriever(search_kwargs={"k": 5})

    results = retriever.invoke(query)

    return "\n\n".join([doc.page_content for doc in results])

def ask_llm(query):
    load_dotenv()
    api_key = os.getenv("OPEN_ROUTER_API")

    if not api_key:
        raise ValueError("OPEN_ROUTER_API environment variable is not set.")

    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    # Get context from your retriever
    context = retriever(query)
    print("got context")

    # Build prompt
    prompt = f"""You are a helpful Academic assistant that helps students to answer their queries based on the provided context from their study materials.

    Instructions for Generating the Final Answer:
    1. *Answer Goal:* Generate a comprehensive, in-depth academic response. The length and detail must be proportional to the mark value mentioned in the Question (e.g., give answer for 10 marks, 1 mark,give line answer,for 5marks etc).
    2. *Output Schema:* Structure the entire response as a detailed, numbered list of points (1., 2., 3., etc.).
    3. *Filtering:* You MUST NOT use any special formatting characters like asterisks (*), hashes (#), hyphens (-), or dashes for lists or bolding. Use only plain text and numbered lists.
    4. *Content:* Use ALL relevant information from the context provided (Definitions, Characteristics, Steps, Advantages, Disadvantages, etc.). DO NOT use external knowledge.
    5. *Fallback:* If the context does not contain the information needed to answer the question, your entire response must be the single phrase: "I don't know".
    
    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "The AI model returned an empty or invalid response. Please try rephrasing your question."

    except Exception as e:
        print(f"An error occurred in ask_llm: {e}")
        return f"An error occurred while communicating with the AI model: {str(e)}"


def rag_pipeline():

    path="C:\\Users\\user\\Downloads\\academic_resource_bot\\downloaded_notes"

    all_documents = []
    for filename in os.listdir(path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(path, filename)
            extracted_text = text_extract(file_path)
            if extracted_text:
                all_documents.extend(extracted_text)
    stored = storing_in_db(all_documents)
    return stored