def get_examples():
    return [
        {
            "input": "Patient John Smith, age 45, ID: MS123456, came in complaining of severe chest pain for the past 2 hours and shortness of breath.",
            "output": {
                "patient_info": {
                    "name": "John Smith",
                    "age": 45,
                    "id_number": "MS123456",
                    "validation_status": "valid"
                },
                "symptoms": [
                    {
                        "name": "chest pain",
                        "severity": "severe",
                        "duration": "2 hours",
                        "severity_confidence": 0.95
                    },
                    {
                        "name": "shortness of breath",
                        "severity": "moderate",
                        "duration": "2 hours",
                        "severity_confidence": 0.85
                    }
                ],
                "reason_for_visit": "Acute onset of severe chest pain with associated shortness of breath requiring immediate cardiac evaluation",
            }
        },
        {
            "input": "Maria Garcia, 67 years old, patient ID 87654321, experiencing mild headache for 3 days and occasional dizziness.",
            "output": {
                "patient_info": {
                    "name": "Maria Garcia",
                    "age": 67,
                    "id_number": "87654321",
                    "validation_status": "valid"
                },
                "symptoms": [
                    {
                        "name": "headache",
                        "severity": "mild",
                        "duration": "3 days",
                        "severity_confidence": 0.90
                    },
                    {
                        "name": "dizziness",
                        "severity": "mild",
                        "duration": "intermittent",
                        "severity_confidence": 0.80
                    }
                ],
                "reason_for_visit": "Evaluation of persistent mild headache with associated dizziness in elderly patient",
            }
        }
    ]