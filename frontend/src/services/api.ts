import axios from 'axios';

// Configure base URL for Firebase Functions using environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001/telepatia-challenge/us-central1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export type Transcription = {
  session_id: string;
  audio_url: string;
  error_message: string;
  status: string;
  text: string;
  created_at: string;
  updated_at: string;
}

export const medicalApi = {
  // Submit audio file or text input to transcription handler
  submitTranscription: async (data: { audioUrl?: string; transcriptionText?: string }): Promise<{ session_id: string }> => {
    // Map camelCase to snake_case for API compatibility
    const requestBody = data.audioUrl 
      ? { audio_url: data.audioUrl }
      : { transcription_text: data.transcriptionText };
    
    const response = await api.post('/transcription_handler', requestBody);
    return response.data;
  },

  getTranscription: async (requestId: string): Promise<Transcription> => {
    const response = await api.get(`/get_transcription/${requestId}`);
    return response.data;
  },
};

export default api;
