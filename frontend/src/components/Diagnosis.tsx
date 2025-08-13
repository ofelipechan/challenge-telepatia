import { useState } from "react";
import { medicalApi, TranscriptionStatusMap, type ClinicalRecord, type TranscriptionStatus } from "../services/api";
import MarkdownPreview from '@uiw/react-markdown-preview';

type DiagnosisProps = {
    sessionId?: string;
}

const TranscriptionStatusText = {
  [TranscriptionStatusMap.TRANSCRIPTION_FINISHED]: "Transcription finished",
  [TranscriptionStatusMap.TRANSCRIPTION_ERROR]: "Transcription error",
  [TranscriptionStatusMap.DIAGNOSIS_STARTED]: "Diagnosis started",
  [TranscriptionStatusMap.DIAGNOSIS_FINISHED]: "Diagnosis finished",
  [TranscriptionStatusMap.DIAGNOSIS_ERROR]: "Diagnosis error",
  [TranscriptionStatusMap.INFORMATION_EXTRACTION_STARTED]: "Information extraction started",
  [TranscriptionStatusMap.INFORMATION_EXTRACTION_FINISHED]: "Information extraction finished",
  [TranscriptionStatusMap.INFORMATION_EXTRACTION_ERROR]: "Information extraction error",
}

export function Diagnosis({ sessionId }: DiagnosisProps) {
  const [status, setStatus] = useState<TranscriptionStatus | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [clinicalRecord, setClinicalRecord] = useState<ClinicalRecord | undefined>(undefined);
  
  const checkStatus = async () => {
    setLoading(true);
    if (!sessionId) {
      return;
    }
    const response = await medicalApi.getTranscription(sessionId);
    console.log(response);
    
    setStatus(response.status);
    if (response.status === TranscriptionStatusMap.DIAGNOSIS_FINISHED) {
      await getClinicalRecord();
    }
    setLoading(false);
  };

  const getClinicalRecord = async () => {
    if (!sessionId) {
      return;
    }
    const response = await medicalApi.getClinicalRecord(sessionId);
    console.log(response);
    setClinicalRecord(response);
  }

  const test = `
# Clinical Case Report

## Diagnosis

### Probable Diagnoses
1. **Acute Gastroenteritis** - Probability: 80%
   - **Explanation**: The patient presents with primary symptoms of diarrhea, nausea, vomiting, and abdominal cramps, which are characteristic of acute gastroenteritis. The fever and mild dizziness upon standing also support this diagnosis. The recent consumption of takeout chicken and rice raises the suspicion of foodborne illness, which can lead to gastroenteritis.
   
2. **Foodborne Illness** - Probability: 70%
   - **Explanation**: Given the patient's recent meal from a takeout restaurant, foodborne illness is a strong consideration. Symptoms align with foodborne pathogens, particularly if the chicken was undercooked or contaminated. The absence of blood in vomit or stool makes severe bacterial infections less likely but does not rule out milder forms.

3. **Upper Respiratory Tract Infection** - Probability: 20%
   - **Explanation**: While the patient has a fever and mild dizziness, the primary gastrointestinal symptoms are more pronounced. Upper respiratory infections typically present with respiratory symptoms, which are absent in this case.

### Most Likely Diagnosis
- **Acute Gastroenteritis** is the most likely diagnosis for Michael Davis. The combination of gastrointestinal symptoms (nausea, vomiting, diarrhea, abdominal cramps) and fever, along with the recent meal history, strongly indicates this condition. The mild dizziness may be attributed to dehydration from diarrhea and vomiting.
  `


  return (
    <div className="text-center">
      <h2 className="text-lg font-bold text-gray-800 mb-4">
        The report is being generated.
      </h2>
      <p className="text-sm text-gray-500 mb-4">Session ID: {sessionId}</p>

      {!clinicalRecord && (
        <button className="bg-blue-500 text-white px-4 py-2 rounded-md cursor-pointer mb-10" onClick={() => checkStatus()}>
          Check status
        </button>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : status && status !== TranscriptionStatusMap.DIAGNOSIS_FINISHED && (
        <p className="text-sm text-gray-500 mb-4">Status: {TranscriptionStatusText[status as keyof typeof TranscriptionStatusText] || status}</p>
      )}

      {clinicalRecord && (
        <div>
          <MarkdownPreview source={clinicalRecord.diagnosis_report} style={{ padding: 16 }} wrapperElement={{ "data-color-mode": "light" }} />
        </div>
      )}
    </div>
  );
}
