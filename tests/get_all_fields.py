import requests
import base64
from cryptography.fernet import Fernet

ENCRYPTION_KEY = 'l_McgngVLOzwP51Ml1YBkiI_HZE1PBpriFEcTSw7fCQ='
ENCRYPTED_PAT = 'gAAAAABn4tZzAiYrOQHBD7oCUu9A_IS3pyHt0gVkd6izX-07JyP__wB4fpT7rSnpO9BH9whBG2is9hEf5UaEvoCfDxJzY8XgaMfnuFfD301zk5_Qjc0L7d3PyZxMCwb9sDJ7r0LiCpV89oOL5QJMqjjwYjFAp_IM_uDJDAg_o3fjXYw02XpvkDmEAgGJvvD1nwMFrstNav8C'
ORGANIZATION = "qualiit"
PROJECT = "Quali IT - Inovação e Tecnologia"
API_VERSION = "7.0"

fernet = Fernet(ENCRYPTION_KEY)
PAT = fernet.decrypt(ENCRYPTED_PAT.encode()).decode()

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode((':' + PAT).encode()).decode()
}

url = f"https://dev.azure.com/{ORGANIZATION}/_apis/wit/fields?api-version={API_VERSION}"
response = requests.get(url, headers=HEADERS)

if response.status_code == 200:
    campos = response.json().get("value", [])
    print("Total de campos encontrados:", len(campos))
    for campo in campos:
        print(f"{campo['referenceName']} - {campo['name']}")
else:
    print("Erro ao obter os campos:", response.status_code)
    print(response.text)
