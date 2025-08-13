import { TranscriptionStatusMap, type TranscriptionStatus } from "../services/api";

export function StepIndicator({ status }: { status?: TranscriptionStatus }) {
  const steps = [
    {
      id: 'transcription',
      title: 'Transcription',
      started: TranscriptionStatusMap.TRANSCRIPTION_STARTED,
      finished: TranscriptionStatusMap.TRANSCRIPTION_FINISHED,
      error: TranscriptionStatusMap.TRANSCRIPTION_ERROR,
    },
    {
      id: 'extraction',
      title: 'Information Extraction',
      started: TranscriptionStatusMap.INFORMATION_EXTRACTION_STARTED,
      finished: TranscriptionStatusMap.INFORMATION_EXTRACTION_FINISHED,
      error: TranscriptionStatusMap.INFORMATION_EXTRACTION_ERROR,
    },
    {
      id: 'diagnosis',
      title: 'Diagnosis Generation',
      started: TranscriptionStatusMap.DIAGNOSIS_STARTED,
      finished: TranscriptionStatusMap.DIAGNOSIS_FINISHED,
      error: TranscriptionStatusMap.DIAGNOSIS_ERROR,
    },
  ];

  const getStepStatus = (step: typeof steps[0]) => {
    if (!status) return 'pending';
    if (status === step.error) return 'error';
    if (status === step.finished) return 'completed';
    if (status === step.started) return 'in-progress';
    
    const stepOrder: TranscriptionStatus[] = [
      TranscriptionStatusMap.TRANSCRIPTION_STARTED,
      TranscriptionStatusMap.TRANSCRIPTION_FINISHED,
      TranscriptionStatusMap.INFORMATION_EXTRACTION_STARTED,
      TranscriptionStatusMap.INFORMATION_EXTRACTION_FINISHED,
      TranscriptionStatusMap.DIAGNOSIS_STARTED,
      TranscriptionStatusMap.DIAGNOSIS_FINISHED,
    ];
    
    const currentStepIndex = stepOrder.indexOf(status);
    
    // If status is not in the step order (like error states), return pending
    if (currentStepIndex === -1) return 'pending';
    
    let thisStepIndex: number;
    if (step.id === 'transcription') {
      thisStepIndex = stepOrder.indexOf(TranscriptionStatusMap.TRANSCRIPTION_FINISHED);
    } else if (step.id === 'extraction') {
      thisStepIndex = stepOrder.indexOf(TranscriptionStatusMap.INFORMATION_EXTRACTION_FINISHED);
    } else {
      thisStepIndex = stepOrder.indexOf(TranscriptionStatusMap.DIAGNOSIS_FINISHED);
    }
    
    if (currentStepIndex > thisStepIndex) {
      return 'completed';
    }
    
    return 'pending';
  };

  return (
    <div className="max-w-2xl mx-auto mb-8 mt-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(step);
          const isLast = index === steps.length - 1;
          
          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center w-30">
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg
                  ${stepStatus === 'completed' ? 'bg-green-500' : ''}
                  ${stepStatus === 'error' ? 'bg-red-500' : ''}
                  ${stepStatus === 'in-progress' ? 'bg-blue-500 animate-pulse' : ''}
                  ${stepStatus === 'pending' ? 'bg-gray-300 text-gray-600' : ''}
                `}>
                  {stepStatus === 'completed' && (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  {stepStatus === 'error' && (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                  {stepStatus === 'in-progress' && (
                    <svg className="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  )}
                  {stepStatus === 'pending' && (index + 1)}
                </div>
                <div className="mt-2 text-center">
                  <p className={`text-sm font-medium ${
                    stepStatus === 'completed' ? 'text-green-600' :
                    stepStatus === 'error' ? 'text-red-600' :
                    stepStatus === 'in-progress' ? 'text-blue-600' :
                    'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                  <p className={`text-xs ${
                    stepStatus === 'completed' ? 'text-green-500' :
                    stepStatus === 'error' ? 'text-red-500' :
                    stepStatus === 'in-progress' ? 'text-blue-500' :
                    'text-gray-400'
                  }`}>
                    {stepStatus === 'completed' && 'Completed'}
                    {stepStatus === 'error' && 'Error'}
                    {stepStatus === 'in-progress' && 'In Progress'}
                    {stepStatus === 'pending' && 'Pending'}
                  </p>
                </div>
              </div>
              
              {!isLast && (
                <div className={`
                  w-30 h-1 mx-4
                  ${stepStatus === 'completed' ? 'bg-green-500' : 'bg-gray-300'}
                `} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
