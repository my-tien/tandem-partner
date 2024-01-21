from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma


def generate_vocabulary_db(vocabulary_path: str):
    with open(vocabulary_path) as vocab_file:
        vocabulary = vocab_file.read()
    # split documents if necessary
    # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20, separators=["\n"])
    # vocabulary = splitter.split_documents(vocabulary)

    embeddings = OpenAIEmbeddings()
    vocab_embedding = embeddings.embed_documents([vocabulary])
    db = Chroma.from_documents(vocabulary, vocab_embedding, persist_directory="./chroma/remembering_traditional_hanzi")
    return db


def get_vocabulary_retriever(db_path: str, llm):
    db = Chroma(persist_directory="./chroma/quiz", embedding_function=OpenAIEmbeddings())

    prompt = ChatPromptTemplate.from_template(
    """
    

    <context>
    {context}
    </context>

    Question: {input}""")

    document_prompt = ChatPromptTemplate.from_template("""Content: {page_content}""")
    document_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt,
    document_prompt=document_prompt
    )
    retriever = db.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)