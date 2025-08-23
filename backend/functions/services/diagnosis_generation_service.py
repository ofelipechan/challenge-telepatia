
from typing import List
from pydantic import BaseModel, Field
from repositories.clinical_record_repository import save_diagnosis_report
from repositories.transcription_repository import set_processing_status
from samples.medical_documents import get_medical_documents
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms, DiagnosisProbability, ReportOutput
from models.transcription import TranscriptionStatus
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class DiagnosisList(BaseModel):
    summary: str = Field(description="A summary about the report.")
    diagnosis_probabilities: List[DiagnosisProbability] = Field(description="List of probable diagnoses")
    conclusion: str = Field(description="A conclusion about the most likely diagnosis of the patient with justification for the selection with clinical reasoning.")

class DiagnosisGenerationService:

    def process(self, clinical_record: ClinicalRecord) -> None:
        """
        Firebase function triggered when a clinical record document is created in Firestore.
        
        This function receives the clinical record data and should generate a diagnosis.
        """
        try:
            assert clinical_record.session_id, "session_id not provided"      
            set_processing_status(clinical_record.session_id, TranscriptionStatus.DIAGNOSIS_STARTED)
            diagnosis_report, parsed_diagnosis = self._generate_diagnosis_report(clinical_record)
            diagnosis_probability: List[DiagnosisProbability] = parsed_diagnosis.diagnosis_probabilities

            diagnosis: ReportOutput = ReportOutput(
                report=diagnosis_report,
                diagnosis_probabilities=diagnosis_probability
            )

            save_diagnosis_report(clinical_record.session_id, diagnosis)
            
            set_processing_status(clinical_record.session_id, TranscriptionStatus.DIAGNOSIS_FINISHED)
        except Exception as e:
            print(f"Error in diagnosis_generation: {str(e)}")
            raise e

    def _generate_diagnosis_report(self, clinical_record: ClinicalRecord) -> tuple[str, DiagnosisList]:
        # Chain 1 - Diagnosis Report
        diagnosis_template = ChatPromptTemplate.from_template("""
            <context>
                You are a doctor with expertise in clinical diagnosis.
                You'll be given a summary of a conversation between a doctor and a patient, information about the patient, reason for the visit and details about the symptoms.
                You need to analyze the patient's symptoms, their severity, and duration.
                Consider the patient's age, demographic factors, behavior, lifestyle, nutrition, hydration, and other factors that might be relevant for the diagnosis.
            </context>

            <input>
                <summary>
                {summary}
                </summary>

                <patient_info>
                {patient_info}
                </patient_info>

                <reason_for_visit>
                {reason_for_visit}
                </reason_for_visit>

                <symptoms_details>
                {symptoms_details}
                </symptoms_details>
            </input>

            <instructions>
                1- Generate a list of probable diagnosis using evidence-based reasoning.
                2- Based on the chances of the patient having the disease, assign probability estimates (0-100%) for each diagnosis.
                3- Explain the disease and the reasoning behind the probable diagnosis. Relate the patient's symptoms to the diagnosis.
                4- Refer to the text within `<knowledge-base></knowledge-base>` for evidence-based reasoning. Use it as guidance, but also, feel free to consider alternative diagnoses not listed in the knowledge base.
            </instructions>
            
            <knowledge-base>
            {knowledge_base}
            </knowledge-base>
            
            <output-instructions>
                Present your response with the following attributes:
                - summary: Explain what the transcription is about. Include patient's name, age, gender, and symptoms and relevant information for the diagnosis.
                - diagnosis_probabilities: Provide the list of probable diagnosis according to the instructions.
                - conclusion: Select the most likely diagnosis of the patient. Justify your selection with clinical reasoning.
            </output-instructions>

            <output>
            {diagnosis_output_parser}
            </output>
            """)

        # Chain 2 - Treatment Plan
        treatment_plan_template = ChatPromptTemplate.from_template(template="""
            <context>
                You are a doctor with expertise in generating treatment plan for patients.
                You'll be given a diagnosis report generated for a patient, having probability estimates (0-100%) based on the chances of the patient having the disease.
                You need to analyze the full report, the patient's symptoms, their severity, and duration.
                Consider the patient's age, demographic factors, behavior, lifestyle, nutrition, hydration, and other factors that might be relevant for the treatment plan.
            </context>
            <instructions>
                # Treatment Plan
                - Develop a **personalized treatment plan** tailored to the patient's condition and symptoms.  
                - Adjust treatment intensity based on **symptom severity**.  
                - Include both **pharmacological** and **non-pharmacological** interventions when applicable.  
                - Provide a clear **explanation and clinical reasoning** behind each element of the treatment plan.  

                # Recommendations
                - Write a **recommendation text** directed to the doctor managing the case.  
                - **Highlight and alert** if any critical or red-flag symptoms are present.  
                - Suggest appropriate **diagnostic tests and procedures** to improve accuracy.  
                - Explain the **clinical reasoning** behind each recommendation.  
                - Include **follow-up actions or monitoring** if relevant.  
            </instructions>
            
            <diagnosis_report>
            {diagnosis_output}
            </diagnosis_report>
            
            <output>
                - Present your response in two distinct sections, each with its own title: "Treatment Plan" and "Recommendation".
            </output>
        """
        )

        report_template = ChatPromptTemplate.from_template(template="""
            <role>
                You are an expert in creating structured and professional **markdown reports** for clinical cases.
            </role>

            <context>
                You will be provided with the following information:
                - A **Diagnosis Report** containing "Summary", "Diagnosis", and "Conclusion".
                - A **Treatment Plan** and **Recommendations** for the patient.
            </context>

            <goal>
                - Generate a clear, well-structured report in **markdown format**.  
                - Use **bullet points** for readability and concise presentation.  
                - Format hierarchy with **"#" for main sections**, **"##" for subsections**, and **"###" for sub-subsections**.  
                - Highlight key details with **bold** and emphasize *medical terms* or important notes with *italics*.  
                - Ensure the report is **intuitive, professional, and easy to navigate** for clinical use.  
            </goal>

            
            <diagnosis_report>
            {diagnosis_output}
            </diagnosis_report>
            
            <treatment_plan>
            {treatment_plan}
            </treatment_plan>
            
            <output>
                Generate a comprehensive report in markdown format combining the diagnosis and treatment information.
            </output>
        """)

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

        knowledge_base = self._retrieve_medical_knowledge(clinical_record)
        symptoms_details = self._format_symptoms_for_prompt(clinical_record.classified_symptoms or [])

        diagnosis_output_parser = PydanticOutputParser(pydantic_object=DiagnosisList)

        # 1 - Generate diagnosis
        diagnosis_chain = diagnosis_template | llm | diagnosis_output_parser
        parsed_diagnosis = diagnosis_chain.invoke({
            "knowledge_base": knowledge_base,
            "summary": clinical_record.summary,
            "patient_info": clinical_record.patient_info.model_dump_json(),
            "reason_for_visit": clinical_record.reason_for_visit or "Not specified",
            "symptoms_details": symptoms_details,
            "diagnosis_output_parser": diagnosis_output_parser.get_format_instructions()
        })
        print('diagnosis generated')
        
        # Convert the parsed diagnosis to a string
        diagnosis_string = parsed_diagnosis.model_dump_json()
        
        print('generating treatment plan and report')
        # Generate treatment plan and final report in a single chain
        treatment_and_report_chain = (
            {"treatment_plan": treatment_plan_template | llm | StrOutputParser()}
            | {"diagnosis_output": RunnablePassthrough(), "treatment_plan": RunnablePassthrough()}
            | report_template | llm | StrOutputParser()
        )
        
        final_report = treatment_and_report_chain.invoke({
            "diagnosis_output": diagnosis_string
        })
        
        return final_report, parsed_diagnosis

    def _retrieve_medical_knowledge(self, clinical_record: ClinicalRecord) -> str:
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
                symptom_names = [s.name.lower() for s in clinical_record.classified_symptoms]
                query_parts.extend(symptom_names)
            
            if clinical_record.reason_for_visit:
                query_parts.append(clinical_record.reason_for_visit.lower())
                
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

    def _format_symptoms_for_prompt(self, symptoms: List[ClassifiedSymptoms]) -> str:
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


