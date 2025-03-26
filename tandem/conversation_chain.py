import re

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel


def get_simplified_traditional_converter_chain():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    converter_system_prompt = """Transcribe all simplified Chinese characters in this input to traditional Chinese characters. Reproduce everything else unchanged. Don't add anything else, just produce an exact transcription.

    -----
    Example input:

    你怎么样？

    Example output:

    你怎麼樣？
    -----
    """

    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain


def get_hanzi_pinyin_converter_chain():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    converter_system_prompt = """Transcribe all Chinese characters in this input to Pinyin. Don't add anything else, just produce an exact transcription.

    -----
    Example input:

    你怎么样？

    Example output:

    Nǐ zěnme yàng？
    -----
    """

    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain


def get_chinese_english_translation_chain():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    converter_system_prompt = """Translate this Chinese input into English. Don't add or alter anything else, just produce an accurate translation.

    -----
    Example input:

    你怎么样？

    Example output:

    How are you?
    -----

    """
    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain


def sentence_splitter(input: dict[str, str]):
    result = {}
    for key, msg in input.items():
        outputs = re.split("[,.?!:;¸\"？。：“「」…]", input)
        pos = 0
        this_result = []
        for piece in outputs:
            sep_pos = pos + len(piece)
            this_result.append(f"{piece}{msg[sep_pos]}")
            pos = sep_pos + 1
        result[key] = this_result
    return result


def get_converter_chain():
    parallel_converters = RunnableParallel(
        simplified2traditional=get_simplified_traditional_converter_chain(),
        hanzi2pinyin=get_hanzi_pinyin_converter_chain(),
        hanzi2english=get_chinese_english_translation_chain()
    )
    converter_chain = parallel_converters() | sentence_splitter
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
    converter = get_converter_chain()

    tandem_partner = {"input": tandem} | converter
    return tandem_partner
