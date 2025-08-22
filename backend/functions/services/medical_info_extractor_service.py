from typing import List
from models.medical_extraction import MedicalExtraction
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from models.transcription import Transcription, TranscriptionStatus
from samples.medical_extraction_examples import get_examples
from repositories.transcription_repository import set_processing_status
from repositories.clinical_record_repository import save_clinical_record


class MedicalInfoExtractor:
    def process(self, transcription: Transcription) -> None:
        """
        Firebase function triggered when a transcription document is created in Firestore.
        
        This function receives the transcription data and should extract medical information.
        For now, it only prints the received value as requested.
        """
        try:
            assert transcription.session_id, "session_id is required"  
            assert transcription.text, "empty transcription"
            set_processing_status(transcription.session_id, TranscriptionStatus.INFORMATION_EXTRACTION_STARTED)
            
            medical_extraction: MedicalExtraction = self._extract_medical_information(transcription)

            symptoms: List[ClassifiedSymptoms] = self._symptoms_severity_classification(medical_extraction)

            clinical_record = ClinicalRecord(
                **medical_extraction.model_dump(),
                session_id=transcription.session_id,
                classified_symptoms=symptoms
            )
            
            save_clinical_record(clinical_record)
            set_processing_status(transcription.session_id, TranscriptionStatus.INFORMATION_EXTRACTION_FINISHED)
        except Exception as e:
            print(f"Error in information_extractor: {str(e)}")
            if transcription.session_id:
                try:
                    set_processing_status(transcription.session_id, TranscriptionStatus.INFORMATION_EXTRACTION_ERROR, str(e))
                except Exception as update_error:
                    print(f"Failed to update error status: {str(update_error)}")

    def _extract_medical_information(self, transcription: Transcription) -> MedicalExtraction:
        """
        Extract medical information from transcription
        """
        print("Start processing transcription for extraction")
        json_parser = PydanticOutputParser(pydantic_object=MedicalExtraction)
        # json_parser = JsonOutputParser(pydantic_object=MedicalExtraction)

        chain = self._build_chain(json_parser)

        result: MedicalExtraction = chain.invoke(input={
            "transcription": transcription.text,
            "format_instructions": json_parser.get_format_instructions(),
        })

        print("Medical extraction information finished")

        return result

    def _symptoms_severity_classification(self, medical_extraction: MedicalExtraction) -> List[ClassifiedSymptoms]:
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


    def _build_chain(self, json_parser: PydanticOutputParser[MedicalExtraction]):
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
