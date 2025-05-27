from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

from models.models import DiagnosisReport

llm = init_chat_model("openai:gpt-4.1")

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a neurologist and you have to identify the diagnosis in the provided report  associated with the ICD-10 code and category of the diagnosis.
            The possible categories are as follows: Multiple sclerosis, cancer, stroke, Parkinson disease, Alzheimer or Other.
            
             Output your answer as JSON that  "
            "matches the given schema: \`\`\`json\n{schema}\n\`\`\`. "
            "Make sure to wrap the answer in \`\`\`json and \`\`\` tags",
            """
        ),
        ("human", "{query}"),
    ]
).partial(schema=DiagnosisReport.model_json_schema())

def generate_diagnosis_report(answer:str):
    parser = PydanticOutputParser(pydantic_object=DiagnosisReport)
    query = answer
    chain = prompt | llm | parser
    report: DiagnosisReport = chain.invoke({"query": query})
    return report
