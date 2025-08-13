import axios from 'axios';
import { ProcessingRequest, MedicalResult } from '../types/medical';

// Configure base URL for Firebase Functions using environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001/telepatia-challenge/us-central1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const medicalApi = {
  // Submit audio file or text input to transcription handler
  submitTranscription: async (data: { audioUrl?: string; transcriptionText?: string }): Promise<{ requestId: string }> => {
    // Map camelCase to snake_case for API compatibility
    const requestBody = data.audioUrl 
      ? { audio_url: data.audioUrl }
      : { transcription_text: data.transcriptionText };
    
    const response = await api.post('/transcription_handler', requestBody);
    return response.data;
  },

  // Get processing status and results
  getProcessingStatus: async (requestId: string): Promise<MedicalResult> => {
    const response = await api.get(`/processing-status/${requestId}`);
    return response.data;
  },

  // Poll for updates (for real-time updates)
  pollProcessingStatus: async (requestId: string): Promise<MedicalResult> => {
    const response = await api.get(`/processing-status/${requestId}?poll=true`);
    return response.data;
  },

  // Legacy method for backward compatibility
  startProcessing: async (request: ProcessingRequest): Promise<{ requestId: string }> => {
    const data = request.audioUrl 
      ? { audioUrl: request.audioUrl }
      : { transcriptionText: request.textInput };
    
    return medicalApi.submitTranscription(data);
  },
};

export default api;
