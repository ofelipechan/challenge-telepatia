from typing import List
from langchain.schema import Document


def get_medical_documents() -> List[Document]:
    """
    Get the medical documents from the medical knowledge base.
    """
    return [
        Document(
            page_content="DIAGNOSIS: Acute Coronary Syndrome (ACS). PRIMARY SYMPTOMS: Chest pain or pressure, shortness of breath, pain radiating to arm/jaw/back. SECONDARY SYMPTOMS: Nausea, vomiting, cold sweats, dizziness, fatigue, anxiety. CAUSES: Atherosclerosis (plaque buildup in arteries), smoking, high blood pressure, high cholesterol, diabetes, obesity, sedentary lifestyle, family history, stress, age over 45 for men/55 for women. DIAGNOSTIC TESTS: ECG/EKG, cardiac enzymes (troponin), chest X-ray, coronary angiography, stress test, echocardiogram. TREATMENT PLAN: Immediate aspirin, oxygen therapy, nitroglycerin, beta-blockers, statins, antiplatelet agents, emergency cardiac catheterization or thrombolytic therapy if STEMI confirmed.",
            metadata={"topic": "cardiac_emergency", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Myocardial Infarction (Heart Attack). PRIMARY SYMPTOMS: Severe chest pain, pressure or squeezing sensation, pain radiating to left arm/jaw/back. SECONDARY SYMPTOMS: Nausea, vomiting, cold sweats, dizziness, fatigue, anxiety, shortness of breath. CAUSES: Complete blockage of coronary artery by blood clot, atherosclerosis, coronary artery spasm, cocaine use, severe emotional stress, extreme physical exertion, underlying heart disease, smoking, hypertension, diabetes. DIAGNOSTIC TESTS: ECG/EKG, cardiac enzymes (troponin), chest X-ray, coronary angiography, echocardiogram. TREATMENT PLAN: Immediate aspirin, oxygen therapy, nitroglycerin, beta-blockers, statins, antiplatelet agents, emergency cardiac catheterization or thrombolytic therapy.",
            metadata={"topic": "cardiac_emergency", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Tension Headache. PRIMARY SYMPTOMS: Dull, aching head pain, pressure sensation around forehead or back of head. SECONDARY SYMPTOMS: Neck stiffness, shoulder tension, sensitivity to light, fatigue, difficulty concentrating. CAUSES: Muscle tension in neck and scalp, stress, anxiety, depression, poor posture, eye strain, lack of sleep, dehydration, skipping meals, caffeine withdrawal, jaw clenching, overuse of pain medications. DIAGNOSTIC TESTS: Physical examination, blood pressure measurement, neurological examination, CT scan or MRI if red flags present. TREATMENT PLAN: Over-the-counter pain relievers (acetaminophen, ibuprofen), stress management, relaxation techniques, physical therapy, preventive medications if chronic.",
            metadata={"topic": "headache", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Migraine. PRIMARY SYMPTOMS: Severe throbbing headache, usually on one side of head, sensitivity to light and sound. SECONDARY SYMPTOMS: Nausea, vomiting, visual disturbances (aura), dizziness, fatigue. CAUSES: Genetic predisposition, hormonal changes (menstruation, pregnancy), certain foods (aged cheese, chocolate, caffeine), alcohol, stress, lack of sleep, bright lights, loud noises, strong smells, weather changes, medications, dehydration, skipping meals. DIAGNOSTIC TESTS: Physical examination, neurological examination, CT scan or MRI to rule out other causes, headache diary. TREATMENT PLAN: Triptans, NSAIDs, antiemetics, preventive medications (beta-blockers, anticonvulsants), lifestyle modifications, avoiding triggers.",
            metadata={"topic": "headache", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Upper Respiratory Tract Infection. PRIMARY SYMPTOMS: Sore throat, nasal congestion, runny nose, cough. SECONDARY SYMPTOMS: Low-grade fever, fatigue, body aches, headache, loss of appetite. CAUSES: Viral infections (rhinovirus, coronavirus, adenovirus, influenza), bacterial infections (group A streptococcus), close contact with infected individuals, poor hand hygiene, weakened immune system, smoking, exposure to cold weather, stress, lack of sleep. DIAGNOSTIC TESTS: Physical examination, rapid strep test, throat culture, blood tests (CBC), rapid flu test. TREATMENT PLAN: Rest, hydration, over-the-counter medications (decongestants, cough suppressants), saltwater gargles, fever reducers.",
            metadata={"topic": "respiratory_infection", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Pneumonia. PRIMARY SYMPTOMS: High fever, productive cough with colored sputum, difficulty breathing, chest pain. SECONDARY SYMPTOMS: Fatigue, loss of appetite, sweating, chills, confusion in elderly. CAUSES: Bacterial infections (Streptococcus pneumoniae, Haemophilus influenzae), viral infections (influenza, RSV), fungal infections, aspiration of food/liquid, smoking, chronic lung disease, weakened immune system, recent surgery, mechanical ventilation, age over 65, alcohol abuse. DIAGNOSTIC TESTS: Chest X-ray, sputum culture, blood tests (CBC, CRP), pulse oximetry, CT scan if needed. TREATMENT PLAN: Antibiotics, oxygen therapy, rest, hydration, fever reducers, hospitalization if severe.",
            metadata={"topic": "respiratory_infection", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Acute Gastroenteritis. PRIMARY SYMPTOMS: Diarrhea, nausea, vomiting, abdominal cramps. SECONDARY SYMPTOMS: Low-grade fever, loss of appetite, dehydration, fatigue. CAUSES: Viral infections (norovirus, rotavirus, adenovirus), bacterial infections (Salmonella, E. coli, Campylobacter), parasitic infections (Giardia), contaminated food or water, poor hand hygiene, close contact with infected individuals, travel to developing countries, weakened immune system, recent antibiotic use. DIAGNOSTIC TESTS: Stool culture, blood tests (CBC, electrolytes), rapid tests for specific pathogens. TREATMENT PLAN: Oral rehydration solutions, antiemetics, antidiarrheals, dietary modifications (BRAT diet), rest.",
            metadata={"topic": "acute_gastrointeritis", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Appendicitis. PRIMARY SYMPTOMS: Right lower abdominal pain, nausea, vomiting, loss of appetite. SECONDARY SYMPTOMS: Fever, abdominal tenderness, rebound tenderness, elevated white blood cell count. CAUSES: Blockage of appendix lumen by fecal matter, lymphoid hyperplasia, parasites, tumors, infection, inflammatory bowel disease, trauma, age (most common in 10-30 years), family history, low-fiber diet, previous abdominal surgery. DIAGNOSTIC TESTS: Physical examination, blood tests (CBC), abdominal CT scan or ultrasound, urinalysis. TREATMENT PLAN: Emergency appendectomy, antibiotics, pain management, IV fluids.",
            metadata={"topic": "appendicitis", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Benign Paroxysmal Positional Vertigo (BPPV). PRIMARY SYMPTOMS: Brief episodes of dizziness triggered by head movements, spinning sensation. SECONDARY SYMPTOMS: Nausea, vomiting, balance problems, anxiety. CAUSES: Dislodged calcium carbonate crystals in inner ear, head trauma, aging, inner ear infections, surgery, prolonged bed rest, migraines, Meniere's disease, vestibular neuritis, family history, osteoporosis, vitamin D deficiency. DIAGNOSTIC TESTS: Dix-Hallpike maneuver, physical examination, vestibular testing, head CT/MRI to rule out other causes. TREATMENT PLAN: Epley maneuver, vestibular rehabilitation exercises, antiemetics, avoiding triggering positions.",
            metadata={"topic": "dizziness", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Orthostatic Hypotension. PRIMARY SYMPTOMS: Dizziness upon standing, lightheadedness, fainting. SECONDARY SYMPTOMS: Nausea, fatigue, blurred vision, weakness. CAUSES: Dehydration, blood loss, medications (diuretics, beta-blockers, antidepressants), heart problems, endocrine disorders (diabetes, adrenal insufficiency), nervous system disorders (Parkinson's, multiple sclerosis), aging, prolonged bed rest, pregnancy, alcohol use, hot weather, large meals. DIAGNOSTIC TESTS: Blood pressure monitoring in different positions, tilt table test, blood tests, ECG. TREATMENT PLAN: Increased salt intake, hydration, compression stockings, medication adjustments, slow position changes.",
            metadata={"topic": "dizziness", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Foodborne Illness. PRIMARY SYMPTOMS: Nausea, vomiting, diarrhea, abdominal cramps. SECONDARY SYMPTOMS: Fever, chills, headache, muscle aches, dehydration. CAUSES: Consumption of contaminated food (undercooked meat, raw eggs, unpasteurized dairy, contaminated produce), bacterial toxins (Staphylococcus aureus, Clostridium botulinum), viral contamination, parasitic infections, improper food handling, cross-contamination, eating at restaurants with poor hygiene, travel to areas with poor sanitation. DIAGNOSTIC TESTS: Stool culture, blood tests, rapid antigen tests for specific pathogens. TREATMENT PLAN: Oral rehydration solutions, antiemetics, antidiarrheals, dietary modifications, rest.",
            metadata={"topic": "food_poisoning", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Osteoarthritis. PRIMARY SYMPTOMS: Joint pain, stiffness, reduced range of motion. SECONDARY SYMPTOMS: Joint swelling, crepitus, muscle weakness, fatigue. CAUSES: Aging, joint injury or trauma, repetitive stress on joints, obesity, genetics, joint malalignment, previous joint surgery, inflammatory conditions, metabolic disorders, occupational factors (repetitive movements), sports injuries, gender (more common in women). DIAGNOSTIC TESTS: X-rays, MRI, blood tests to rule out inflammatory arthritis, joint aspiration. TREATMENT PLAN: Anti-inflammatory medications, physical therapy, weight management, joint protection, corticosteroid injections, surgery for severe cases.",
            metadata={"topic": "joint_pain", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Rheumatoid Arthritis. PRIMARY SYMPTOMS: Joint pain, stiffness, swelling, symmetrical joint involvement. SECONDARY SYMPTOMS: Fatigue, fever, weight loss, morning stiffness lasting hours. CAUSES: Autoimmune disorder where immune system attacks joint lining, genetic predisposition, environmental triggers (smoking, infections, stress), hormonal factors (more common in women), age (30-60 years), family history, obesity, exposure to certain chemicals, viral or bacterial infections, gut microbiome changes. DIAGNOSTIC TESTS: Blood tests (rheumatoid factor, anti-CCP), X-rays, MRI, joint aspiration. TREATMENT PLAN: Disease-modifying antirheumatic drugs (DMARDs), biologic agents, anti-inflammatory medications, physical therapy, surgery for severe cases.",
            metadata={"topic": "joint_pain", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Mechanical Low Back Pain. PRIMARY SYMPTOMS: Back pain, stiffness, reduced mobility. SECONDARY SYMPTOMS: Muscle spasms, pain with movement, difficulty standing or sitting. CAUSES: Muscle strain or sprain, poor posture, heavy lifting, repetitive movements, obesity, weak core muscles, sedentary lifestyle, stress, anxiety, depression, smoking, age-related degeneration, previous back injury, pregnancy, poor ergonomics at work. DIAGNOSTIC TESTS: Physical examination, X-rays, MRI if red flags present, blood tests to rule out other causes. TREATMENT PLAN: Rest, ice/heat therapy, physical therapy, pain medications, muscle relaxants, exercise program.",
            metadata={"topic": "back_pain", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Herniated Disc. PRIMARY SYMPTOMS: Back pain, pain radiating to legs (sciatica), numbness, tingling. SECONDARY SYMPTOMS: Muscle weakness, difficulty walking, bowel/bladder dysfunction in severe cases. CAUSES: Age-related disc degeneration, heavy lifting with poor technique, sudden twisting or bending, trauma or injury, obesity, sedentary lifestyle, smoking, genetics, repetitive stress, poor posture, driving for long periods, vibration exposure, previous back surgery. DIAGNOSTIC TESTS: MRI, CT scan, electromyography (EMG), physical examination. TREATMENT PLAN: Physical therapy, pain medications, epidural steroid injections, surgery for severe cases with neurological deficits.",
            metadata={"topic": "back_pain", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Type 2 Diabetes Mellitus. PRIMARY SYMPTOMS: Increased thirst, frequent urination, fatigue, blurred vision. SECONDARY SYMPTOMS: Weight loss, slow-healing wounds, frequent infections, numbness in extremities. CAUSES: Insulin resistance, obesity, sedentary lifestyle, poor diet (high in processed foods, sugar), family history, age over 45, ethnicity (higher risk in African Americans, Hispanics, Native Americans), gestational diabetes history, polycystic ovary syndrome, high blood pressure, high cholesterol, sleep disorders, stress, certain medications. DIAGNOSTIC TESTS: Fasting blood glucose, HbA1c, oral glucose tolerance test, urine analysis, kidney function tests. TREATMENT PLAN: Blood glucose monitoring, oral medications (metformin, sulfonylureas), insulin therapy, dietary modifications, exercise, regular medical follow-up.",
            metadata={"topic": "diabetes", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Diabetic Ketoacidosis. PRIMARY SYMPTOMS: High blood sugar, excessive thirst, frequent urination, nausea, vomiting. SECONDARY SYMPTOMS: Abdominal pain, rapid breathing, fruity breath odor, confusion, fatigue. CAUSES: Severe insulin deficiency, missed insulin doses, infection or illness, heart attack, stroke, trauma, surgery, certain medications (steroids, diuretics), alcohol or drug use, stress, undiagnosed diabetes, pump malfunction, expired insulin, poor diabetes management. DIAGNOSTIC TESTS: Blood glucose, blood ketones, arterial blood gas, electrolyte panel, urine analysis. TREATMENT PLAN: Emergency insulin therapy, IV fluids, electrolyte replacement, monitoring, hospitalization.",
            metadata={"topic": "diabetes", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Essential Hypertension. PRIMARY SYMPTOMS: Often asymptomatic, may include headaches, dizziness. SECONDARY SYMPTOMS: Chest pain, shortness of breath, vision problems, irregular heartbeat. CAUSES: Genetic factors, age (risk increases with age), obesity, high salt intake, low potassium intake, excessive alcohol consumption, stress, sedentary lifestyle, smoking, sleep apnea, family history, race (higher in African Americans), chronic kidney disease, adrenal gland disorders, thyroid problems. DIAGNOSTIC TESTS: Blood pressure monitoring, ECG, echocardiogram, kidney function tests, urine analysis. TREATMENT PLAN: Lifestyle modifications (diet, exercise, stress reduction), antihypertensive medications, regular monitoring, salt restriction.",
            metadata={"topic": "hypertension", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Allergic Reaction. PRIMARY SYMPTOMS: Itching, rash, swelling, sneezing, runny nose. SECONDARY SYMPTOMS: Watery eyes, cough, wheezing, nausea, fatigue. CAUSES: Exposure to allergens (pollen, dust mites, pet dander, mold, foods, medications, insect stings, latex), family history of allergies, environmental factors, air pollution, climate change, hygiene hypothesis (reduced early exposure to microbes), stress, hormonal changes, respiratory infections, smoking, occupational exposure. DIAGNOSTIC TESTS: Skin prick tests, blood tests (IgE levels), elimination diet, challenge tests. TREATMENT PLAN: Antihistamines, corticosteroids, avoidance of triggers, immunotherapy for severe cases.",
            metadata={"topic": "allergic_reaction", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Anaphylaxis. PRIMARY SYMPTOMS: Difficulty breathing, swelling of face/throat, rapid heartbeat, dizziness. SECONDARY SYMPTOMS: Nausea, vomiting, loss of consciousness, hives, abdominal pain. CAUSES: Severe allergic reaction to foods (peanuts, tree nuts, shellfish, eggs, milk), medications (penicillin, aspirin, NSAIDs), insect stings (bees, wasps), latex, exercise, unknown triggers, previous history of anaphylaxis, asthma, family history, age (more common in children and young adults), certain medical conditions. DIAGNOSTIC TESTS: Physical examination, blood tests (tryptase), allergy testing, ECG. TREATMENT PLAN: Immediate epinephrine injection, emergency care, antihistamines, corticosteroids, oxygen therapy.",
            metadata={"topic": "allergic_reaction", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Urinary Tract Infection (UTI). PRIMARY SYMPTOMS: Frequent urination, burning sensation, urgency, cloudy urine. SECONDARY SYMPTOMS: Lower abdominal pain, blood in urine, fatigue, mild fever. CAUSES: Bacterial infection (E. coli most common), sexual activity, poor hygiene, holding urine too long, dehydration, diabetes, pregnancy, menopause, urinary catheter use, kidney stones, enlarged prostate, previous UTI, use of spermicides, tight clothing, bubble baths, certain birth control methods. DIAGNOSTIC TESTS: Urine analysis, urine culture, blood tests, kidney ultrasound if recurrent. TREATMENT PLAN: Antibiotics (trimethoprim-sulfamethoxazole, nitrofurantoin), increased fluid intake, pain relief, cranberry supplements.",
            metadata={"topic": "urinary_tract_infection", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Pyelonephritis. PRIMARY SYMPTOMS: High fever, back pain, frequent urination, burning sensation. SECONDARY SYMPTOMS: Nausea, vomiting, fatigue, blood in urine, confusion in elderly. CAUSES: Bacterial infection spreading from bladder to kidneys, untreated UTI, urinary obstruction (kidney stones, enlarged prostate), pregnancy, diabetes, weakened immune system, urinary catheter use, recent urinary tract surgery, vesicoureteral reflux, anatomical abnormalities, sexual activity, poor hygiene, dehydration. DIAGNOSTIC TESTS: Urine analysis, urine culture, blood tests, kidney ultrasound, CT scan. TREATMENT PLAN: IV antibiotics, hospitalization, pain management, increased fluid intake, follow-up care.",
            metadata={"topic": "urinary_tract_infection", "urgency": "high"},
        ),
        Document(
            page_content="DIAGNOSIS: Contact Dermatitis. PRIMARY SYMPTOMS: Red, itchy rash, skin inflammation, blisters. SECONDARY SYMPTOMS: Oozing, crusting, skin thickening, pain. CAUSES: Direct contact with irritants (soaps, detergents, chemicals, solvents), allergens (nickel, latex, poison ivy, cosmetics, fragrances), occupational exposure, jewelry, clothing dyes, topical medications, plants, metals, rubber, adhesives, repeated exposure to water, friction, temperature extremes. DIAGNOSTIC TESTS: Physical examination, patch testing, skin biopsy, allergy testing. TREATMENT PLAN: Topical corticosteroids, avoiding triggers, moisturizers, antihistamines, cool compresses.",
            metadata={"topic": "skin_rash", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Atopic Dermatitis (Eczema). PRIMARY SYMPTOMS: Dry, itchy patches, red inflamed skin, scaling. SECONDARY SYMPTOMS: Cracking, oozing, skin thickening, sleep disturbance. CAUSES: Genetic predisposition, immune system dysfunction, environmental triggers (allergens, irritants), dry skin, stress, temperature changes, sweating, certain foods, wool or synthetic fabrics, harsh soaps, infections, hormonal changes, family history of allergies, asthma, hay fever, urban environment, pollution. DIAGNOSTIC TESTS: Physical examination, skin biopsy, allergy testing, blood tests. TREATMENT PLAN: Moisturizers, topical corticosteroids, avoiding triggers, antihistamines, phototherapy for severe cases.",
            metadata={"topic": "skin_rash", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Conjunctivitis (Pink Eye). PRIMARY SYMPTOMS: Redness, itching, burning sensation, discharge. SECONDARY SYMPTOMS: Blurred vision, sensitivity to light, foreign body sensation, crusting of eyelids. CAUSES: Viral infections (adenovirus, herpes simplex), bacterial infections (Staphylococcus, Streptococcus), allergies (pollen, dust, pet dander), irritants (smoke, chemicals, chlorine), contact lens wear, poor hygiene, sharing towels or makeup, seasonal allergies, autoimmune conditions, eye trauma, foreign objects in eye. DIAGNOSTIC TESTS: Slit lamp examination, culture of discharge, fluorescein staining, allergy testing. TREATMENT PLAN: Antibiotic eye drops, artificial tears, warm compresses, avoiding contact lenses, steroid drops for severe cases.",
            metadata={"topic": "eye_problems", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Dry Eye Syndrome. PRIMARY SYMPTOMS: Dryness, burning sensation, gritty feeling, redness. SECONDARY SYMPTOMS: Blurred vision, sensitivity to light, eye fatigue, excessive tearing. CAUSES: Aging, hormonal changes (menopause), medications (antihistamines, decongestants, antidepressants), medical conditions (diabetes, rheumatoid arthritis, thyroid disorders), environmental factors (dry air, wind, smoke), contact lens wear, computer use, reading, LASIK surgery, autoimmune diseases, vitamin A deficiency, eyelid problems. DIAGNOSTIC TESTS: Tear production test, slit lamp examination, fluorescein staining, meibomian gland evaluation. TREATMENT PLAN: Artificial tears, warm compresses, eyelid hygiene, prescription eye drops, lifestyle modifications.",
            metadata={"topic": "eye_problems", "urgency": "low"},
        ),
        Document(
            page_content="DIAGNOSIS: Major Depressive Disorder. PRIMARY SYMPTOMS: Persistent sadness, loss of interest in activities, feelings of hopelessness. SECONDARY SYMPTOMS: Sleep changes, appetite changes, fatigue, difficulty concentrating, thoughts of self-harm. CAUSES: Genetic predisposition, brain chemistry imbalances, hormonal changes, life events (loss, trauma, stress), medical conditions, medications, substance abuse, personality traits, childhood trauma, social isolation, economic hardship, chronic illness, sleep problems, seasonal changes, postpartum period. DIAGNOSTIC TESTS: Psychological evaluation, depression screening tools, blood tests to rule out medical causes, thyroid function tests. TREATMENT PLAN: Psychotherapy (CBT, DBT), antidepressant medications, lifestyle modifications, support groups, crisis intervention if needed.",
            metadata={"topic": "mental_health", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Generalized Anxiety Disorder. PRIMARY SYMPTOMS: Excessive worry, restlessness, difficulty controlling worry. SECONDARY SYMPTOMS: Fatigue, difficulty concentrating, irritability, muscle tension, sleep problems. CAUSES: Genetic factors, brain chemistry imbalances, personality traits, life experiences, trauma, stress, medical conditions, substance abuse, caffeine, medications, family history, childhood adversity, perfectionism, overprotective parenting, major life changes, work stress, financial problems, health concerns. DIAGNOSTIC TESTS: Psychological evaluation, anxiety screening tools, blood tests to rule out medical causes, thyroid function tests. TREATMENT PLAN: Psychotherapy (CBT), anti-anxiety medications, stress management techniques, lifestyle modifications.",
            metadata={"topic": "mental_health", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Gestational Diabetes. PRIMARY SYMPTOMS: Often asymptomatic, may include increased thirst, frequent urination. SECONDARY SYMPTOMS: Fatigue, blurred vision, increased hunger, slow-healing wounds. CAUSES: Hormonal changes during pregnancy, insulin resistance, obesity, family history of diabetes, age over 25, previous gestational diabetes, polycystic ovary syndrome, certain ethnicities (Hispanic, African American, Native American, Asian), previous large baby, physical inactivity, poor diet, stress, multiple pregnancies, certain medications. DIAGNOSTIC TESTS: Glucose screening test, glucose tolerance test, regular blood glucose monitoring, HbA1c. TREATMENT PLAN: Dietary modifications, blood glucose monitoring, exercise, insulin therapy if needed, regular prenatal care.",
            metadata={"topic": "pregnancy_concerns", "urgency": "moderate"},
        ),
        Document(
            page_content="DIAGNOSIS: Preeclampsia. PRIMARY SYMPTOMS: High blood pressure, protein in urine, swelling. SECONDARY SYMPTOMS: Severe headaches, vision changes, abdominal pain, decreased fetal movement. CAUSES: First pregnancy, previous preeclampsia, family history, age under 20 or over 40, obesity, multiple pregnancies, chronic hypertension, diabetes, kidney disease, autoimmune disorders, in vitro fertilization, molar pregnancy, certain genetic factors, poor nutrition, stress, environmental factors, placental problems, immune system response to pregnancy. DIAGNOSTIC TESTS: Blood pressure monitoring, urine analysis, blood tests, ultrasound, fetal monitoring. TREATMENT PLAN: Bed rest, blood pressure medications, delivery planning, magnesium sulfate for severe cases, hospitalization.",
            metadata={"topic": "pregnancy_concerns", "urgency": "high"},
        ),
    ]
