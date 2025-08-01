import requests
from utils.api import get_work_item

def test_get_work_item_mock(requests_mock):
    wi_id = "123"
    requests_mock.get(
        f"https://dev.azure.com/qualiit/Quali%20IT%20-%20Inovação%20e%20Tecnologia/_apis/wit/workitems/{wi_id}?api-version=7.0&$expand=all",
        json={"id": wi_id, "fields": {"System.Title": "Teste"}}
    )
    result = get_work_item(wi_id)
    assert result["fields"]["System.Title"] == "Teste" # type: ignore