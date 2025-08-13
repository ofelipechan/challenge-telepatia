import React from 'react';
import { Activity, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { MedicalResult } from '../types/medical';

interface ProcessingStatusProps {
  result: MedicalResult | null;
  isPolling: boolean;
}

const getStatusIcon = (status: MedicalResult['processingStatus']) => {
  switch (status) {
    case 'pending':
      return <Clock className="text-gray-500" size={24} />;
    case 'transcribing':
    case 'extracting':
    case 'diagnosing':
      return <Activity className="text-blue-500 animate-pulse" size={24} />;
    case 'completed':
      return <CheckCircle className="text-green-500" size={24} />;
    case 'error':
      return <AlertCircle className="text-red-500" size={24} />;
    default:
      return <Clock className="text-gray-500" size={24} />;
  }
};

const getStatusText = (status: MedicalResult['processingStatus']) => {
  switch (status) {
    case 'pending':
      return 'Request submitted, waiting to start...';
    case 'transcribing':
      return 'Transcribing audio file...';
    case 'extracting':
      return 'Extracting medical information...';
    case 'diagnosing':
      return 'Generating diagnosis and treatment plan...';
    case 'completed':
      return 'Processing completed successfully!';
    case 'error':
      return 'An error occurred during processing';
    default:
      return 'Unknown status';
  }
};

const getProgressPercentage = (status: MedicalResult['processingStatus']) => {
  switch (status) {
    case 'pending':
      return 0;
    case 'transcribing':
      return 25;
    case 'extracting':
      return 50;
    case 'diagnosing':
      return 75;
    case 'completed':
      return 100;
    case 'error':
      return 0;
    default:
      return 0;
  }
};

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ result, isPolling }) => {
  if (!result) return null;

  getProgressPercentage('pending');

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center space-x-3 mb-4">
        {getStatusIcon(result.processingStatus)}
        <div>
          <h3 className="text-lg font-semibold text-gray-800">
            Processing Status
          </h3>
          <p className="text-sm text-gray-600">
            {getStatusText(result.processingStatus)}
          </p>
        </div>
        {isPolling && (
          <div className="ml-auto">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {result.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="text-red-500" size={20} />
            <h4 className="text-red-800 font-medium">Processing Error</h4>
          </div>
          <p className="text-red-700 mt-2">{result.error}</p>
        </div>
      )}

      {/* Transcription Display */}
      {result.transcription && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Transcription</h4>
          <div className="bg-gray-50 rounded-md p-3">
            <p className="text-gray-800 text-sm">{result.transcription}</p>
          </div>
        </div>
      )}

      {/* Processing Steps */}
      <div className="space-y-2">
        <div className={`flex items-center space-x-2 text-sm ${
          result.processingStatus === 'completed' || result.processingStatus === 'error' ? 'text-green-600' : 'text-gray-400'
        }`}>
          <CheckCircle size={16} />
          <span>Request submitted</span>
        </div>
        
        {result.transcription && (
          <div className="flex items-center space-x-2 text-sm text-green-600">
            <CheckCircle size={16} />
            <span>Audio transcribed</span>
          </div>
        )}
        
        {result.extraction && result.processingStatus !== 'pending' && (
          <div className="flex items-center space-x-2 text-sm text-green-600">
            <CheckCircle size={16} />
            <span>Medical information extracted</span>
          </div>
        )}
        
        {result.diagnosis && result.processingStatus === 'completed' && (
          <div className="flex items-center space-x-2 text-sm text-green-600">
            <CheckCircle size={16} />
            <span>Diagnosis generated</span>
          </div>
        )}
      </div>
    </div>
  );
};
