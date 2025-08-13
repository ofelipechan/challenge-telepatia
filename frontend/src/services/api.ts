import axios from 'axios';

// Configure base URL for Firebase Functions using environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001/telepatia-challenge/us-central1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const TranscriptionStatusMap = {
  TRANSCRIPTION_STARTED: "transcription_started",
  TRANSCRIPTION_FINISHED: "transcription_finished",
  TRANSCRIPTION_ERROR: "transcription_error",
  DIAGNOSIS_STARTED: "diagnosis_started",
  DIAGNOSIS_FINISHED: "diagnosis_finished",
  DIAGNOSIS_ERROR: "diagnosis_error",
  INFORMATION_EXTRACTION_STARTED: "information_extraction_started",
  INFORMATION_EXTRACTION_FINISHED: "information_extraction_finished",
  INFORMATION_EXTRACTION_ERROR: "information_extraction_error",
} as const;

export type TranscriptionStatus = typeof TranscriptionStatusMap[keyof typeof TranscriptionStatusMap];

export type Transcription = {
  session_id: string;
  audio_url: string;
  error_message: string;
  status: TranscriptionStatus;
  text: string;
  created_at: string;
  updated_at: string;
}

export type PatientInfo = {
  name?: string;
  age?: number;
  id_number?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
}

export type Symptom = {
  name: string;
  duration?: string;
  intensity?: string;
}

export type DiagnosisProbability = {
  name: string;
  probability?: number;
  reasoning?: string;
  symptoms?: string[];
}

export type ClassifiedSymptoms = {
  name: string;
  intensity?: string;
  severity?: string;
  duration?: string;
  confidence_score: number;
}

export type ClinicalRecord = {
  summary?: string;
  patient_info?: PatientInfo;
  symptoms?: Symptom[];
  reason_for_visit?: string;
  confidence_score: number;
  session_id: string;
  classified_symptoms?: ClassifiedSymptoms[];
  diagnosis_report?: string;
  diagnosis?: DiagnosisProbability[];
  created_at?: string;
  updated_at?: string;
}

export const medicalApi = {
  submitTranscription: async (data: { audioUrl?: string; transcriptionText?: string }): Promise<{ session_id: string }> => {
    const requestBody = data.audioUrl 
      ? { audio_url: data.audioUrl }
      : { transcription_text: data.transcriptionText };
    
    const response = await api.post('/transcription_handler', requestBody);
    return response.data;
  },

  getTranscription: async (session_id: string): Promise<Transcription> => {
    const response = await api.get(`/get_transcription?session_id=${session_id}`);
    return response.data.data;
  },
  
  getClinicalRecord: async (session_id: string): Promise<ClinicalRecord> => {
    const response = await api.get(`/get_clinical_record?session_id=${session_id}`);
    return response.data.data;
  },
};

export default api;
