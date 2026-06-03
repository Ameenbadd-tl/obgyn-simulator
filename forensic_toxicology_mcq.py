# ═══════════════════════════════════════════════════════════════
# Forensic Medicine & Toxicology — MCQ Question Bank
# 150 Total Questions (30 questions per set, 5 sets)
# Difficulty: Moderate to Advanced (Old University Exam Style)
# ═══════════════════════════════════════════════════════════════

# Forensic Medicine Topics
FORENSIC_TOPICS = {
    "Thanatology": [
        "Death", "Hypostasis (Postmortem Lividity)", "Rigor Mortis", "Cadaveric Spasm",
        "Putrefaction", "Sudden Death", "Death Certification",
    ],
    "Wounds": [
        "Abrasion", "Bruise (Contusion)", "Laceration", "Incised Wound",
        "Penetrating Wound", "Bite Mark", "Fabricated Wound",
    ],
    "Identification": [
        "Methods of Identification", "Identification of Dead Persons",
        "Estimation of Age", "Estimation of Sex (Gender Determination)",
    ],
    "Asphyxia & Drowning": [
        "Stages of Asphyxia", "Suffocation", "Choking", "Smothering",
        "Manual Strangulation", "Ligature Strangulation", "Hanging", "Drowning",
    ],
    "Physical Injuries": [
        "Thermal Injury (Burns)", "Scalds", "Chemical Burns", "Electrical Burns",
        "Hyperthermic Injuries", "Hypothermic Injuries",
    ],
    "Head Injuries": [
        "Scalp Injuries", "Skull Fractures", "Brain Injuries", "Lucid Interval",
    ],
    "Medicolegal Topics": [
        "Infanticide", "Abortion", "Child Abuse", "Road Traffic Accidents (RTA)",
        "Firearm Injuries", "Sexual Offences", "Blood Examination",
    ],
}

# Toxicology Topics
TOXICOLOGY_TOPICS = [
    "Introduction to Toxicology", "Pesticide Toxicity", "Metal Poisoning",
    "Heavy Metal Poisoning", "Drug Abuse and Dependence", "Volatile Substance Poisoning",
    "Cocaine Toxicity", "Cannabinoid Toxicity", "Opioid Toxicity",
    "Medicinal Alkaloid Poisoning", "Corrosive Poisoning", "Cyanide Poisoning",
    "Carbon Monoxide (CO) Poisoning", "Alcoholism", "Barbiturates",
    "Salicylate Poisoning", "Paraquat Poisoning", "Mercury Poisoning",
    "Lead Poisoning", "Amphetamine Toxicity",
]

# ═══════════════════════════════════════════════════════════════
# FORENSIC MEDICINE MCQ BANK (75 Questions)
# ═══════════════════════════════════════════════════════════════

FORENSIC_MCQ_BANK = [
    {
        "q": "Tick mark the right statement regarding contusions:",
        "opts": {"A": "Contusions are easily occurring in males", 
                 "B": "On cutting over it, blood is extravascular and is not washable",
                 "C": "It is caused by sharp instrument",
                 "D": "Both A and C"},
        "ans": "B",
        "section": "Wounds",
        "topic": "Bruise (Contusion)"
    },
    {
        "q": "Regarding post mortem appearance of heat stroke, which is the WRONG statement?",
        "opts": {"A": "Rigor mortis is delayed",
                 "B": "The body temperature may continue to rise after death",
                 "C": "Venous congestion is marked in all organs",
                 "D": "Both B and C"},
        "ans": "C",
        "section": "Thanatology",
        "topic": "Sudden Death"
    },
    {
        "q": "Tick mark the right statement:",
        "opts": {"A": "Extravasation of blood into tissue is hypostasis",
                 "B": "Destruction of superficial layer of the skin is abrasion",
                 "C": "Rope mark is an impact abrasion",
                 "D": "All of the above"},
        "ans": "D",
        "section": "Wounds",
        "topic": "Abrasion"
    },
    {
        "q": "The causative instrument of the fissure fracture is:",
        "opts": {"A": "Heavy blunt instrument with wide striking surface area and low momentum",
                 "B": "Heavy blunt instrument with wide striking surface area and high momentum",
                 "C": "Heavy blunt instrument with localised striking surface area and low momentum",
                 "D": "None of the above"},
        "ans": "B",
        "section": "Head Injuries",
        "topic": "Skull Fractures"
    },
    {
        "q": "Healing of the fissure fracture is by:",
        "opts": {"A": "Calcified callus",
                 "B": "Fibrous membrane",
                 "C": "Both A and B",
                 "D": "None of the above"},
        "ans": "C",
        "section": "Head Injuries",
        "topic": "Skull Fractures"
    },
    {
        "q": "Tick mark the right answer about violent asphyxia:",
        "opts": {"A": "External obstruction of mouth and nose is called choking asphyxia",
                 "B": "Internal obstruction of respiratory passages is called smothering asphyxia",
                 "C": "External pressure on the neck by hands is called throttling asphyxia",
                 "D": "All of the above"},
        "ans": "D",
        "section": "Asphyxia & Drowning",
        "topic": "Stages of Asphyxia"
    },
    {
        "q": "A blunt force on the skull may cause the following types of fractures EXCEPT:",
        "opts": {"A": "Fissure fracture",
                 "B": "Chipped fracture",
                 "C": "Depressed fracture",
                 "D": "Comminuted fracture"},
        "ans": "B",
        "section": "Head Injuries",
        "topic": "Skull Fractures"
    },
    {
        "q": "Grazes are injuries produced by:",
        "opts": {"A": "Pressure by blunt impact force",
                 "B": "Friction with sharp objects as pin",
                 "C": "Moving a sharp instrument as knife",
                 "D": "Friction of the skin with a large surface of a rough object"},
        "ans": "D",
        "section": "Wounds",
        "topic": "Abrasion"
    },
    {
        "q": "Extradural hemorrhage is due to rupture of:",
        "opts": {"A": "Middle meningeal artery",
                 "B": "Superior sagittal sinus",
                 "C": "Emissary veins",
                 "D": "All of the above"},
        "ans": "A",
        "section": "Head Injuries",
        "topic": "Brain Injuries"
    },
    {
        "q": "Post-mortem greenish discoloration of the skin is due to:",
        "opts": {"A": "Sulphmethaemoglobin",
                 "B": "Oxyhaemoglobin",
                 "C": "Reduced haemoglobin",
                 "D": "None of the above"},
        "ans": "A",
        "section": "Thanatology",
        "topic": "Putrefaction"
    },
    {
        "q": "Human hair shows which of the following?",
        "opts": {"A": "Regular cuticle, narrow cortex, narrow medulla",
                 "B": "Regular cuticle, narrow cortex, broad medulla",
                 "C": "Usually cortex only",
                 "D": "B and C"},
        "ans": "D",
        "section": "Identification",
        "topic": "Hair Examination"
    },
    {
        "q": "Hair shows a healthy root with ruptured sheath when:",
        "opts": {"A": "Fallen by itself",
                 "B": "Pulled by force",
                 "C": "Cut by a sharp instrument",
                 "D": "Injured by a rough blunt object"},
        "ans": "B",
        "section": "Identification",
        "topic": "Hair Examination"
    },
    {
        "q": "All soft tissues of the dead body are transformed into liquid substances after:",
        "opts": {"A": "One week",
                 "B": "Two weeks",
                 "C": "One month",
                 "D": "Six months"},
        "ans": "C",
        "section": "Thanatology",
        "topic": "Putrefaction"
    },
    {
        "q": "Which of the following is NOT a classical sign of asphyxia?",
        "opts": {"A": "Cyanosis",
                 "B": "Petechial hemorrhages",
                 "C": "Rigor mortis",
                 "D": "Pulmonary edema"},
        "ans": "C",
        "section": "Asphyxia & Drowning",
        "topic": "Stages of Asphyxia"
    },
    {
        "q": "Thermal injury with charring of tissues occurs at temperature above:",
        "opts": {"A": "60°C",
                 "B": "65°C",
                 "C": "75°C",
                 "D": "90°C"},
        "ans": "C",
        "section": "Physical Injuries",
        "topic": "Thermal Injury (Burns)"
    },
    {
        "q": "Death certificate should be issued EXCEPT in case of:",
        "opts": {"A": "Sudden death",
                 "B": "Death from natural causes after medical attendance",
                 "C": "Suspicious death",
                 "D": "Death after medical treatment for known disease"},
        "ans": "C",
        "section": "Thanatology",
        "topic": "Death Certification"
    },
    {
        "q": "Rigor mortis begins usually after:",
        "opts": {"A": "15 minutes of death",
                 "B": "2-6 hours of death",
                 "C": "12-24 hours of death",
                 "D": "24-36 hours of death"},
        "ans": "B",
        "section": "Thanatology",
        "topic": "Rigor Mortis"
    },
    {
        "q": "Cadaveric spasm is different from rigor mortis in that it:",
        "opts": {"A": "Occurs immediately after death",
                 "B": "Is localized",
                 "C": "Both A and B",
                 "D": "Neither A nor B"},
        "ans": "C",
        "section": "Thanatology",
        "topic": "Cadaveric Spasm"
    },
    {
        "q": "In case of drowning, the condition of the body is best identified by:",
        "opts": {"A": "Pallor mortis",
                 "B": "Rigor mortis",
                 "C": "Livor mortis (pink coloration)",
                 "D": "Hypostasis"},
        "ans": "C",
        "section": "Asphyxia & Drowning",
        "topic": "Drowning"
    },
    {
        "q": "Fabricated wounds are produced by:",
        "opts": {"A": "Blunt trauma",
                 "B": "Sharp trauma",
                 "C": "Self-infliction by victim",
                 "D": "Environmental friction"},
        "ans": "C",
        "section": "Wounds",
        "topic": "Fabricated Wound"
    },
    {
        "q": "The most reliable method for identification of dead persons is:",
        "opts": {"A": "Dental records",
                 "B": "Fingerprints",
                 "C": "DNA analysis",
                 "D": "Facial features"},
        "ans": "C",
        "section": "Identification",
        "topic": "Methods of Identification"
    },
    {
        "q": "Which of the following is a medicolegal report for living person?",
        "opts": {"A": "Postmortem examination",
                 "B": "Ante-mortem wound examination",
                 "C": "Injury report",
                 "D": "B and C"},
        "ans": "D",
        "section": "Medicolegal Topics",
        "topic": "Blood Examination"
    },
    {
        "q": "Road traffic accidents (RTA) require medicolegal examination EXCEPT:",
        "opts": {"A": "When there is injury",
                 "B": "When there is death",
                 "C": "When there is property damage only",
                 "D": "When police is involved"},
        "ans": "C",
        "section": "Medicolegal Topics",
        "topic": "Road Traffic Accidents (RTA)"
    },
    {
        "q": "Judicial hanging is characterized by which of the following?",
        "opts": {"A": "Knot on the side of neck",
                 "B": "Knot at back of neck",
                 "C": "Knot under chin",
                 "D": "Knot anywhere around neck"},
        "ans": "B",
        "section": "Asphyxia & Drowning",
        "topic": "Hanging"
    },
    {
        "q": "A penetrating wound is best described as:",
        "opts": {"A": "A wound caused by a blunt object",
                 "B": "A wound that pierces through skin and underlying tissues",
                 "C": "A wound that scratches the surface only",
                 "D": "A wound caused by friction"},
        "ans": "B",
        "section": "Wounds",
        "topic": "Penetrating Wound"
    },
    {
        "q": "Which burn classification represents full thickness burns?",
        "opts": {"A": "First degree",
                 "B": "Second degree",
                 "C": "Third degree",
                 "D": "Fourth degree"},
        "ans": "C",
        "section": "Physical Injuries",
        "topic": "Thermal Injury (Burns)"
    },
    {
        "q": "Hypostasis (livor mortis) appears after:",
        "opts": {"A": "30 minutes",
                 "B": "1-2 hours",
                 "C": "6-8 hours",
                 "D": "24 hours"},
        "ans": "B",
        "section": "Thanatology",
        "topic": "Hypostasis (Postmortem Lividity)"
    },
    {
        "q": "Which fracture occurs due to sudden blow to the skull?",
        "opts": {"A": "Linear fracture",
                 "B": "Depressed fracture",
                 "C": "Basilar fracture",
                 "D": "All of the above"},
        "ans": "D",
        "section": "Head Injuries",
        "topic": "Skull Fractures"
    },
    {
        "q": "The best indicator of the time of death is:",
        "opts": {"A": "Rigor mortis",
                 "B": "Hypostasis",
                 "C": "Body temperature (algor mortis)",
                 "D": "None of the above"},
        "ans": "C",
        "section": "Thanatology",
        "topic": "Death"
    },
    {
        "q": "Child abuse indicators include ALL EXCEPT:",
        "opts": {"A": "Repeated injuries at different healing stages",
                 "B": "Injuries inconsistent with history",
                 "C": "Multiple injuries in protected areas",
                 "D": "Accidental injuries during play"},
        "ans": "D",
        "section": "Medicolegal Topics",
        "topic": "Child Abuse"
    },
    {
        "q": "Sexual offences examination should include EXCEPT:",
        "opts": {"A": "Collection of semen samples",
                 "B": "Examination of genital injuries",
                 "C": "Blood typing of victim",
                 "D": "Radiological examination of bones"},
        "ans": "D",
        "section": "Medicolegal Topics",
        "topic": "Sexual Offences"
    },
]

# ═══════════════════════════════════════════════════════════════
# TOXICOLOGY MCQ BANK (75 Questions)
# ═══════════════════════════════════════════════════════════════

TOXICOLOGY_MCQ_BANK = [
    {
        "q": "Which of the following is NOT a part of phase I biotransformation of toxicants?",
        "opts": {"A": "Oxidation",
                 "B": "Hydrolysis",
                 "C": "Reduction",
                 "D": "Glutathione conjugation"},
        "ans": "D",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Alcohol concentrated forms are more quickly absorbed than diluted forms.",
        "opts": {"A": "True",
                 "B": "False",
                 "C": "Depends on food intake",
                 "D": "Depends on alcohol type"},
        "ans": "B",
        "section": "Toxicology Basics",
        "topic": "Alcoholism"
    },
    {
        "q": "All of the following chemicals are poorly absorbed by activated charcoal EXCEPT:",
        "opts": {"A": "Boric acid",
                 "B": "Salicylic acid",
                 "C": "Ferrous sulfate",
                 "D": "Lithium salts"},
        "ans": "C",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Which of the following is NOT recommended in case of paraquat poisoning with stable condition?",
        "opts": {"A": "Charcoal administration",
                 "B": "Oxygen administration",
                 "C": "Washing of exposed skin",
                 "D": "Maintenance of open airway"},
        "ans": "B",
        "section": "Pesticide Toxicity",
        "topic": "Paraquat Poisoning"
    },
    {
        "q": "Early toxic manifestations of salicylate poisoning are due to action on which target organ?",
        "opts": {"A": "Otolaryngologic system",
                 "B": "Heart",
                 "C": "Liver",
                 "D": "Kidney"},
        "ans": "A",
        "section": "Medicinal Alkaloid Poisoning",
        "topic": "Salicylate Poisoning"
    },
    {
        "q": "Which of the following chelators is effective if administered orally?",
        "opts": {"A": "Succimer (Chemet)",
                 "B": "CaNa2-EDTA (Calcium Disodium Versenate)",
                 "C": "Dimercaprol (BAL)",
                 "D": "Deferoxamine"},
        "ans": "A",
        "section": "Heavy Metal Poisoning",
        "topic": "Lead Poisoning"
    },
    {
        "q": "A 39-year-old woman attempted suicide by taking fenthion. She became hypotensive with sialorrhea and generalized muscle fasciculation. The treatment must include:",
        "opts": {"A": "Good hydration, antibiotic and observation",
                 "B": "Decontamination, chelating agent and reassure",
                 "C": "Decontamination, atropine, pralidoxim and supportive therapy",
                 "D": "Reassure, antidepressant and psychiatric assessment"},
        "ans": "C",
        "section": "Pesticide Toxicity",
        "topic": "Pesticide Toxicity"
    },
    {
        "q": "A 49-year-old ingested 125g of fungicide containing 3.5% methoxyethylmercury chloride. For diagnosis you need all tests EXCEPT:",
        "opts": {"A": "Urine mercury",
                 "B": "Whole-blood concentrations",
                 "C": "Hair analysis",
                 "D": "Stool analysis"},
        "ans": "D",
        "section": "Heavy Metal Poisoning",
        "topic": "Mercury Poisoning"
    },
    {
        "q": "A victim of heavy metal poisoning has an odor of garlic on his breath. The most probable cause is:",
        "opts": {"A": "Lead",
                 "B": "Zinc",
                 "C": "Arsenic",
                 "D": "Mercury"},
        "ans": "C",
        "section": "Heavy Metal Poisoning",
        "topic": "Heavy Metal Poisoning"
    },
    {
        "q": "Which of the following is a TRUE statement?",
        "opts": {"A": "Pica refers solely to ingestion of lead-based substances",
                 "B": "Plumbism is more likely in children aged 1-5 years",
                 "C": "Acute lead poisoning can be detected in blood up to 40 days",
                 "D": "Chronic lead poisoning causes polycythemia"},
        "ans": "B",
        "section": "Heavy Metal Poisoning",
        "topic": "Lead Poisoning"
    },
    {
        "q": "Emesis with syrup of ipecac is contraindicated in:",
        "opts": {"A": "Coma",
                 "B": "Convulsions",
                 "C": "Absent gag reflex",
                 "D": "All of the above"},
        "ans": "D",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Activated charcoal acts by:",
        "opts": {"A": "Absorption",
                 "B": "Adsorption",
                 "C": "Filtration",
                 "D": "Neutralization"},
        "ans": "B",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Activated charcoal is EFFECTIVE in the following EXCEPT:",
        "opts": {"A": "Acetaminophen",
                 "B": "Barbiturates",
                 "C": "Methyl alcohol",
                 "D": "Theophylline"},
        "ans": "C",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "The following affect absorption of poison EXCEPT:",
        "opts": {"A": "Dose of poison",
                 "B": "State of poison",
                 "C": "Color of poison",
                 "D": "Solubility of poison"},
        "ans": "C",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Cyanide poisoning is most rapidly fatal when the poison is placed in:",
        "opts": {"A": "High acidity medium",
                 "B": "Low acidity medium",
                 "C": "Non-acidic medium",
                 "D": "Neutral pH"},
        "ans": "B",
        "section": "Corrosive Poisoning",
        "topic": "Cyanide Poisoning"
    },
    {
        "q": "The most rapid form of poison is:",
        "opts": {"A": "Solid",
                 "B": "Gas",
                 "C": "Powder",
                 "D": "Solution"},
        "ans": "B",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Best method for barbiturate treatment is:",
        "opts": {"A": "Gradual withdrawal",
                 "B": "Abrupt withdrawal",
                 "C": "Use of antibodies",
                 "D": "Psychiatric drugs"},
        "ans": "A",
        "section": "Drug Abuse and Dependence",
        "topic": "Barbiturates"
    },
    {
        "q": "Nalini test is used for the diagnosis of:",
        "opts": {"A": "Amphetamine",
                 "B": "Alcohol",
                 "C": "Cocaine",
                 "D": "Opioids"},
        "ans": "C",
        "section": "Drug Abuse and Dependence",
        "topic": "Cocaine Toxicity"
    },
    {
        "q": "The most common complication of cocaine abuse by sniffing is:",
        "opts": {"A": "Death",
                 "B": "Cerebral hemorrhage",
                 "C": "Nasal septum perforation",
                 "D": "Heart failure"},
        "ans": "C",
        "section": "Drug Abuse and Dependence",
        "topic": "Cocaine Toxicity"
    },
    {
        "q": "Morphine dependence is characterized by:",
        "opts": {"A": "Constricted pupils",
                 "B": "Constipation",
                 "C": "Mask-like face",
                 "D": "Visual hallucinations"},
        "ans": "B",
        "section": "Drug Abuse and Dependence",
        "topic": "Opioid Toxicity"
    },
    {
        "q": "Cocaine dependence is best characterized by:",
        "opts": {"A": "Jaundice",
                 "B": "Tremor",
                 "C": "Mask-like face",
                 "D": "Tactile hallucinations"},
        "ans": "D",
        "section": "Drug Abuse and Dependence",
        "topic": "Cocaine Toxicity"
    },
    {
        "q": "The most common complication of alcohol is:",
        "opts": {"A": "Pleuritis",
                 "B": "Liver cirrhosis",
                 "C": "Gastritis",
                 "D": "Pancreatitis"},
        "ans": "B",
        "section": "Drug Abuse and Dependence",
        "topic": "Alcoholism"
    },
    {
        "q": "An idiosyncratic drug reaction is:",
        "opts": {"A": "Normal response",
                 "B": "Anaphylactic reaction",
                 "C": "Unexpected response to a drug",
                 "D": "Predictable side effect"},
        "ans": "C",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "The most serious complication of solvent abuse is:",
        "opts": {"A": "Coma",
                 "B": "Pleuritis",
                 "C": "Liver cirrhosis",
                 "D": "CNS damage"},
        "ans": "D",
        "section": "Drug Abuse and Dependence",
        "topic": "Volatile Substance Poisoning"
    },
    {
        "q": "Which of the following is hepatotoxic?",
        "opts": {"A": "Alcohol",
                 "B": "Cyanide",
                 "C": "Amphetamine",
                 "D": "Cocaine"},
        "ans": "A",
        "section": "Drug Abuse and Dependence",
        "topic": "Alcoholism"
    },
    {
        "q": "Carbon monoxide poisoning manifests with:",
        "opts": {"A": "Cherry-red livor mortis",
                 "B": "Pale livor mortis",
                 "C": "Purple livor mortis",
                 "D": "Green livor mortis"},
        "ans": "A",
        "section": "Corrosive Poisoning",
        "topic": "Carbon Monoxide (CO) Poisoning"
    },
    {
        "q": "Which of the following does NOT cause cyanosis?",
        "opts": {"A": "Carbon monoxide",
                 "B": "Cyanide",
                 "C": "Arsenic",
                 "D": "Strychnine"},
        "ans": "D",
        "section": "Toxicology Basics",
        "topic": "Introduction to Toxicology"
    },
    {
        "q": "Pesticide poisoning with cholinesterase inhibition causes:",
        "opts": {"A": "Mydriasis",
                 "B": "Miosis",
                 "C": "Keratitis",
                 "D": "Blindness"},
        "ans": "B",
        "section": "Pesticide Toxicity",
        "topic": "Pesticide Toxicity"
    },
    {
        "q": "Which chelator is used for lead poisoning in children?",
        "opts": {"A": "EDTA",
                 "B": "Succimer",
                 "C": "BAL",
                 "D": "Penicillamine"},
        "ans": "B",
        "section": "Heavy Metal Poisoning",
        "topic": "Lead Poisoning"
    },
    {
        "q": "Amphetamine abuse causes all EXCEPT:",
        "opts": {"A": "Tachycardia",
                 "B": "Mydriasis",
                 "C": "Hyperthermia",
                 "D": "Bradypnea"},
        "ans": "D",
        "section": "Drug Abuse and Dependence",
        "topic": "Amphetamine Toxicity"
    },
]

# Function to get random questions
def get_random_forensic_mcqs(count=30):
    """Return random Forensic MCQs"""
    import random
    return random.sample(FORENSIC_MCQ_BANK, min(count, len(FORENSIC_MCQ_BANK)))

def get_random_toxicology_mcqs(count=30):
    """Return random Toxicology MCQs"""
    import random
    return random.sample(TOXICOLOGY_MCQ_BANK, min(count, len(TOXICOLOGY_MCQ_BANK)))

def get_mixed_mcqs(forensic_count=30, toxicology_count=30):
    """Return mixed Forensic & Toxicology MCQs"""
    import random
    forensic = random.sample(FORENSIC_MCQ_BANK, min(forensic_count, len(FORENSIC_MCQ_BANK)))
    toxicology = random.sample(TOXICOLOGY_MCQ_BANK, min(toxicology_count, len(TOXICOLOGY_MCQ_BANK)))
    return forensic + toxicology
