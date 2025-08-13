
from typing import List
from firebase_functions import firestore_fn
from google.cloud.firestore import DocumentSnapshot
from firebase_admin import firestore
from pydantic import BaseModel, Field
from samples.medical_documents import get_medical_documents
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms, DiagnosisProbability
from models.transcription import TranscriptionStatus
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.output_parsers import PydanticOutputParser

class ReportOutput(BaseModel):
    report: str = Field(description="The markdown diagnosis report")
    diagnosis_probabilities: List[DiagnosisProbability] = Field(description="A list of probable diagnoses of the patient's condition")

class DiagnosisList(BaseModel):
    diagnosis_probabilities: List[DiagnosisProbability] = Field(description="List of probable diagnoses")

@firestore_fn.on_document_created(document="clinical_record/{session_id}")
def diagnosis_generation_handler(event: firestore_fn.Event[DocumentSnapshot]) -> None:
    """
    Firebase function triggered when a clinical record document is created in Firestore.
    
    This function receives the clinical record data and should generate a diagnosis.
    """
    try:
        # Get the document data
        session_id = event.params.get("session_id")
        assert session_id, "Session ID is required"
        print(f"Diagnosis generation triggered for session: {session_id}")
        if event.data:
            data_dict = event.data.to_dict()
            clinical_record = ClinicalRecord(**data_dict)
        else:
            print("Empty object provided on function invoke")
            return
        
        set_processing_status(session_id, TranscriptionStatus.DIAGNOSIS_STARTED)
        diagnosis_report: str = generate_diagnosis_report(clinical_record)
        diagnosis_probability: List[DiagnosisProbability] = extract_diagnosis_from_report(diagnosis_report)

        diagnosis: ReportOutput = ReportOutput(
            report=diagnosis_report,
            diagnosis_probabilities=diagnosis_probability
        )

        save_diagnosis_report(clinical_record.session_id, diagnosis)
        
        set_processing_status(session_id, TranscriptionStatus.DIAGNOSIS_FINISHED)
        print('Diagnosis generation complete')

    except Exception as e:
        print(f"Error in diagnosis_generation: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, TranscriptionStatus.DIAGNOSIS_ERROR, str(e))
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")


def set_processing_status(session_id: str, status: TranscriptionStatus, error_message: str = "") -> None:
    db = firestore.client()
    doc_ref = db.collection('transcriptions').document(session_id)
    doc_ref.update({
        "status": status.value,
        "error_message": error_message,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Updated status for session {session_id}")

def generate_diagnosis_report(clinical_record: ClinicalRecord) -> str:
    """
    Generate comprehensive diagnosis with treatment plan and recommendations using LLM.
    
    Returns markdown-formatted report combining:
    - Diagnosis with estimated probabilities using multi-step reasoning
    - Treatment plan personalized by age and symptoms
    - Recommendations including alerts for critical symptoms
    """
    print("Starting diagnosis generation with multi-step reasoning")
        # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # Get relevant medical knowledge using RAG
    medical_context = retrieve_medical_knowledge(clinical_record)
    
    # Build the comprehensive diagnosis prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an experienced doctor with expertise in clinical diagnosis, treatment planning, and patient care.

        You are given a clinical case of a patient.
        Your task is to generate a report about this clinical case.

        The report should be in the following format using proper markdown structure:
        
        # Diagnosis
        
        You need to analyze the patient's symptoms, their severity, and duration.
        Consider the patient's age, demographic factors, behavior, lifestyle, nutrition, hydration, and other factors that might be relevant for the diagnosis.
        Then:
        - Generate a list of probable diagnosis using evidence-based reasoning.
        - Assign probability estimates (0-100%) for each diagnosis based on the probability of the patient having the disease given their clinical case.
        - Explain the disease and the reasoning behind the probable diagnosis. Relate the patient's symptoms to the diagnosis.
        - Select the most likely diagnosis of the patient. Justify your selection with clinical reasoning.
        - Use the following text extracted from a medical knowledge base for evidence-based reasoning:
        
        {medical_context}

        # Treatment Plan
        
        - Create a personalized treatment plan to treat the patient's symptoms and disease.
        - Consider symptom severity in treatment intensity.
        - Include both pharmacological and non-pharmacological interventions (if applicable) to treat the patient's symptoms and disease.

        # Recommendations
        
        - Identify and alert if the patient has critical symptoms.
        - Provide follow-up recommendations (if applicable).
        - Include recommended tests and procedures for better diagnosis accuracy.

        ---

        **Formatting Instructions:**
        - Use "#" for main section titles (Diagnosis, Treatment Plan, Recommendations)
        - Use "##" for subsections within each main section (e.g., "## Probable Diagnoses", "## Most Likely Diagnosis")
        - Use "###" for sub-subsections if needed (e.g., "### Pharmacological Interventions", "### Non-Pharmacological Interventions")
        - Use bullet points for lists and readability
        - Use **bold** for emphasis on important information
        - Use *italic* for medical terms or emphasis

        ---

        IMPORTANT: Return ONLY the markdown content without any code block delimiters (no ```markdown or ``` at the beginning or end).
        """),
        ("human", """Please analyze this clinical case and provide a comprehensive diagnosis report:

        Clinical Record:
        {summary}

        Patient Information:
        {patient_info}
        
        Reason for visit:
        {reason_for_visit}

        Symptoms Analysis:
        {symptoms_details}
        """)
    ])
    
    # Format symptoms for the prompt
    symptoms_details = format_symptoms_for_prompt(clinical_record.classified_symptoms or [])

    # Prepare prompt variables
    chain = prompt_template | llm
    
    try:
        print("Generating diagnosis")
        response = chain.invoke({
            "medical_context": medical_context,
            "summary": clinical_record.summary,
            "patient_info": clinical_record.patient_info.model_dump_json(),
            "reason_for_visit": clinical_record.reason_for_visit or "Not specified",
            "symptoms_details": symptoms_details,
        })
        
        print("Diagnosis generation completed successfully")
        return response.content
        
    except Exception as e:
        print(f"Error generating diagnosis: {str(e)}")
        raise "Unable to generate diagnosis at this time."

def extract_diagnosis_from_report(diagnosis_report: str) -> List[DiagnosisProbability]:
    """
    Extract diagnosis from the report.
    """
    try:
        print("Extracting diagnosis from report")

        json_parser = PydanticOutputParser(pydantic_object=DiagnosisList)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
            You are given a report of a clinical case of a patient.
            Your task is to extract the exact List of probable diagnoses from the report
            and return with the following format:

            {format_instructions}
            """),
            ("human", """Please analyze this clinical case and provide a comprehensive diagnosis report:
            {diagnosis_report}
            """),
        ])
        chain = prompt_template | llm | json_parser
        response: DiagnosisList = chain.invoke({
            "diagnosis_report": diagnosis_report,
            "format_instructions": json_parser.get_format_instructions()
            })
        return response.diagnosis_probabilities
    except Exception as e:
        print(f"Error extracting diagnosis from report: {str(e)}")
        raise "Unable to extract diagnosis from report at this time."
     

def retrieve_medical_knowledge(clinical_record: ClinicalRecord) -> str:
    """
    Simple RAG implementation using in-memory vector store with medical knowledge.
    """
    try:
        print("Retrieving medical knowledge")
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Create a simple medical knowledge base
        medical_documents = get_medical_documents()
        
        # Initialize vector store
        vector_store = InMemoryVectorStore(embeddings)
        vector_store.add_documents(medical_documents)
        
        # Create query from symptoms and patient info
        query_parts = []
        if clinical_record.classified_symptoms:
            symptom_names = [s.name for s in clinical_record.classified_symptoms]
            query_parts.extend(symptom_names)
        
        if clinical_record.reason_for_visit:
            query_parts.append(clinical_record.reason_for_visit)
            
        query = " ".join(query_parts)
        
        # Retrieve relevant knowledge
        relevant_docs = vector_store.similarity_search(query, k=3)
        
        # Format context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"- {doc.page_content}")
        
        return "\n".join(context_parts) if context_parts else "General medical knowledge base available for consultation."
        
    except Exception as e:
        print(f"Error retrieving medical knowledge: {str(e)}")
        return "Medical knowledge base temporarily unavailable."

def format_symptoms_for_prompt(symptoms: List[ClassifiedSymptoms]) -> str:
    """Format symptoms data for inclusion in the LLM prompt."""
    if not symptoms:
        return "No specific symptoms documented."
    
    formatted_symptoms = []
    for symptom in symptoms:
        # Build details list
        details = [f"{type}: {value}" for type, value in [
            ("Severity", symptom.severity),
            ("Intensity", symptom.intensity),
            ("Duration", symptom.duration),
            ("Confidence", str(symptom.confidence_score))
        ] if value is not None]
        
        # Format: "- **symptom_name** - detail1 - detail2"
        detail_suffix = " - " + " - ".join(details) if details else ""
        formatted_symptoms.append(f"- **{symptom.name}**{detail_suffix}")
    
    return "\n".join(formatted_symptoms)


def save_diagnosis_report(session_id: str, diagnosis: ReportOutput) -> None:
    """
    Save the diagnosis report to Firestore.
    """
    print(f'Saving diagnosis report for session: {session_id}')
    db = firestore.client()
    doc_ref = db.collection('clinical_record').document(session_id)
    
    doc_ref.update({
        "diagnosis_report": diagnosis.report,
        "diagnosis": [d.model_dump() for d in diagnosis.diagnosis_probabilities],
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    print(f"Diagnosis report saved to Firestore for session: {session_id}")
