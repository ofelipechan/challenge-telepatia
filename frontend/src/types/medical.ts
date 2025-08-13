export interface Symptom {
  name: string;
  severity: 'mild' | 'moderate' | 'severe' | 'critical';
  description?: string;
  duration?: string;
}

export interface PatientInfo {
  name?: string;
  age?: number;
  idNumber?: string;
  gender?: 'male' | 'female' | 'other';
}

export interface MedicalExtraction {
  symptoms: Symptom[];
  patientInfo: PatientInfo;
  reasonForVisit: string;
  timestamp: string;
}

export interface Diagnosis {
  primaryDiagnosis: string;
  differentialDiagnoses: Array<{
    condition: string;
    probability: number;
  }>;
  confidence: number;
}

export interface TreatmentPlan {
  medications: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration: string;
  }>;
  recommendations: string[];
  followUp: string;
  alerts: string[];
}

export interface MedicalResult {
  transcription?: string;
  extraction: MedicalExtraction;
  diagnosis: Diagnosis;
  treatmentPlan: TreatmentPlan;
  processingStatus: 'pending' | 'transcribing' | 'extracting' | 'diagnosing' | 'completed' | 'error';
  error?: string;
}

export interface ProcessingRequest {
  audioUrl?: string;
  textInput?: string;
  requestId: string;
}
