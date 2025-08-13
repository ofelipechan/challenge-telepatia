import { medicalApi } from "../services/api";

type DiagnosisProps = {
    sessionId?: string;
}

export function Diagnosis({ sessionId }: DiagnosisProps) {
  const checkStatus = async () => {
    if (!sessionId) {
      return;
    }
    const response = await medicalApi.getTranscription(sessionId);
    console.log(response);
  };

  return (
    <div className="text-center">
      <h2 className="text-lg font-bold text-gray-800 mb-4">
        The report is being generated.
      </h2>
      <p className="text-sm text-gray-500 mb-4">Session ID: {sessionId}</p>
      <button className="bg-blue-500 text-white px-4 py-2 rounded-md cursor-pointer" onClick={() => checkStatus()}>
        Check status
      </button>
    </div>
  );
}
