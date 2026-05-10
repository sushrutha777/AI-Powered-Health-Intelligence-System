import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Full symptom list from disease_service.py
SYMPTOM_LIST = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing",
    "shivering", "chills", "joint_pain", "stomach_pain", "acidity",
    "ulcers_on_tongue", "muscle_wasting", "vomiting", "burning_micturition",
    "spotting_urination", "fatigue", "weight_gain", "anxiety",
    "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
    "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
    "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
    "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
    "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation",
    "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload",
    "swelling_of_stomach", "swelled_lymph_nodes", "malaise",
    "blurred_and_distorted_vision", "phlegm", "throat_irritation",
    "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
    "chest_pain", "weakness_in_limbs", "fast_heart_rate",
    "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
    "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
    "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes",
    "enlarged_thyroid", "brittle_nails", "swollen_extremeties",
    "excessive_hunger", "extra_marital_contacts", "drying_and_tingling_lips",
    "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
    "stiff_neck", "swelling_joints", "movement_stiffness",
    "spinning_movements", "loss_of_balance", "unsteadiness",
    "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
    "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases",
    "internal_itching", "toxic_look_(typhos)", "depression", "irritability",
    "muscle_pain", "altered_sensorium", "red_spots_over_body",
    "belly_pain", "abnormal_menstruation", "dischromic_patches",
    "watering_from_eyes", "increased_appetite", "polyuria",
    "family_history", "mucoid_sputum", "rusty_sputum",
    "lack_of_concentration", "visual_disturbances",
    "receiving_blood_transfusion", "receiving_unsterile_injections", "coma",
    "stomach_bleeding", "distention_of_abdomen",
    "history_of_alcohol_consumption", "fluid_overload.1",
    "blood_in_sputum", "prominent_veins_on_calf", "palpitations",
    "painful_walking", "pus_filled_pimples", "blackheads", "scurrying",
    "skin_peeling", "silver_like_dusting", "small_dents_in_nails",
    "inflammatory_nails", "blister", "red_sore_around_nose",
    "yellow_crust_ooze",
]

DISEASE_LIST = [
    "Fungal infection", "Allergy", "GERD", "Chronic cholestasis",
    "Drug Reaction", "Peptic ulcer disease", "AIDS", "Diabetes",
    "Gastroenteritis", "Bronchial Asthma", "Hypertension", "Migraine",
    "Cervical spondylosis", "Paralysis (brain hemorrhage)", "Jaundice",
    "Malaria", "Chicken pox", "Dengue", "Typhoid", "Hepatitis A",
    "Hepatitis B", "Hepatitis C", "Hepatitis D", "Hepatitis E",
    "Alcoholic hepatitis", "Tuberculosis", "Common Cold", "Pneumonia",
    "Dimorphic hemorrhoids (piles)", "Heart attack", "Varicose veins",
    "Hypothyroidism", "Hyperthyroidism", "Hypoglycemia",
    "Osteoarthristis", "Arthritis",
    "(vertigo) Paroxysmal Positional Vertigo", "Acne",
    "Urinary tract infection", "Psoriasis", "Impetigo",
]

data = []

for _ in range(5000):
    disease = np.random.choice(DISEASE_LIST)
    row = {s: 0 for s in SYMPTOM_LIST}
    
    # Add some random noise
    noise_symptoms = np.random.choice(SYMPTOM_LIST, size=np.random.randint(0, 3), replace=False)
    for s in noise_symptoms:
        row[s] = 1

    # Add characteristic symptoms for specific diseases
    if disease == 'Fungal infection':
        row['itching'] = 1
        row['skin_rash'] = 1
        row['dischromic_patches'] = 1
    elif disease == 'Allergy':
        row['continuous_sneezing'] = 1
        row['shivering'] = 1
        row['chills'] = 1
        row['watering_from_eyes'] = 1
    elif disease == 'Diabetes':
        row['fatigue'] = 1
        row['weight_loss'] = 1
        row['restlessness'] = 1
        row['lethargy'] = 1
        row['irregular_sugar_level'] = 1
        row['increased_appetite'] = 1
    elif disease == 'Hypertension':
        row['headache'] = 1
        row['chest_pain'] = 1
        row['dizziness'] = 1
        row['loss_of_balance'] = 1
    elif disease == 'Migraine':
        row['acidity'] = 1
        row['indigestion'] = 1
        row['headache'] = 1
        row['blurred_and_distorted_vision'] = 1
        row['depression'] = 1
    elif disease == 'Common Cold':
        row['continuous_sneezing'] = 1
        row['chills'] = 1
        row['fatigue'] = 1
        row['cough'] = 1
        row['high_fever'] = 1
        row['headache'] = 1
        row['swelled_lymph_nodes'] = 1
        row['malaise'] = 1
        row['phlegm'] = 1
        row['throat_irritation'] = 1
        row['redness_of_eyes'] = 1
        row['sinus_pressure'] = 1
        row['runny_nose'] = 1
        row['congestion'] = 1
        row['chest_pain'] = 1
        row['loss_of_smell'] = 1
    elif disease == 'Malaria':
        row['chills'] = 1
        row['vomiting'] = 1
        row['high_fever'] = 1
        row['sweating'] = 1
        row['headache'] = 1
        row['nausea'] = 1
        row['muscle_pain'] = 1
    elif disease == 'Typhoid':
        row['chills'] = 1
        row['vomiting'] = 1
        row['fatigue'] = 1
        row['high_fever'] = 1
        row['headache'] = 1
        row['nausea'] = 1
        row['constipation'] = 1
        row['abdominal_pain'] = 1
        row['diarrhoea'] = 1
        row['toxic_look_(typhos)'] = 1
        row['belly_pain'] = 1
    elif disease == 'Jaundice':
        row['itching'] = 1
        row['vomiting'] = 1
        row['fatigue'] = 1
        row['weight_loss'] = 1
        row['high_fever'] = 1
        row['yellowish_skin'] = 1
        row['dark_urine'] = 1
        row['abdominal_pain'] = 1
    
    # Generic mapping for everything else to avoid empty rows
    if sum(row.values()) == 0:
        row[np.random.choice(SYMPTOM_LIST)] = 1
        
    row['prognosis'] = disease
    data.append(row)

df = pd.DataFrame(data)
os.makedirs('backend/ml/data', exist_ok=True)
df.to_csv('backend/ml/data/disease_dataset.csv', index=False)
print('Comprehensive mock dataset created successfully at backend/ml/data/disease_dataset.csv')
