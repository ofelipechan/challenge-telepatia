from typing import List
from firebase_functions import firestore_fn
from firebase_admin import firestore
from google.cloud.firestore import DocumentSnapshot
from models.medical_extraction import MedicalExtraction
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from models.transcription import Transcription, TranscriptionStatus
from samples.medical_extraction_examples import get_examples

@firestore_fn.on_document_created(document="transcriptions/{session_id}")
def information_extractor_handler(event: firestore_fn.Event[DocumentSnapshot]) -> None:
    """
    Firebase function triggered when a transcription document is created in Firestore.
    
    This function receives the transcription data and should extract medical information.
    For now, it only prints the received value as requested.
    """
    try:
        # Get the document data
        session_id = event.params.get("session_id")
        assert session_id, "Session ID is required"
        print(f"Information extractor triggered for session: {session_id}")
        if event.data:
            data_dict = event.data.to_dict()
            transcription = Transcription(**data_dict)
        else:
            print("Empty object provided on function invoke")
            return
        
        # Update the document status to indicate processing started
        set_processing_status(session_id, TranscriptionStatus.INFORMATION_EXTRACTION_STARTED)
        
        medical_extraction: MedicalExtraction = extract_medical_information(transcription)

        symptoms: List[ClassifiedSymptoms] = symptoms_severity_classification(medical_extraction)

        clinical_record = ClinicalRecord(
            **medical_extraction.model_dump(),
            session_id=session_id,
            classified_symptoms=symptoms
        )
        
        save_clinical_record(clinical_record)
        set_processing_status(session_id, TranscriptionStatus.INFORMATION_EXTRACTION_FINISHED)
        
        print('information extraction complete')
        
    except Exception as e:
        print(f"Error in information_extractor: {str(e)}")
        if session_id:
            try:
                set_processing_status(session_id, TranscriptionStatus.TRANSCRIPTION_ERROR, str(e))
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

def extract_medical_information(transcription: Transcription) -> MedicalExtraction:
    """
    Extract medical information from transcription
    """
    

    print("Start processing transcription for extraction")
    json_parser = PydanticOutputParser(pydantic_object=MedicalExtraction)
    # json_parser = JsonOutputParser(pydantic_object=MedicalExtraction)

    chain = build_chain(json_parser)

    print("invoke chain")

    result: MedicalExtraction = chain.invoke(input={
        "transcription": transcription.text,
        "format_instructions": json_parser.get_format_instructions(),
    })
    print("got result from chain invoke")

    return result

def symptoms_severity_classification(medical_extraction: MedicalExtraction) -> List[ClassifiedSymptoms]:
    print('Classify symptoms classification using semantic similarity embeddings')
    
    if not medical_extraction.symptoms:
        return []
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Create severity reference documents for vector store
    severity_documents = [
        Document(
            page_content="Minor discomfort, slight symptoms, minimal impact on daily activities, barely noticeable",
            metadata={"severity": "mild"}
        ),
        Document(
            page_content="Noticeable discomfort, some impact on daily activities, manageable symptoms, requires attention",
            metadata={"severity": "moderate"}
        ),
        Document(
            page_content="Significant discomfort, major impact on daily activities, intense symptoms, major limitations",
            metadata={"severity": "severe"}
        ),
        Document(
            page_content="Life-threatening, emergency symptoms, extreme discomfort, requires urgent medical intervention",
            metadata={"severity": "critical"}
        )
    ]
    
    # Initialize vector store with severity references
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(severity_documents)
    
    classified_symptoms = []
    
    for symptom in medical_extraction.symptoms:
        # Create symptom query text
        symptom_text = f"{symptom.name}"
        if symptom.duration:
            symptom_text += f" lasting {symptom.duration}"
            
        # Search for most similar severity level
        results = vector_store.similarity_search_with_score(symptom_text, k=4)
        
        # Get the best match (highest similarity = lowest score)
        best_match = min(results, key=lambda x: x[1])
        severity_level = best_match[0].metadata["severity"]
        confidence_score = 1 - best_match[1]  # Convert distance to similarity score
        
        classified_symptoms.append(ClassifiedSymptoms(
            name=symptom.name,
            intensity=symptom.intensity,
            duration=symptom.duration,
            severity=severity_level,
            confidence_score=confidence_score,
        ))
    
    print(f"Classified {len(classified_symptoms)} symptoms with severity levels")
    return classified_symptoms


def build_chain(json_parser: PydanticOutputParser[MedicalExtraction]):
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.1)

    examples = get_examples()

    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}")
    ])

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
    )

    prompt_template = ChatPromptTemplate.from_messages(messages=[
        ("system", """You are a medical information extractor with expertise in clinical documentation.
        You will be given the transcription of a conversation between a doctor and a patient.
        
        Follow this chain-of-thought process:
        
        STEP 1 - PATIENT IDENTIFICATION:
        - Extract patient name, age, date of birth, nationality, and ID number if mentioned during transcription.
        - Ensure age is within reasonable range (0-120)
        
        STEP 2 - REASON FOR VISIT ANALYSIS:
        - Identify the primary complaint or reason for seeking medical care.
        - Assess urgency level.
        
        STEP 3 - SYMPTOM EXTRACTION:
        - Identify all symptoms the patient presented.
        - Add the intensity of each symptom based on the patient's speech.
        - Note the duration the symptom has persisted.
        - 
        
        STEP 4 - CONFIDENCE ASSESSMENT:
        - Evaluate completeness of information.
        - Assess clarity of medical terminology.
        - Consider ambiguity in patient statements.

        STEP 5 - GENERATE SUMMARY
        - Finalize by generating a summary of the transcription.
        - Include the patient's name, age, reason for visit and symptoms.
        - Ensure the summary is concise and informative.
        - Based in the transcription, you include information that might be relevant for the diagnosis process, such as:
          - behavior situations (actions the patient took that could have lead to the symptoms)
          - lifestyle (the patient's lifestyle, habits, and routines)
          - nutrition (what did the patient report to have eaten)
          - hydration (the patient report to getting hydrated)
          - sleep (how much sleep is the patient getting)
          - or any other relevant information.
        
        Use the following JSON schema for output:
        {format_instructions}

        Ensure all extracted data follows medical standards and validation rules."""),
        few_shot_prompt,
        ("human", "Extract medical information from this transcription using the step-by-step process: {transcription}"),
    ])

    return prompt_template | llm | json_parser

# def save_symptoms_to_firestore(session_id: str, symptoms: List[Dict[str, Any]]):
#     """Save extracted symptoms to Firestore for the next function in the chain."""
#     print(f'Saving {len(symptoms)} symptoms to Firestore for session: {session_id}')
#     db = firestore.client()
#     doc_ref = db.collection('symptoms').document(session_id)
    
#     symptoms_data = {
#         "session_id": session_id,
#         "symptoms": symptoms,
#         "extracted_at": firestore.SERVER_TIMESTAMP,
#         "status": "extracted"
#     }
    
#     doc_ref.set(symptoms_data)
#     print(f"Symptoms saved to Firestore for session: {session_id}")

def save_clinical_record(clinical_record: ClinicalRecord):
    print('Saving clinical record')
    db = firestore.client()
    doc_ref = db.collection('clinical_record').document(clinical_record.session_id)
    
    doc_ref.set(clinical_record.model_dump())
    print(f"Clinical Record saved to Firestore for session: {clinical_record.session_id}")