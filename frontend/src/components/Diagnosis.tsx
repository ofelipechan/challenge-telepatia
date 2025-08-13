import MarkdownPreview from '@uiw/react-markdown-preview';
import type { ClinicalRecord } from '../services/api';

type DiagnosisProps = {
    sessionId?: string;
    clinicalRecord?: ClinicalRecord;
    isLoading?: boolean;
    checkStatus?: () => void;
}

export function Diagnosis({ sessionId, clinicalRecord, isLoading, checkStatus }: DiagnosisProps) {

  return (
    <div className="text-center">
      {!clinicalRecord && (<h2 className="text-lg font-bold text-gray-800 mb-4">
        The report is being generated.
      </h2>)}
      <p className="text-sm text-gray-500 mb-4">Session ID: {sessionId}</p>

      {!clinicalRecord && (
        <button className="bg-blue-500 text-white px-4 py-2 rounded-md cursor-pointer mb-10" onClick={checkStatus}>
          Check status
        </button>
      )}

      {isLoading && (
        <div className="flex items-center justify-center mb-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">Checking status...</span>
        </div>
      )}

      {clinicalRecord && (
        <div>
          <MarkdownPreview source={clinicalRecord.diagnosis_report} style={{ padding: 16 }} wrapperElement={{ "data-color-mode": "light" }} />
        </div>
      )}
    </div>
  );
}
