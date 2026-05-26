import os
import json
import requests
from crewai.tools import tool

@tool("ICD11 Fetcher")
def fetch_icd11_disease_data(disease_name: str) -> str:
    """Apelează ICD-11 API pentru a extrage definiția unei boli pe baza numelui.
    Dacă nu există credențiale valide, returnează date mock (simulate)."""
    
    client_id = os.getenv("ICD_API_CLIENT_ID")
    client_secret = os.getenv("ICD_API_CLIENT_SECRET")
    
    # Fallback to mock data if no credentials
    if not client_id or not client_secret:
        return _mock_icd_response(disease_name)
    
    try:
        # 1. Get OAuth2 Token
        token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'icdapi_access',
            'grant_type': 'client_credentials'
        }
        
        token_response = requests.post(token_endpoint, data=payload, timeout=10)
        if token_response.status_code != 200:
            return f"Eroare autentificare ICD-11: {token_response.text}. Fallback to mock: {_mock_icd_response(disease_name)}"
            
        token = token_response.json().get('access_token')
        
        # 2. Search for the disease entity
        search_endpoint = f'https://id.who.int/icd/entity/search?q={disease_name}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'API-Version': 'v2'
        }
        
        search_response = requests.get(search_endpoint, headers=headers, timeout=10)
        if search_response.status_code != 200:
            return f"Eroare la căutare ICD-11: {search_response.text}"
            
        data = search_response.json()
        
        # Parse the top result
        if data.get('destinationEntities'):
            top_result = data['destinationEntities'][0]
            title = top_result.get('title', disease_name)
            code = top_result.get('theCode', 'N/A')
            
            # Since searching gives limited details, we return the title and code
            # and ask the agent to use it. Real API usage would follow the entity ID url
            # for full symptoms, but for this demo, the title and code are enough.
            result = {
                "title": title,
                "icd11_code": code,
                "definition": f"Clinical entity matching '{disease_name}' from ICD-11 API.",
                "api_match": True
            }
            return json.dumps(result)
        else:
            return f"No results found in ICD-11 API for {disease_name}. Fallback: {_mock_icd_response(disease_name)}"
            
    except Exception as e:
        return f"Exception in ICD11 API: {str(e)}. Fallback: {_mock_icd_response(disease_name)}"

def _mock_icd_response(disease_name: str) -> str:
    """Returns mock data for testing purposes."""
    mock_db = {
        "tuberculosis": {
            "title": "Tuberculosis of heart",
            "code": "1B12.0",
            "definition": "A disease of the heart caused by an infection with Mycobacterium tuberculosis.",
            "symptoms_referenced": ["chest pain", "fever", "night sweats", "fatigue"]
        },
        "migraine": {
            "title": "Migraine without aura",
            "code": "8A80.0",
            "definition": "A recurrent headache disorder manifesting in attacks lasting 4-72 hours.",
            "symptoms_referenced": ["unilateral headache", "pulsating pain", "nausea", "photophobia", "phonophobia"]
        }
    }
    
    key = disease_name.lower().strip()
    # Simple partial match
    for k, v in mock_db.items():
        if k in key or key in k:
            return json.dumps(v)
            
    # Default generic mock
    return json.dumps({
        "title": disease_name.title(),
        "code": "Unknown",
        "definition": f"Synthetic placeholder for {disease_name}.",
        "symptoms_referenced": ["pain", "discomfort", "fatigue"]
    })
