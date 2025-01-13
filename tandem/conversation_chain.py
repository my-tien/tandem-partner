import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_contextualizer_chain():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    contextualizer_system_prompt = """Given a chat history and the latest user input which might reference context in the chat history, formulate a standalone input which 
can be understood without the chat history. Do NOT answer the input, just reformulate it if needed and otherwise return it as is."""
    contextualizer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualizer_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    contextualizer_chain = contextualizer_prompt | llm | StrOutputParser()
    return contextualizer_chain


def get_simplified_traditional_converter_chain():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    converter_system_prompt = """Given the provided input, replace all simplified Chinese characters with traditional Chinese characters and add a Pinyin transcription as well as an English translation. Use the below output format. Do NOT answer the input, just return the input with the described changes.    
    Output format:

    <message in traditional chinese characters>
    ---
    <message in Pinyin transcription>
    ---
    <english translation of the message>
    """
    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain

def get_tandem_chain(stories: str):
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)
    tandem_system_message = f"""You are Lang, a teacher for Chinese language. The user intends to practice Chinese by answering comprehension questions about the short stories in the provided context below. The conversation should be driven by your comprehension questions. Provide feedback about the correctness and grammar of the user's answer in Chinese and help them with any question they might have. Each lesson begins with the user choosing one story to talk about.
    
<context>
{stories}
</context>"""
    tandem_prompt = ChatPromptTemplate.from_messages([("system", tandem_system_message), ("user", "{input}")])
    tandem_chain = tandem_prompt | llm | StrOutputParser()

    return tandem_chain


def get_tandem_chain_chars(character_list: str):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    tandem_system_message = f"""You are Lang, a tandem partner who is native in Chinese. The user intends to practice Chinese and the typical usage of characters through a casual conversation with you. In the provided context is a list of characters that your tandem partner intends to practice. Whenever it makes sense, incorporate one or more of the characters into your response. Also include a remark or question toward the user to continue the conversation. Keep your response within 1 - 3 sentences.

<context>
{character_list}
</context>
"""

    tandem_prompt = ChatPromptTemplate.from_messages([("system", tandem_system_message), ("user", "{input}")])
    tandem_chain = tandem_prompt | llm | StrOutputParser()

    return tandem_chain


def get_tandem_partner(character_list):
    tandem = get_tandem_chain(character_list)
    converter = get_simplified_traditional_converter_chain()

    tandem_partner = {"input": tandem} | converter
    return tandem_partner
