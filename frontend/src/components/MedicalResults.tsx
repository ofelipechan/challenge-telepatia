import React from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { 
  User, 
  AlertTriangle, 
  Stethoscope, 
  Pill, 
  Calendar,
  Activity,
  TrendingUp
} from 'lucide-react';
import { MedicalResult, Symptom } from '../types/medical';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface MedicalResultsProps {
  result: MedicalResult;
}

const getSeverityColor = (severity: Symptom['severity']) => {
  switch (severity) {
    case 'mild':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'moderate':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'severe':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'critical':
      return 'bg-red-100 text-red-800 border-red-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getSeverityValue = (severity: Symptom['severity']) => {
  switch (severity) {
    case 'mild':
      return 1;
    case 'moderate':
      return 2;
    case 'severe':
      return 3;
    case 'critical':
      return 4;
    default:
      return 0;
  }
};

export const MedicalResults: React.FC<MedicalResultsProps> = ({ result }) => {
  if (result.processingStatus !== 'completed') return null;

  const { extraction, diagnosis, treatmentPlan } = result;

  // Prepare chart data for symptoms severity
  const symptomsData = {
    labels: extraction.symptoms.map(s => s.name),
    datasets: [
      {
        label: 'Symptom Severity',
        data: extraction.symptoms.map(s => getSeverityValue(s.severity)),
        backgroundColor: extraction.symptoms.map(s => {
          switch (s.severity) {
            case 'mild': return 'rgba(34, 197, 94, 0.6)';
            case 'moderate': return 'rgba(234, 179, 8, 0.6)';
            case 'severe': return 'rgba(249, 115, 22, 0.6)';
            case 'critical': return 'rgba(239, 68, 68, 0.6)';
            default: return 'rgba(156, 163, 175, 0.6)';
          }
        }),
        borderColor: extraction.symptoms.map(s => {
          switch (s.severity) {
            case 'mild': return 'rgb(34, 197, 94)';
            case 'moderate': return 'rgb(234, 179, 8)';
            case 'severe': return 'rgb(249, 115, 22)';
            case 'critical': return 'rgb(239, 68, 68)';
            default: return 'rgb(156, 163, 175)';
          }
        }),
        borderWidth: 1,
      },
    ],
  };

  // Prepare chart data for diagnosis probabilities
  const diagnosisData = {
    labels: diagnosis.differentialDiagnoses.map(d => d.condition),
    datasets: [
      {
        data: diagnosis.differentialDiagnoses.map(d => d.probability),
        backgroundColor: [
          'rgba(59, 130, 246, 0.6)',
          'rgba(16, 185, 129, 0.6)',
          'rgba(245, 158, 11, 0.6)',
          'rgba(239, 68, 68, 0.6)',
          'rgba(139, 92, 246, 0.6)',
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
          'rgb(139, 92, 246)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 4,
        ticks: {
          stepSize: 1,
          callback: function(value: number) {
            switch (value) {
              case 1: return 'Mild';
              case 2: return 'Moderate';
              case 3: return 'Severe';
              case 4: return 'Critical';
              default: return '';
            }
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Patient Information */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-4">
          <User className="text-blue-500" size={24} />
          <h3 className="text-xl font-semibold text-gray-800">Patient Information</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {extraction.patientInfo.name && (
            <div>
              <label className="text-sm font-medium text-gray-500">Name</label>
              <p className="text-gray-900">{extraction.patientInfo.name}</p>
            </div>
          )}
          {extraction.patientInfo.age && (
            <div>
              <label className="text-sm font-medium text-gray-500">Age</label>
              <p className="text-gray-900">{extraction.patientInfo.age} years</p>
            </div>
          )}
          {extraction.patientInfo.gender && (
            <div>
              <label className="text-sm font-medium text-gray-500">Gender</label>
              <p className="text-gray-900 capitalize">{extraction.patientInfo.gender}</p>
            </div>
          )}
          {extraction.patientInfo.idNumber && (
            <div>
              <label className="text-sm font-medium text-gray-500">ID Number</label>
              <p className="text-gray-900">{extraction.patientInfo.idNumber}</p>
            </div>
          )}
        </div>
        <div className="mt-4">
          <label className="text-sm font-medium text-gray-500">Reason for Visit</label>
          <p className="text-gray-900 mt-1">{extraction.reasonForVisit}</p>
        </div>
      </div>

      {/* Symptoms */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="text-orange-500" size={24} />
          <h3 className="text-xl font-semibold text-gray-800">Symptoms</h3>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <div className="space-y-3">
              {extraction.symptoms.map((symptom, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${getSeverityColor(symptom.severity)}`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium">{symptom.name}</h4>
                      {symptom.description && (
                        <p className="text-sm mt-1 opacity-80">{symptom.description}</p>
                      )}
                      {symptom.duration && (
                        <p className="text-sm mt-1 opacity-80">Duration: {symptom.duration}</p>
                      )}
                    </div>
                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-white bg-opacity-50">
                      {symptom.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-lg font-medium text-gray-800 mb-4">Symptom Severity Chart</h4>
            <Bar data={symptomsData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Diagnosis */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Stethoscope className="text-purple-500" size={24} />
          <h3 className="text-xl font-semibold text-gray-800">Diagnosis</h3>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <div className="mb-4">
              <h4 className="text-lg font-medium text-gray-800 mb-2">Primary Diagnosis</h4>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-900 font-medium">{diagnosis.primaryDiagnosis}</p>
                <p className="text-blue-700 text-sm mt-1">
                  Confidence: {Math.round(diagnosis.confidence * 100)}%
                </p>
              </div>
            </div>
            <div>
              <h4 className="text-lg font-medium text-gray-800 mb-2">Differential Diagnoses</h4>
              <div className="space-y-2">
                {diagnosis.differentialDiagnoses.map((diff, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-800">{diff.condition}</span>
                    <span className="text-sm font-medium text-gray-600">
                      {Math.round(diff.probability * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div>
            <h4 className="text-lg font-medium text-gray-800 mb-4">Diagnosis Probability Distribution</h4>
            <Doughnut data={diagnosisData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Treatment Plan */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Pill className="text-green-500" size={24} />
          <h3 className="text-xl font-semibold text-gray-800">Treatment Plan</h3>
        </div>
        
        {/* Medications */}
        {treatmentPlan.medications.length > 0 && (
          <div className="mb-6">
            <h4 className="text-lg font-medium text-gray-800 mb-3">Medications</h4>
            <div className="space-y-3">
              {treatmentPlan.medications.map((medication, index) => (
                <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h5 className="font-medium text-green-900">{medication.name}</h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2 text-sm">
                        <span className="text-green-700">
                          <strong>Dosage:</strong> {medication.dosage}
                        </span>
                        <span className="text-green-700">
                          <strong>Frequency:</strong> {medication.frequency}
                        </span>
                        <span className="text-green-700">
                          <strong>Duration:</strong> {medication.duration}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-3">Recommendations</h4>
          <div className="space-y-2">
            {treatmentPlan.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Follow-up */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-800 mb-2">Follow-up</h4>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-900">{treatmentPlan.followUp}</p>
          </div>
        </div>

        {/* Alerts */}
        {treatmentPlan.alerts.length > 0 && (
          <div>
            <h4 className="text-lg font-medium text-gray-800 mb-3">Important Alerts</h4>
            <div className="space-y-2">
              {treatmentPlan.alerts.map((alert, index) => (
                <div key={index} className="flex items-start space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <AlertTriangle className="text-red-500 mt-0.5" size={16} />
                  <p className="text-red-800">{alert}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
