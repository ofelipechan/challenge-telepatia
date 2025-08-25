
from typing import List
from pydantic import BaseModel, Field
from repositories.medical_knowledge_base_repository import MedicalKnowledgeRepository
from repositories.clinical_record_repository import save_diagnosis_report
from repositories.transcription_repository import set_processing_status
from models.clinical_record import ClinicalRecord, ClassifiedSymptoms, DiagnosisProbability, ReportOutput
from models.transcription import TranscriptionStatus
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.callbacks import get_openai_callback
from langchain import hub

class DiagnosisList(BaseModel):
    summary: str = Field(description="A summary about the report.")
    diagnosis_probabilities: List[DiagnosisProbability] = Field(description="List of probable diagnoses")
    conclusion: str = Field(description="A conclusion about the most likely diagnosis of the patient with justification for the selection with clinical reasoning.")

class DiagnosisGenerationService:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

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
                - Include both **pharmacological** and **non-pharmacological** interventions (when applicable).
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

        knowledge_base = self._retrieve_medical_knowledge(clinical_record)
        symptoms_details = self._format_symptoms_for_prompt(clinical_record.classified_symptoms or [])
        
        total_tokens = 0

        with get_openai_callback() as cb:
            diagnosis_output_parser = PydanticOutputParser(pydantic_object=DiagnosisList)
            diagnosis_chain = diagnosis_template | self.llm | diagnosis_output_parser
            parsed_diagnosis = diagnosis_chain.invoke({
                "knowledge_base": knowledge_base,
                "summary": clinical_record.summary,
                "patient_info": clinical_record.patient_info.model_dump_json(),
                "reason_for_visit": clinical_record.reason_for_visit or "Not specified",
                "symptoms_details": symptoms_details,
                "diagnosis_output_parser": diagnosis_output_parser.get_format_instructions()
            })
            print('diagnosis generated')
            total_tokens += cb.total_tokens
        
        # Convert the parsed diagnosis to a string
        diagnosis_string = parsed_diagnosis.model_dump_json()
        
        print('generating treatment plan and report')
        # Generate treatment plan and final report in a single chain
        with get_openai_callback() as cb:
            treatment_and_report_chain = (
                {"treatment_plan": treatment_plan_template | self.llm | StrOutputParser()}
                | {"diagnosis_output": RunnablePassthrough(), "treatment_plan": RunnablePassthrough()}
                | report_template | self.llm | StrOutputParser()
            )
            
            final_report = treatment_and_report_chain.invoke({
                "diagnosis_output": diagnosis_string
            })
            total_tokens += cb.total_tokens
        
        print(f"Total tokens used for generating diagnosis: {total_tokens}")
        return final_report, parsed_diagnosis

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _retrieve_medical_knowledge(self, clinical_record: ClinicalRecord) -> str:
        query_parts = []
        if clinical_record.reason_for_visit:
            query_parts.append(clinical_record.reason_for_visit.lower())
        if clinical_record.classified_symptoms:
            symptom_names = [s.name.lower() for s in clinical_record.classified_symptoms]
            query_parts.extend(symptom_names)
        if len(query_parts) == 0:
            return ""

        query = " ".join(query_parts)

        medical_knowledge = MedicalKnowledgeRepository()
        print(f"the query is: {query}")
        relevant_docs = medical_knowledge.similarity_search(query)
        print(f"found {len(relevant_docs)} relevant documents")
        # relevant_docs = medical_knowledge.retrieve_full_docs(query)
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"- {doc.page_content}")
        
        return "\n".join(context_parts) if context_parts else ""
        

        # print('loading RAG for medical knowledge')
        # vectorstore = MedicalKnowledgeRepository().vectorstore
        # prompt = hub.pull("rlm/rag-prompt")

        # qa_chain = (
        #     {
        #         "context": vectorstore.as_retriever() | self._format_docs,
        #         "question": RunnablePassthrough()
        #     }
        #     | prompt
        #     | self.llm
        #     | StrOutputParser()
        # )

        # response = qa_chain.invoke(query)
        # print(f'got response from qa_chain: {response}')

        # return response

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


