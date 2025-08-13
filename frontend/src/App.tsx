import { useState, useCallback } from "react";
import { InputForm } from "./components/InputForm";
import { medicalApi, TranscriptionStatusMap, type ClinicalRecord, type TranscriptionStatus } from "./services/api";
import { toast, Toaster } from "react-hot-toast";
import "./App.css";
import { Diagnosis } from "./components/Diagnosis";
import { StepIndicator } from "./components/StepIndicator";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [submitted, setSubmitted] = useState(false);
  const [status, setStatus] = useState<TranscriptionStatus | undefined>(undefined);
  const [clinicalRecord, setClinicalRecord] = useState<ClinicalRecord | undefined>(undefined);

  const handleSubmit = useCallback(
    async (data: { audioUrl?: string; textInput?: string }) => {
      try {
        setIsLoading(true);
        setStatus(TranscriptionStatusMap.TRANSCRIPTION_STARTED);

        const response = await medicalApi.submitTranscription({
          audioUrl: data.audioUrl,
          transcriptionText: data.textInput,
        });

        console.log("session_id is: ", response.session_id);
        setSubmitted(true);
        setSessionId(response.session_id);
        setStatus(TranscriptionStatusMap.TRANSCRIPTION_FINISHED);
        toast.success("Processing started!");
      } catch (error) {
        console.error("Error starting processing:", error);
        toast.error("Failed to start processing. Please try again.");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const checkStatus = async () => {
    setIsLoading(true);
    if (!sessionId) {
      return;
    }
    const response = await medicalApi.getTranscription(sessionId);
    console.log(response);
    
    setStatus(response.status);
    if (response.status === TranscriptionStatusMap.DIAGNOSIS_FINISHED) {
      await getClinicalRecord();
    }
    setIsLoading(false);
  };

  
  const getClinicalRecord = async () => {
    if (!sessionId) {
      return;
    }
    const response = await medicalApi.getClinicalRecord(sessionId);
    console.log(response);
    setClinicalRecord(response);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#363636",
            color: "#fff",
          },
        }}
      />

      <main className="max-w-7xl mx-auto py-8 px-5 md:px-0 md:max-w-2xl">
        <div className="space-y-6">
          <div className="p-6 mb-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-4 text-center">
              Medical Information Processing
            </h1>
            <p className="text-sm text-gray-500 mb-4 text-center">
              This is an AI-powered medical assistant designed to write clinical
              report.
            </p>
          </div>

          {!submitted && (
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
          )}
          <StepIndicator status={status} />
          {submitted && (
            <Diagnosis sessionId={sessionId} clinicalRecord={clinicalRecord} isLoading={isLoading} checkStatus={checkStatus} />
          )}

        </div>
      </main>
    </div>
  );
}

export default App;
