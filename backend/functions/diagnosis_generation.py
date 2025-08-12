
from typing import List
from firebase_functions import firestore_fn
from google.cloud.firestore import DocumentSnapshot
from firebase_admin import firestore
from pydantic import BaseModel, Field
from samples.medical_documents import get_medical_documents
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms, DiagnosisProbability
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.output_parsers import PydanticOutputParser

class ReportOutput(BaseModel):
    report: str = Field(description="The markdown diagnosis report")
    diagnosis_probability: List[DiagnosisProbability] = Field(description="Based on the Diagnosis section of the report, generate a list of probable diagnoses for the patient")

@firestore_fn.on_document_created(document="clinical_record/{session_id}")
def diagnosis_generation(event: firestore_fn.Event[DocumentSnapshot]) -> None:
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
        
        set_processing_status(session_id, "processing_diagnosis")
        diagnosis: ReportOutput = generate_diagnosis(clinical_record)
        print(f"Diagnosis report: \n\n{diagnosis.report}")
        print(f"Probabilistic differential diagnosis: \n\n{diagnosis.diagnosis_probability}")
        # Save the diagnosis report to Firestore
        save_diagnosis_report(clinical_record.session_id, diagnosis)
        
        set_processing_status(session_id, "diagnosis_complete")
        print('Diagnosis generation complete')

    except Exception as e:
        print(f"Error in diagnosis_generation: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, "error_processing_diagnosis", str(e))
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")


def set_processing_status(session_id: str, status: str, error_message: str = "") -> None:
    db = firestore.client()
    doc_ref = db.collection('transcriptions').document(session_id)
    doc_ref.update({
        "status": status,
        "error_message": error_message,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Updated status for session {session_id}")

def generate_diagnosis(clinical_record: ClinicalRecord) -> ReportOutput:
    """
    Generate comprehensive diagnosis with treatment plan and recommendations using LLM.
    
    Returns markdown-formatted report combining:
    - Diagnosis with estimated probabilities using multi-step reasoning
    - Treatment plan personalized by age and symptoms
    - Recommendations including alerts for critical symptoms
    """
    print("Starting diagnosis generation with multi-step reasoning")
    json_parser = PydanticOutputParser(pydantic_object=ReportOutput)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # Get relevant medical knowledge using RAG
    medical_context = retrieve_medical_knowledge(clinical_record)
    print(f"Medical context: {medical_context}")
    
    # Check for critical symptoms that need immediate attention
    # critical_alerts = check_critical_symptoms(clinical_record.classified_symptoms or [])
    
    # Build the comprehensive diagnosis prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an experienced doctor with expertise in clinical diagnosis, treatment planning, and patient care.

        You are given a clinical case of a patient.
        Your task is to generate a report for the patient.

        The report should be in the following format:
        
        **Diagnosis**
        You need to analyze the patient's symptoms, their severity, and duration.
        Consider the patient's age, demographic factors, behavior, lifestyle, nutrition, hydration, and other factors that might be relevant for the diagnosis.
        Then:
        - Generate a list of probable diagnosis using evidence-based reasoning.
        - Assign probability estimates (0-100%) for each diagnosis based on the probability of the patient having the disease given their clinical case.
        - Explain the disease and the reasoning behind the probable diagnosis. Relate the patient's symptoms to the diagnosis.
        - Select the most likely diagnosis of the patient. Justify your selection with clinical reasoning.
        - Use the following text extracted from a medical knowledge base for evidence-based reasoning:
        
        {medical_context}

        **Treatment plan**
        - Create a personalized treatment plan to treat the patient's symptoms and disease.
        - Consider symptom severity in treatment intensity.
        - Include both pharmacological and non-pharmacological interventions (if applicable) to treat the patient's symptoms and disease.

        **Recommendations**
        - Identify and alert if the patient has critical symptoms.
        - Provide follow-up recommendations (if applicable).
        - Include recommended tests and procedures for better diagnosis accuracy.

        ---

        Use bullet points for readability.

        ---
        IMPORTANT: You must provide your response in the exact JSON format specified below. The response should include:
        1. A "report" field containing the complete markdown diagnosis report
        2. A "diagnosis_probability" field containing a list of probable diagnoses with their probabilities, reasoning, and related symptoms.
        
        {format_instructions}
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
    chain = prompt_template | llm | json_parser
    
    try:
        print("Generating diagnosis")
        response: ReportOutput = chain.invoke({
            "medical_context": medical_context,
            "summary": clinical_record.summary,
            "patient_info": clinical_record.patient_info.model_dump_json(),
            "reason_for_visit": clinical_record.reason_for_visit or "Not specified",
            "symptoms_details": symptoms_details,
            "format_instructions": json_parser.get_format_instructions(),
        })
        
        print("Diagnosis generation completed successfully")
        return response
        
    except Exception as e:
        print(f"Error generating diagnosis: {str(e)}")
        raise "Unable to generate diagnosis at this time."


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
        "diagnosis_probability": [d.model_dump() for d in diagnosis.diagnosis_probability],
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    print(f"Diagnosis report saved to Firestore for session: {session_id}")
