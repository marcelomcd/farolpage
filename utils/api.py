import requests
import base64
from cryptography.fernet import Fernet
from typing import Optional
from utils.helpers import AREA_PATHS

ENCRYPTION_KEY = 'l_McgngVLOzwP51Ml1YBkiI_HZE1PBpriFEcTSw7fCQ='
ENCRYPTED_PAT = 'gAAAAABoUDDucV2IdiH6e0EscS_GYdkTUZfVgVYfmIi4w6EuGAZIi6EDLNGbjPrEt1Vdzv26Z97wpJjn4m0qwvk9HFJ5tOVtOiVVpUV5XnV9voc2t3nQ6Vb1J-ewq1eNXM9gEeAFEAUU3sg84JOtEbxVS-TxzjqbDOFhX89VcaUj6sOshELfzf3KxgU-FSYkusKvf72ubp4Y'

fernet = Fernet(ENCRYPTION_KEY)
PAT = fernet.decrypt(ENCRYPTED_PAT.encode()).decode()

ORGANIZATION = "qualiit"
PROJECT = "Quali IT - Inovação e Tecnologia"
API_URL = f"https://dev.azure.com/{ORGANIZATION}"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode((':' + PAT).encode()).decode()
}

ALL_FEATURE_FIELDS = [
    "Custom.AcoesTomadas",
    "Custom.AprovadorProjetoCliente",
    "Custom.ComentariosAdicionais",
    "Custom.CoordenadorProjetosCliente",
    "Custom.CronogramaProjeto",
    "Custom.DataLiberadaHomologacao",
    "Custom.DataInicialEntregaProjeto",
    "Custom.EscopoProjeto",
    "Custom.FaseProjeto",
    "Custom.HorasVendidas",
    "Custom.KeyUserCliente",
    "Custom.MotivoEstouroProjeto",
    "Custom.NumeroProposta",
    "Custom.PorcentagemEntrega",
    "Custom.PrincipaisPontosAtencao",
    "Custom.ProjetoAtrasado",
    "Custom.ProximosPassos",
    "Custom.RequestClienteNome",
    "Custom.ResponsavelCliente",
    "Custom.ResponsavelTecnico",
    "Custom.StatusHoras",
    "Custom.StatusProjeto",
    "Microsoft.VSTS.Common.StateChangeDate",
    "Microsoft.VSTS.Scheduling.StartDate",
    "Microsoft.VSTS.Scheduling.TargetDate",
    "System.AreaPath",
    "System.AssignedTo",
    "System.Id",
    "System.State",
    "System.Title"
]

ALL_REQUEST_FIELDS = ALL_FEATURE_FIELDS

def get_work_item(wi_id):
    url = f"{API_URL}/{PROJECT}/_apis/wit/workitems/{wi_id}?api-version=7.0&$expand=all"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else None

def get_revisions(wi_id):
    url = f"{API_URL}/{PROJECT}/_apis/wit/workitems/{wi_id}/revisions?api-version=7.0"
    r = requests.get(url, headers=HEADERS)
    return r.json().get("value", []) if r.status_code == 200 else []

def get_all_features_by_cliente(cliente: Optional[str] = None, top: Optional[int] = None, force_admin: bool = False):
    if cliente and not force_admin:
        cliente = cliente.lower()
        path = AREA_PATHS.get(cliente)
        if not path:
            print(f"❌ Cliente não mapeado: {cliente}")
            return []

        area_path_filter = f"[System.AreaPath] UNDER '{path}'"
    else:
        # Admin ou usuário sem cliente específico → retorna tudo
        area_path_filter = "[System.AreaPath] UNDER 'Quali IT - Inovação e Tecnologia'"

    query = f"""
    SELECT [System.Id]
    FROM WorkItems
    WHERE
        {area_path_filter}
        AND [System.WorkItemType] = 'Feature'
    ORDER BY [System.ChangedDate] DESC
    """

    wiql_url = f"{API_URL}/{PROJECT}/_apis/wit/wiql?api-version=7.0"
    response = requests.post(wiql_url, headers=HEADERS, json={"query": query})

    if response.status_code != 200:
        print("❌ Erro WIQL:", response.status_code, response.text)
        return []

    all_ids = [item["id"] for item in response.json().get("workItems", [])]
    if not all_ids:
        return []

    ids = all_ids[:top] if top else all_ids
    batch_url = f"{API_URL}/{PROJECT}/_apis/wit/workitemsbatch?api-version=7.0"

    resultados = []
    lote = 200

    for i in range(0, len(ids), lote):
        batch_ids = ids[i:i + lote]
        batch_body = {
            "ids": batch_ids,
            "fields": ALL_FEATURE_FIELDS
        }
        batch_response = requests.post(batch_url, headers=HEADERS, json=batch_body)
        if batch_response.status_code == 200:
            resultados.extend(batch_response.json().get("value", []))
        else:
            print("❌ Erro no batch:", batch_response.status_code, batch_response.text)

    return resultados


def get_all_requests(top: Optional[int] = None):
    query = """
    SELECT [System.Id]
    FROM WorkItems
    WHERE
        [System.TeamProject] = 'Quali IT - Inovação e Tecnologia'
        AND [System.WorkItemType] = 'Request'
    ORDER BY [System.ChangedDate] DESC
    """
    
    wiql_url = f"{API_URL}/{PROJECT}/_apis/wit/wiql?api-version=7.0"
    response = requests.post(wiql_url, headers=HEADERS, json={"query": query})

    if response.status_code != 200:
        print("❌ Erro WIQL (Requests):", response.status_code, response.text)
        return []

    all_ids = [item["id"] for item in response.json().get("workItems", [])]
    if not all_ids:
        return []

    ids = all_ids[:top] if top else all_ids
    batch_url = f"{API_URL}/{PROJECT}/_apis/wit/workitemsbatch?api-version=7.0"

    resultados = []
    lote = 200

    for i in range(0, len(ids), lote):
        batch_ids = ids[i:i + lote]
        batch_body = {
            "ids": batch_ids,
            "fields": ALL_REQUEST_FIELDS
        }
        batch_response = requests.post(batch_url, headers=HEADERS, json=batch_body)
        if batch_response.status_code == 200:
            resultados.extend(batch_response.json().get("value", []))
        else:
            print("❌ Erro no batch (Requests):", batch_response.status_code, batch_response.text)

    return resultados
