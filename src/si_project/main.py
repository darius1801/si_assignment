#!/usr/bin/env python
import sys
import warnings

from si_project.crew import SiProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    # Lista extinsă de boli pentru generarea dataset-ului
    diseases = [
        #{'target_disease': 'tuberculosis'},
        #{'target_disease': 'migraine'},
        #{'target_disease': 'type 2 diabetes mellitus'},
        # {'target_disease': 'essential hypertension'},
        # {'target_disease': 'asthma'},
        # {'target_disease': 'coronary artery disease'},
        {'target_disease': 'rheumatoid arthritis'},
        {'target_disease': 'hypothyroidism'},
        {'target_disease': 'chronic obstructive pulmonary disease'},
        {'target_disease': 'alzheimer disease'},
        {'target_disease': 'parkinson disease'},
        {'target_disease': 'major depressive disorder'},
        {'target_disease': 'generalized anxiety disorder'},
        {'target_disease': 'schizophrenia'},
        {'target_disease': 'bipolar disorder'},
        {'target_disease': 'celiac disease'},
        {'target_disease': 'crohn disease'},
        {'target_disease': 'ulcerative colitis'},
        {'target_disease': 'multiple sclerosis'},
        {'target_disease': 'psoriasis'},
        {'target_disease': 'endometriosis'}
    ]

    try:
        import os
        import json
        
        output_file = 'medical_dataset.json'
        crew_instance = SiProject().crew()
        
        print(f"\n=== STARTING DATASET GENERATION FOR {len(diseases)} DISEASES ===")
        
        # Procesam boala cu boala si salvam imediat fiecare rezultat
        for idx, disease_input in enumerate(diseases):
            disease_name = disease_input['target_disease']
            print(f"\n[{idx+1}/{len(diseases)}] Se proceseaza: {disease_name}...")
            
            # Rulam workflow-ul CrewAI fix pentru aceasta boala
            result = crew_instance.kickoff(inputs=disease_input)
            
            # Citim dataset-ul curent
            existing_data = []
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
                        
            # Extragem datele Pydantic si adaugam la lista
            if hasattr(result, 'pydantic') and result.pydantic:
                data_dict = json.loads(result.pydantic.model_dump_json())
                existing_data.append(data_dict)
                
                # Rescriem instant fisierul cu noul item
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)
                    
                print(f"-> SALVAT IN JSON: {disease_name}. Total inregistrari curente: {len(existing_data)}")
            else:
                print(f"-> EROARE: Nu s-a putut parsa formatul final pentru {disease_name}.")
                
        print("\n=== DATASET GENERATION FULLY COMPLETED ===")
                
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "target_disease": "tuberculosis"
    }
    try:
        SiProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SiProject().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "target_disease": "tuberculosis"
    }

    try:
        SiProject().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
