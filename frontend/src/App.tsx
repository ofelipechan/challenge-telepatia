import { useState, useCallback } from "react";
import { InputForm } from "./components/InputForm";
import { medicalApi } from "./services/api";
import { toast, Toaster } from "react-hot-toast";
import "./App.css";
import { Diagnosis } from "./components/Diagnosis";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [submitted, setSubmitted] = useState(false);

  // Handle form submission
  const handleSubmit = useCallback(
    async (data: { audioUrl?: string; textInput?: string }) => {
      try {
        setIsLoading(true);

        // Submit to transcription handler
        const response = await medicalApi.submitTranscription({
          audioUrl: data.audioUrl,
          transcriptionText: data.textInput,
        });

        console.log("session_id is: ", response.session_id);
        setSubmitted(true);
        setSessionId(response.session_id);
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

      {/* Main Content */}
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

          {!submitted ? (
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
          ) : (
            <Diagnosis sessionId={sessionId} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
