import base64
import json
import random
import re
import uuid
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db as firebase_db
import g4f
import streamlit as st
from streamlit.components.v1 import html as components_html

# ═══════════════════════════════════════════════════════════════
# MCQ BANK - Forensic Medicine & Toxicology
# ═══════════════════════════════════════════════════════════════

FORENSIC_TOPICS = {
    "Thanatology": [
        "Death", "Hypostasis (Postmortem Lividity)", "Rigor Mortis", "Cadaveric Spasm",
        "Putrefaction", "Sudden Death (Cardiovascular System Only)", "Death Certification",
    ],
    "Wounds": [
        "Abrasion", "Bruise (Contusion)", "Laceration", "Incised Wound (Cut Wound)",
        "Penetrating Wound", "Bite Mark", "Fabricated Wound",
    ],
    "Identification": [
        "Methods of Identification", "Identification of Dead Persons", "Identification of Living Persons",
        "Estimation of Age", "Period of Middle Age", "Estimation of Sex (Gender Determination)",
    ],
    "Asphyxia & Drowning": [
        "Stages of Asphyxia", "Classical Signs of Asphyxia", "Autopsy Findings in Asphyxia",
        "Suffocation", "Choking", "Smothering", "Manual Strangulation", "Ligature Strangulation",
        "Hanging", "Judicial Hanging", "Drowning",
    ],
    "Hair Examination": ["Hair Examination"],
    "Physical Injuries": [
        "Thermal Injury (Burns)", "Scalds", "Chemical Burns", "Electrical Burns",
        "Hyperthermic Injuries", "Hypothermic Injuries",
    ],
    "Head Injuries": [
        "Scalp Injuries", "Skull Fractures", "Injuries of the Meninges", "Brain Injuries",
        "Lucid Interval", "Brain Contusion and Laceration",
    ],
    "Medicolegal & Special Topics": [
        "Infanticide", "Abortion", "Ethics of Medical Practice", "Blood Examination",
        "Child Abuse", "Road Traffic Accidents (RTA)", "Firearm Injuries", "Regional Injuries",
        "Sexual Offences",
    ],
}

TOXICOLOGY_TOPICS = [
    "Introduction to Toxicology", "Animal Poisons", "Pesticide Toxicity", "Metal Poisoning",
    "Heavy Metal Poisoning", "Drug Abuse, Dependence and Addiction", "Volatile Substance Poisoning",
    "Cocaine Toxicity", "Cannabinoid Toxicity", "Opioid Toxicity", "Medicinal Alkaloid Poisoning",
    "Corrosive Poisoning", "Cyanide Poisoning", "Carbon Monoxide (CO) Poisoning",
    "Deliriant Poisoning", "Alcoholism", "Narcotics", "Hashish", "Toxicology of Therapeutics",
]

FORENSIC_MCQ_BANK = [
    {"q": "Tick mark the right statement regarding contusions:", "opts": {"A": "Contusions are easily occurring in males", "B": "On cutting over it, blood is extravascular and is not washable", "C": "It is caused by sharp instrument", "D": "Both A and C"}, "ans": "B", "section": "Wounds", "topic": "Bruise (Contusion)"},
    {"q": "Regarding post mortem appearance of heat stroke, which is the WRONG statement?", "opts": {"A": "Rigor mortis is delayed", "B": "The body temperature may continue to rise after death", "C": "Venous congestion is marked in all organs", "D": "Both B and C"}, "ans": "C", "section": "Thanatology", "topic": "Sudden Death"},
    {"q": "Tick mark the right statement:", "opts": {"A": "Extravasation of blood into tissue is hypostasis", "B": "Destruction of superficial layer of the skin is abrasion", "C": "Rope mark is an impact abrasion", "D": "All of the above"}, "ans": "D", "section": "Wounds", "topic": "Abrasion"},
    {"q": "The causative instrument of the fissure fracture is:", "opts": {"A": "Heavy blunt instrument with wide striking surface area and low momentum", "B": "Heavy blunt instrument with wide striking surface area and high momentum", "C": "Heavy blunt instrument with localised striking surface area and low momentum", "D": "None of the above"}, "ans": "B", "section": "Head Injuries", "topic": "Skull Fractures"},
    {"q": "Healing of the fissure fracture is by:", "opts": {"A": "Calcified callus", "B": "Fibrous membrane", "C": "Both A and B", "D": "None of the above"}, "ans": "C", "section": "Head Injuries", "topic": "Skull Fractures"},
    {"q": "Tick mark the right answer about violent asphyxia:", "opts": {"A": "External obstruction of mouth and nose is called choking asphyxia", "B": "Internal obstruction of respiratory passages is called smothering asphyxia", "C": "External pressure on the neck by hands is called throttling asphyxia", "D": "All of the above"}, "ans": "D", "section": "Asphyxia & Drowning", "topic": "Stages of Asphyxia"},
    {"q": "A blunt force on the skull may cause the following types of fractures EXCEPT:", "opts": {"A": "Fissure fracture", "B": "Chipped fracture", "C": "Depressed fracture", "D": "Comminuted fracture"}, "ans": "B", "section": "Head Injuries", "topic": "Skull Fractures"},
    {"q": "Grazes are injuries produced by:", "opts": {"A": "Pressure by blunt impact force", "B": "Friction with sharp objects as pin", "C": "Moving a sharp instrument as knife", "D": "Friction of the skin with a large surface of a rough object"}, "ans": "D", "section": "Wounds", "topic": "Abrasion"},
    {"q": "Extradural hemorrhage is due to rupture of:", "opts": {"A": "Middle meningeal artery", "B": "Superior sagittal sinus", "C": "Emissary veins", "D": "All of the above"}, "ans": "A", "section": "Head Injuries", "topic": "Brain Injuries"},
    {"q": "Post-mortem greenish discoloration of the skin is due to:", "opts": {"A": "Sulphmethaemoglobin", "B": "Oxyhaemoglobin", "C": "Reduced haemoglobin", "D": "None of the above"}, "ans": "A", "section": "Thanatology", "topic": "Putrefaction"},
    {"q": "Human hair shows which of the following?", "opts": {"A": "Regular cuticle, narrow cortex, narrow medulla", "B": "Regular cuticle, narrow cortex, broad medulla", "C": "Usually cortex only", "D": "B and C"}, "ans": "D", "section": "Identification", "topic": "Hair Examination"},
    {"q": "Hair shows a healthy root with ruptured sheath when:", "opts": {"A": "Fallen by itself", "B": "Pulled by force", "C": "Cut by a sharp instrument", "D": "Injured by a rough blunt object"}, "ans": "B", "section": "Identification", "topic": "Hair Examination"},
    {"q": "All soft tissues of the dead body are transformed into liquid substances after:", "opts": {"A": "One week", "B": "Two weeks", "C": "One month", "D": "Six months"}, "ans": "C", "section": "Thanatology", "topic": "Putrefaction"},
    {"q": "Which of the following is NOT a classical sign of asphyxia?", "opts": {"A": "Cyanosis", "B": "Petechial hemorrhages", "C": "Rigor mortis", "D": "Pulmonary edema"}, "ans": "C", "section": "Asphyxia & Drowning", "topic": "Stages of Asphyxia"},
    {"q": "Thermal injury with charring of tissues occurs at temperature above:", "opts": {"A": "60°C", "B": "65°C", "C": "75°C", "D": "90°C"}, "ans": "C", "section": "Physical Injuries", "topic": "Thermal Injury (Burns)"},
    {"q": "Death certificate should be issued EXCEPT in case of:", "opts": {"A": "Sudden death", "B": "Death from natural causes after medical attendance", "C": "Suspicious death", "D": "Death after medical treatment for known disease"}, "ans": "C", "section": "Thanatology", "topic": "Death Certification"},
    {"q": "Rigor mortis begins usually after:", "opts": {"A": "15 minutes of death", "B": "2-6 hours of death", "C": "12-24 hours of death", "D": "24-36 hours of death"}, "ans": "B", "section": "Thanatology", "topic": "Rigor Mortis"},
    {"q": "Cadaveric spasm is different from rigor mortis in that it:", "opts": {"A": "Occurs immediately after death", "B": "Is localized", "C": "Both A and B", "D": "Neither A nor B"}, "ans": "C", "section": "Thanatology", "topic": "Cadaveric Spasm"},
    {"q": "In case of drowning, the condition of the body is best identified by:", "opts": {"A": "Pallor mortis", "B": "Rigor mortis", "C": "Livor mortis (pink coloration)", "D": "Hypostasis"}, "ans": "C", "section": "Asphyxia & Drowning", "topic": "Drowning"},
    {"q": "Fabricated wounds are produced by:", "opts": {"A": "Blunt trauma", "B": "Sharp trauma", "C": "Self-infliction by victim", "D": "Environmental friction"}, "ans": "C", "section": "Wounds", "topic": "Fabricated Wound"},
    {"q": "The most reliable method for identification of dead persons is:", "opts": {"A": "Dental records", "B": "Fingerprints", "C": "DNA analysis", "D": "Facial features"}, "ans": "C", "section": "Identification", "topic": "Methods of Identification"},
    {"q": "Which of the following is a medicolegal report for living person?", "opts": {"A": "Postmortem examination", "B": "Ante-mortem wound examination", "C": "Injury report", "D": "B and C"}, "ans": "D", "section": "Medicolegal & Special Topics", "topic": "Blood Examination"},
    {"q": "Road traffic accidents (RTA) require medicolegal examination EXCEPT:", "opts": {"A": "When there is injury", "B": "When there is death", "C": "When there is property damage only", "D": "When police is involved"}, "ans": "C", "section": "Medicolegal & Special Topics", "topic": "Road Traffic Accidents (RTA)"},
    {"q": "Judicial hanging is characterized by which of the following?", "opts": {"A": "Knot on the side of neck", "B": "Knot at back of neck", "C": "Knot under chin", "D": "Knot anywhere around neck"}, "ans": "B", "section": "Asphyxia & Drowning", "topic": "Hanging"},
    {"q": "A penetrating wound is best described as:", "opts": {"A": "A wound caused by a blunt object", "B": "A wound that pierces through skin and underlying tissues", "C": "A wound that scratches the surface only", "D": "A wound caused by friction"}, "ans": "B", "section": "Wounds", "topic": "Penetrating Wound"},
    {"q": "Which burn classification represents full thickness burns?", "opts": {"A": "First degree", "B": "Second degree", "C": "Third degree", "D": "Fourth degree"}, "ans": "C", "section": "Physical Injuries", "topic": "Thermal Injury (Burns)"},
    {"q": "Hypostasis (livor mortis) appears after:", "opts": {"A": "30 minutes", "B": "1-2 hours", "C": "6-8 hours", "D": "24 hours"}, "ans": "B", "section": "Thanatology", "topic": "Hypostasis (Postmortem Lividity)"},
    {"q": "Which fracture occurs due to sudden blow to the skull?", "opts": {"A": "Linear fracture", "B": "Depressed fracture", "C": "Basilar fracture", "D": "All of the above"}, "ans": "D", "section": "Head Injuries", "topic": "Skull Fractures"},
    {"q": "The best indicator of the time of death is:", "opts": {"A": "Rigor mortis", "B": "Hypostasis", "C": "Body temperature (algor mortis)", "D": "None of the above"}, "ans": "C", "section": "Thanatology", "topic": "Death"},
    {"q": "Child abuse indicators include ALL EXCEPT:", "opts": {"A": "Repeated injuries at different healing stages", "B": "Injuries inconsistent with history", "C": "Multiple injuries in protected areas", "D": "Accidental injuries during play"}, "ans": "D", "section": "Medicolegal & Special Topics", "topic": "Child Abuse"},
    {"q": "Sexual offences examination should include EXCEPT:", "opts": {"A": "Collection of semen samples", "B": "Examination of genital injuries", "C": "Blood typing of victim", "D": "Radiological examination of bones"}, "ans": "D", "section": "Medicolegal & Special Topics", "topic": "Sexual Offences"},
]

TOXICOLOGY_MCQ_BANK = [
    {"q": "Which of the following is NOT a part of phase I biotransformation of toxicants?", "opts": {"A": "Oxidation", "B": "Hydrolysis", "C": "Reduction", "D": "Glutathione conjugation"}, "ans": "D", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Alcohol concentrated forms are more quickly absorbed than diluted forms.", "opts": {"A": "True", "B": "False", "C": "Depends on food intake", "D": "Depends on alcohol type"}, "ans": "B", "section": "Toxicology Basics", "topic": "Alcoholism"},
    {"q": "All of the following chemicals are poorly absorbed by activated charcoal EXCEPT:", "opts": {"A": "Boric acid", "B": "Salicylic acid", "C": "Ferrous sulfate", "D": "Lithium salts"}, "ans": "C", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Which of the following is NOT recommended in case of paraquat poisoning with stable condition?", "opts": {"A": "Charcoal administration", "B": "Oxygen administration", "C": "Washing of exposed skin", "D": "Maintenance of open airway"}, "ans": "B", "section": "Pesticide Toxicity", "topic": "Pesticide Toxicity"},
    {"q": "Early toxic manifestations of salicylate poisoning are due to action on which target organ?", "opts": {"A": "Otolaryngologic system", "B": "Heart", "C": "Liver", "D": "Kidney"}, "ans": "A", "section": "Medicinal Alkaloid Poisoning", "topic": "Medicinal Alkaloid Poisoning"},
    {"q": "Which of the following chelators is effective if administered orally?", "opts": {"A": "Succimer (Chemet)", "B": "CaNa2-EDTA (Calcium Disodium Versenate)", "C": "Dimercaprol (BAL)", "D": "Deferoxamine"}, "ans": "A", "section": "Heavy Metal Poisoning", "topic": "Heavy Metal Poisoning"},
    {"q": "A 39-year-old woman attempted suicide by taking fenthion. She became hypotensive with sialorrhea and generalized muscle fasciculation. The treatment must include:", "opts": {"A": "Good hydration, antibiotic and observation", "B": "Decontamination, chelating agent and reassure", "C": "Decontamination, atropine, pralidoxim and supportive therapy", "D": "Reassure, antidepressant and psychiatric assessment"}, "ans": "C", "section": "Pesticide Toxicity", "topic": "Pesticide Toxicity"},
    {"q": "A 49-year-old ingested 125g of fungicide containing 3.5% methoxyethylmercury chloride. For diagnosis you need all tests EXCEPT:", "opts": {"A": "Urine mercury", "B": "Whole-blood concentrations", "C": "Hair analysis", "D": "Stool analysis"}, "ans": "D", "section": "Heavy Metal Poisoning", "topic": "Heavy Metal Poisoning"},
    {"q": "A victim of heavy metal poisoning has an odor of garlic on his breath. The most probable cause is:", "opts": {"A": "Lead", "B": "Zinc", "C": "Arsenic", "D": "Mercury"}, "ans": "C", "section": "Heavy Metal Poisoning", "topic": "Heavy Metal Poisoning"},
    {"q": "Which of the following is a TRUE statement?", "opts": {"A": "Pica refers solely to ingestion of lead-based substances", "B": "Plumbism is more likely in children aged 1-5 years", "C": "Acute lead poisoning can be detected in blood up to 40 days", "D": "Chronic lead poisoning causes polycythemia"}, "ans": "B", "section": "Heavy Metal Poisoning", "topic": "Heavy Metal Poisoning"},
    {"q": "Emesis with syrup of ipecac is contraindicated in:", "opts": {"A": "Coma", "B": "Convulsions", "C": "Absent gag reflex", "D": "All of the above"}, "ans": "D", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Activated charcoal acts by:", "opts": {"A": "Absorption", "B": "Adsorption", "C": "Filtration", "D": "Neutralization"}, "ans": "B", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Activated charcoal is EFFECTIVE in the following EXCEPT:", "opts": {"A": "Acetaminophen", "B": "Barbiturates", "C": "Methyl alcohol", "D": "Theophylline"}, "ans": "C", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "The following affect absorption of poison EXCEPT:", "opts": {"A": "Dose of poison", "B": "State of poison", "C": "Color of poison", "D": "Solubility of poison"}, "ans": "C", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Cyanide poisoning is most rapidly fatal when the poison is placed in:", "opts": {"A": "High acidity medium", "B": "Low acidity medium", "C": "Non-acidic medium", "D": "Neutral pH"}, "ans": "B", "section": "Corrosive Poisoning", "topic": "Cyanide Poisoning"},
    {"q": "The most rapid form of poison is:", "opts": {"A": "Solid", "B": "Gas", "C": "Powder", "D": "Solution"}, "ans": "B", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Best method for barbiturate treatment is:", "opts": {"A": "Gradual withdrawal", "B": "Abrupt withdrawal", "C": "Use of antibodies", "D": "Psychiatric drugs"}, "ans": "A", "section": "Drug Abuse and Dependence", "topic": "Barbiturates"},
    {"q": "Nalini test is used for the diagnosis of:", "opts": {"A": "Amphetamine", "B": "Alcohol", "C": "Cocaine", "D": "Opioids"}, "ans": "C", "section": "Drug Abuse and Dependence", "topic": "Cocaine Toxicity"},
    {"q": "The most common complication of cocaine abuse by sniffing is:", "opts": {"A": "Death", "B": "Cerebral hemorrhage", "C": "Nasal septum perforation", "D": "Heart failure"}, "ans": "C", "section": "Drug Abuse and Dependence", "topic": "Cocaine Toxicity"},
    {"q": "Morphine dependence is characterized by:", "opts": {"A": "Constricted pupils", "B": "Constipation", "C": "Mask-like face", "D": "Visual hallucinations"}, "ans": "B", "section": "Drug Abuse and Dependence", "topic": "Opioid Toxicity"},
    {"q": "Cocaine dependence is best characterized by:", "opts": {"A": "Jaundice", "B": "Tremor", "C": "Mask-like face", "D": "Tactile hallucinations"}, "ans": "D", "section": "Drug Abuse and Dependence", "topic": "Cocaine Toxicity"},
    {"q": "The most common complication of alcohol is:", "opts": {"A": "Pleuritis", "B": "Liver cirrhosis", "C": "Gastritis", "D": "Pancreatitis"}, "ans": "B", "section": "Drug Abuse and Dependence", "topic": "Alcoholism"},
    {"q": "An idiosyncratic drug reaction is:", "opts": {"A": "Normal response", "B": "Anaphylactic reaction", "C": "Unexpected response to a drug", "D": "Predictable side effect"}, "ans": "C", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "The most serious complication of solvent abuse is:", "opts": {"A": "Coma", "B": "Pleuritis", "C": "Liver cirrhosis", "D": "CNS damage"}, "ans": "D", "section": "Drug Abuse and Dependence", "topic": "Volatile Substance Poisoning"},
    {"q": "Which of the following is hepatotoxic?", "opts": {"A": "Alcohol", "B": "Cyanide", "C": "Amphetamine", "D": "Cocaine"}, "ans": "A", "section": "Drug Abuse and Dependence", "topic": "Alcoholism"},
    {"q": "Carbon monoxide poisoning manifests with:", "opts": {"A": "Cherry-red livor mortis", "B": "Pale livor mortis", "C": "Purple livor mortis", "D": "Green livor mortis"}, "ans": "A", "section": "Corrosive Poisoning", "topic": "Carbon Monoxide (CO) Poisoning"},
    {"q": "Which of the following does NOT cause cyanosis?", "opts": {"A": "Carbon monoxide", "B": "Cyanide", "C": "Arsenic", "D": "Strychnine"}, "ans": "D", "section": "Toxicology Basics", "topic": "Introduction to Toxicology"},
    {"q": "Pesticide poisoning with cholinesterase inhibition causes:", "opts": {"A": "Mydriasis", "B": "Miosis", "C": "Keratitis", "D": "Blindness"}, "ans": "B", "section": "Pesticide Toxicity", "topic": "Pesticide Toxicity"},
    {"q": "Which chelator is used for lead poisoning in children?", "opts": {"A": "EDTA", "B": "Succimer", "C": "BAL", "D": "Penicillamine"}, "ans": "B", "section": "Heavy Metal Poisoning", "topic": "Heavy Metal Poisoning"},
    {"q": "Amphetamine abuse causes all EXCEPT:", "opts": {"A": "Tachycardia", "B": "Mydriasis", "C": "Hyperthermia", "D": "Bradypnea"}, "ans": "D", "section": "Drug Abuse and Dependence", "topic": "Amphetamine Toxicity"},
]

def get_random_forensic_mcqs(count=30):
    return random.sample(FORENSIC_MCQ_BANK, min(count, len(FORENSIC_MCQ_BANK)))

def get_random_toxicology_mcqs(count=30):
    return random.sample(TOXICOLOGY_MCQ_BANK, min(count, len(TOXICOLOGY_MCQ_BANK)))

def get_mixed_mcqs(forensic_count=30, toxicology_count=30):
    forensic = random.sample(FORENSIC_MCQ_BANK, min(forensic_count, len(FORENSIC_MCQ_BANK)))
    toxicology = random.sample(TOXICOLOGY_MCQ_BANK, min(toxicology_count, len(TOXICOLOGY_MCQ_BANK)))
    return forensic + toxicology

# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "banner.png"  

try:
    img_b64 = get_base64_of_bin_file(image_path)
    st.markdown(
        f"""
        <div style="width:100%; margin-top: 20px;">
            <img src="data:image/png;base64,{img_b64}" style="
                width: 100%;
                display: block;
                border-radius: 14px;
                object-fit: cover;
            " alt="Simulator banner">
        </div>
        """,
        unsafe_allow_html=True,
    )
except FileNotFoundError:
    pass

st.set_page_config(page_title="4th Year Exam Simulator", page_icon="🩺", layout="wide")

if not firebase_admin._apps:
    try:
        cred_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "databaseURL": st.secrets["FIREBASE_DATABASE_URL"]
        })
    except Exception as _fb_err:
        st.error(f"خطأ في الاتصال بـ Firebase: {_fb_err}")
        st.stop()

ADMIN_USERNAME = "Ameenbadda"
ADMIN_PASSWORD = "862000A"

st.markdown(
    """
    <style>
        :root {
            --ink: #123C69;
            --teal: #1D9A8A;
            --mint: #E7F6F2;
            --coral: #F46F5E;
            --amber: #F2B84B;
            --paper: #FFFFFF;
            --soft: #F5FAFA;
            --line: #D8E7E7;
            --muted: #667085;
            --shadow-sm: 0 10px 24px rgba(18, 60, 105, 0.08);
            --shadow-md: 0 18px 42px rgba(18, 60, 105, 0.14);
        }
        .stApp {
            background:
                linear-gradient(135deg, rgba(29,154,138,0.10) 0 18%, transparent 18% 100%),
                linear-gradient(45deg, rgba(244,111,94,0.08) 0 12%, transparent 12% 100%),
                linear-gradient(180deg, #f7fbfb 0%, #eef7f5 48%, #f9fbfd 100%);
        }
        h1 {
            text-align: center;
            color: var(--ink);
            font-weight: 900 !important;
            text-shadow: 0 1px 0 rgba(255,255,255,0.85);
        }
        .mcq-card {
            background: rgba(255,255,255,0.94);
            border: 1px solid var(--line);
            border-right: 5px solid var(--teal);
            padding: 16px 18px;
            border-radius: 14px;
            margin-bottom: 14px;
            box-shadow: var(--shadow-sm);
        }
        .mcq-correct {
            border-right: 5px solid #28a745 !important;
            background: linear-gradient(180deg, #f0fff4, #ffffff) !important;
        }
        .mcq-wrong {
            border-right: 5px solid #dc3545 !important;
            background: linear-gradient(180deg, #fff5f5, #ffffff) !important;
        }
        .hero-panel {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 16px;
            background: linear-gradient(135deg, rgba(18,60,105,0.98) 0%, rgba(29,154,138,0.96) 72%, rgba(242,184,75,0.82) 100%);
            color: white;
            border-radius: 18px;
            padding: 28px;
            margin: 10px 0 18px 0;
            box-shadow: 0 22px 52px rgba(18, 60, 105, 0.22);
        }
        .hero-panel h2 {
            margin: 0 0 8px 0;
            font-size: 2rem;
            color: #ffffff !important;
        }
        .visual-tile {
            background: rgba(255,255,255,0.16);
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #ffffff !important;
            cursor: pointer;
            transition: all 0.18s ease;
            text-decoration: none !important;
        }
        .visual-tile:hover {
            background: rgba(255,255,255,0.24);
            transform: translateY(-4px);
        }
        .stButton>button {
            width: 100% !important;
            padding: 13px 20px !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, var(--ink), var(--teal)) !important;
            color: white !important;
            font-weight: bold !important;
            transition: all 0.18s ease !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🩺 محاكي امتحانات السنة الرابعة")

# ═══════════════════════════════════════════════════════════════
# Forensic & Toxicology MCQ Committee
# ═══════════════════════════════════════════════════════════════

def render_ft_mcq_committee():
    st.header("📝 لجنة MCQs النظري — Forensic Medicine & Toxicology")
    st.write("أسئلة انجليزية متقدمة من مواضيع الفرونسك والتوكسو، مع تصحيح مفصل بعد إنهاء الامتحان.")

    back_col, _ = st.columns([1, 4])
    with back_col:
        if st.button("رجوع للجان فرونسك و توكسو", key="back_to_forensic_home"):
            st.session_state.forensic_board = ""
            if "ft" in st.query_params:
                del st.query_params["ft"]
            st.rerun()

    st.markdown("### اختر نوع الأسئلة")
    col_for, col_tox, col_mix, col_past = st.columns(4)
    mode_clicked = None
    
    with col_for:
        if st.button("🔬 فرونسك فقط\n(30 سؤال)", key="ft_forensic_30", use_container_width=True):
            mode_clicked = "Forensic only"
    
    with col_tox:
        if st.button("☠️ توكسو فقط\n(30 سؤال)", key="ft_toxicology_30", use_container_width=True):
            mode_clicked = "Toxicology only"
    
    with col_mix:
        if st.button("⚖️ فرونسك + توكسو\n(60 سؤال)", key="ft_mixed_60", use_container_width=True):
            mode_clicked = "Mixed"
    
    with col_past:
        st.button("📚 أسئلة السنوات\n(قريباً)", key="ft_past_years", disabled=True, use_container_width=True)

    if mode_clicked:
        st.session_state.ft_mcq_mode = mode_clicked
        st.session_state.ft_mcq_questions = []
        st.session_state.ft_mcq_answers = {}
        st.session_state.ft_mcq_submitted = False
        
        with st.spinner("جاري تحضير الأسئلة..."):
            try:
                if mode_clicked == "Forensic only":
                    st.session_state.ft_mcq_questions = get_random_forensic_mcqs(30)
                elif mode_clicked == "Toxicology only":
                    st.session_state.ft_mcq_questions = get_random_toxicology_mcqs(30)
                else:
                    st.session_state.ft_mcq_questions = get_mixed_mcqs(30, 30)
            except Exception as err:
                st.error(f"خطأ: {str(err)}")
        st.rerun()

    questions = st.session_state.get("ft_mcq_questions", [])
    if not questions:
        st.info("اختر نوع الأسئلة من الأزرار بالأعلى لبدء امتحان جديد.")
        return

    mode_ar = {
        "Forensic only": "🔬 فرونسك فقط",
        "Toxicology only": "☠️ توكسو فقط",
        "Mixed": "⚖️ فرونسك + توكسو",
    }.get(st.session_state.ft_mcq_mode, st.session_state.ft_mcq_mode)
    
    st.success(f"✅ تم تحضير: {mode_ar} — عدد الأسئلة: {len(questions)}")

    for i, mcq in enumerate(questions):
        saved = st.session_state.ft_mcq_answers.get(i)
        options_list = [f"{letter}. {mcq['opts'][letter]}" for letter in ["A", "B", "C", "D"]]

        if st.session_state.ft_mcq_submitted:
            is_correct = saved == mcq["ans"]
            card_class = "mcq-card mcq-correct" if is_correct else "mcq-card mcq-wrong"
            status_icon = "✅" if is_correct else "❌"
            chosen_text = mcq["opts"].get(saved, "لم تتم الإجابة") if saved else "لم تتم الإجابة"
            correct_text = mcq["opts"][mcq["ans"]]
            
            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{status_icon} Q{i + 1}. {mcq['q']}</b><br>
                    <span style="color:#667085;font-size:0.9rem;">الموضوع: {mcq.get('topic', '—')} | القسم: {mcq.get('section', '—')}</span><br><br>
                    <b>إجابتك:</b> {saved or '—'} - {chosen_text}<br>
                    <b>الإجابة الصحيحة:</b> {mcq['ans']} - {correct_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            default_idx = None
            if saved:
                for idx, opt in enumerate(options_list):
                    if opt.startswith(saved + "."):
                        default_idx = idx
                        break
            
            chosen = st.radio(
                f"Q{i + 1}. {mcq['q']}",
                options=options_list,
                index=default_idx,
                key=f"ft_mcq_q_{i}",
            )
            st.caption(f"الموضوع: {mcq.get('topic', '—')} | القسم: {mcq.get('section', '—')}")
            
            if chosen:
                st.session_state.ft_mcq_answers[i] = chosen[0]

    st.write("---")

    if not st.session_state.ft_mcq_submitted:
        answered = len(st.session_state.ft_mcq_answers)
        st.caption(f"أجبت على {answered} من {len(questions)} سؤال.")
        
        if st.button("✅ تحقق من إجاباتي", key="ft_mcq_submit", use_container_width=True):
            st.session_state.ft_mcq_submitted = True
            st.rerun()
    else:
        correct_count = sum(
            1 for i, mcq in enumerate(questions)
            if st.session_state.ft_mcq_answers.get(i) == mcq["ans"]
        )
        total = len(questions)
        pct = round(correct_count / total * 100) if total else 0
        
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#123C69,#1D9A8A);color:white;
                border-radius:14px;padding:22px 28px;text-align:center;margin:10px 0 20px 0;
                box-shadow:0 8px 24px rgba(18,60,105,0.18);">
                <div style="font-size:2.2rem;font-weight:900;">{correct_count}/{total}</div>
                <div style="font-size:1.3rem;margin:4px 0;">{pct}%</div>
                <div style="font-size:1rem;margin-top:8px;">
                    {"🌟 ممتاز!" if pct >= 80 else "👍 جيد جداً" if pct >= 65 else "📘 مقبول" if pct >= 50 else "📖 يحتاج مراجعة"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col_retry, col_new = st.columns(2)
        with col_retry:
            if st.button("🔄 إعادة الامتحان", key="ft_mcq_retry", use_container_width=True):
                st.session_state.ft_mcq_answers = {}
                st.session_state.ft_mcq_submitted = False
                st.rerun()
        
        with col_new:
            if st.button("🆕 توليد مجموعة جديدة", key="ft_mcq_new_set", use_container_width=True):
                mode = st.session_state.ft_mcq_mode or "Forensic only"
                st.session_state.ft_mcq_mode = mode
                st.session_state.ft_mcq_questions = []
                st.session_state.ft_mcq_answers = {}
                st.session_state.ft_mcq_submitted = False
                with st.spinner("جاري توليد مجموعة جديدة..."):
                    try:
                        if mode == "Forensic only":
                            st.session_state.ft_mcq_questions = get_random_forensic_mcqs(30)
                        elif mode == "Toxicology only":
                            st.session_state.ft_mcq_questions = get_random_toxicology_mcqs(30)
                        else:
                            st.session_state.ft_mcq_questions = get_mixed_mcqs(30, 30)
                    except Exception as err:
                        st.error(f"خطأ: {str(err)}")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════════

if "ft_mcq_questions" not in st.session_state:
    st.session_state.ft_mcq_questions = []
if "ft_mcq_answers" not in st.session_state:
    st.session_state.ft_mcq_answers = {}
if "ft_mcq_submitted" not in st.session_state:
    st.session_state.ft_mcq_submitted = False
if "ft_mcq_mode" not in st.session_state:
    st.session_state.ft_mcq_mode = ""
if "forensic_board" not in st.session_state:
    st.session_state.forensic_board = ""

# ═══════════════════════════════════════════════════════════════
# Main Flow
# ═══════════════════════════════════════════════════════════════

subject = st.query_params.get("subject", "")
ft_param = st.query_params.get("ft", "")

if subject == "forensic":
    if ft_param == "mcq":
        st.session_state.forensic_board = "mcq"
    else:
        st.session_state.forensic_board = ""

if st.session_state.forensic_board == "mcq":
    render_ft_mcq_committee()
else:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.72); border-radius: 18px; margin: 20px 0;">
            <h2>🎯 لجان مادتي الفرونسك و التوكسو</h2>
            <p style="font-size: 1.05rem; color: #444;">واجهة تدريب منظمة وسريعة</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤰🩺👶\n\nالنساء والولادة\nObstetrics & Gynecology", 
                     use_container_width=True, 
                     key="subject_gyne"):
            st.query_params["subject"] = "gyne"
            st.rerun()
    
    with col2:
        if st.button("🔬💀⚖️\n\nالطب الشرعي والسموم\nForensic & Toxicology", 
                     use_container_width=True,
                     key="subject_forensic"):
            st.query_params["subject"] = "forensic"
            st.session_state.forensic_board = ""
            st.rerun()
    
    st.write("---")
    
    # Forensic Dashboard
    if subject == "forensic" and st.session_state.forensic_board == "":
        st.markdown(
            """
            <div class="hero-panel">
                <div>
                    <h2>📋 لجان الفرونسك و التوكسو</h2>
                    <p>محاكي امتحان الطب الشرعي والسموم — لجنة MCQs النظري. أسئلة معدة وفقاً لمستوى الجامعة بنمط امتحانات السنوات السابقة.</p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <a class="visual-tile" href="?subject=forensic&ft=mcq" target="_self" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                        <div style="font-size: 2rem;">📝</div>
                        <div style="font-weight: bold;">لجنة MCQs النظري</div>
                        <div style="font-size: 0.9rem;">فرونسك / توكسو / مختلط</div>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
