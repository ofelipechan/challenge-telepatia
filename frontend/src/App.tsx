import { useState, useCallback } from 'react';
import { Heart, Brain } from 'lucide-react';
import { InputForm } from './components/InputForm';
import { ProcessingStatus } from './components/ProcessingStatus';
import { MedicalResults } from './components/MedicalResults';
import { medicalApi } from './services/api';
import type { MedicalResult, ProcessingRequest } from './types/medical';
import './App.css';
import { toast, Toaster } from 'react-hot-toast';
import Header from './components/Header';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [medicalResult, setMedicalResult] = useState<MedicalResult | null>(null);

  // Handle form submission
  const handleSubmit = useCallback(async (data: { audioUrl?: string; textInput?: string }) => {
    try {
      setIsLoading(true);
      setMedicalResult(null);
      
      // Submit to transcription handler
      const response = await medicalApi.submitTranscription({
        audioUrl: data.audioUrl,
        transcriptionText: data.textInput,
      });

      console.log('session_id is: ', response)
      
      toast.success('Processing started!');
      
    } catch (error) {
      console.error('Error starting processing:', error);
      toast.error('Failed to start processing. Please try again.');
      setMedicalResult({
        processingStatus: 'error',
        error: 'Failed to start processing',
        extraction: {
          symptoms: [],
          patientInfo: {},
          reasonForVisit: '',
          timestamp: new Date().toISOString(),
        },
        diagnosis: {
          primaryDiagnosis: '',
          differentialDiagnoses: [],
          confidence: 0,
        },
        treatmentPlan: {
          medications: [],
          recommendations: [],
          followUp: '',
          alerts: [],
        },
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-5 md:px-0 md:max-w-2xl">
        <div className="space-y-6">
          {/* Input Form */}
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />

          {/* Processing Status */}
          {medicalResult && (
            <ProcessingStatus result={medicalResult} isPolling={false} />
          )}

          {/* Medical Results */}
          {medicalResult && medicalResult.processingStatus === 'completed' && (
            <MedicalResults result={medicalResult} />
          )}
        </div>
      </main>

      
    </div>
  );
}

export default App;
