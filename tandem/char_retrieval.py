from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores.chroma import Chroma


def generate_character_db(character_txt_path: str, persist_directory: Optional[str] = None):
    persist_directory = persist_directory or f".chroma/{Path(character_txt_path).stem}"
    # split documents if necessary
    # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20, separators=["\n"])
    # char_embedding = splitter.split_documents(char_embedding)

    loader = TextLoader(character_txt_path, encoding="utf-8")
    char_documents = loader.load()

    db = Chroma.from_documents(char_documents, embedding=OpenAIEmbeddings(), persist_directory=persist_directory)
    return db


def get_output_converter():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    converter_system_prompt = """Given the provided input, replace all simplified Chinese characters with traditional Chinese characters, add Pinyin and English translation. Do NOT answer the question, just return the input with the described changes.

Output format:

1. [chinese characters] (pinyin) – (english translation)
...
"""
    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain

def get_character_list(db_path: str, topic):
    db = Chroma(persist_directory=db_path, embedding_function=OpenAIEmbeddings())

    prompt = ChatPromptTemplate.from_template(
"""
Please select up to 10 traditional characters from the provided context and form words with them that could be used in a Chinese conversation about the provided topic.

<context>
{context}
</context>

Topic: {input}

Output format:

1. [chinese characters]
...
"""
    )
    document_chain = create_stuff_documents_chain(llm=ChatOpenAI(temperature=0.5), prompt=prompt)
    retriever = db.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain) | StrOutputParser()

    converter_chain = get_output_converter()

    chain = {"input": retrieval_chain} | converter_chain
    result = chain.invoke({"input": topic})
    return result
