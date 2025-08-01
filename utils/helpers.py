# utils/helpers.py
import re
import unicodedata
from datetime import datetime
from html import unescape
import dash_bootstrap_components as dbc
from dash import html

# ========================
# RENOMEAR CAMPOS, EXCLUSÕES E ORDENS
# ========================

RENOMEAR_CAMPOS = {
    "acoestomadas": "Ações Tomadas",
    "aprovadorprojetocliente": "Aprovador (Cliente)",
    "comentariosadicionais": "Comentários Adicionais",
    "complexidadelist": "Complexidade",
    "coordenadorprojetoscliente": "Coordenador (Cliente)",
    "cronogramaprojeto": "Cronograma",
    "criticidade": "Criticidade",
    "dataliberadahomologacao": "Data Homologação",
    "datainicialentregaprojeto": "Data Inicial Entrega",
    "datapausadopelocliente": "Data Pausa Cliente",
    "datapendentecliente": "Data Pendente Cliente",
    "datafinalgarantia": "Data Final Garantia",
    "detalhesproblemasprojeto": "Detalhes do Problema",
    "escopoprojeto": "Escopo",
    "envolveqa": "Envolve QA",
    "faseprojeto": "Fase do Projeto",
    "horasconsumidasreal": "Horas Consumidas",
    "horasvendidas": "Horas Vendidas",
    "keyusercliente": "Key User",
    "moivopausacliente": "Motivo Pausa Cliente",
    "motivoestouroprojeto": "Motivo Estouro",
    "numeroproposta": "N° Proposta",
    "porcentagementrega": "%",
    "principaispontosatencao": "Pontos de Atenção",
    "projetoatrasado": "Projeto Atrasado",
    "proximospassos": "Próximos Passos",
    "responsavelcliente": "Responsável",
    "custom.datainicialentregaprojeto": "Data Fim Original",    
    "responsaveltecnico": "Técnico",
    "statusprojeto": "Status do Projeto",
    "statushoras": "Status Horas",
    "microsoft.vsts.scheduling.targetdate": "Data Fim",
    "custom.dataliberadahomologacao": "Data Homologação",
    "system.assignedto": "PMO",
    "system.state": "Status",
    "system.title": "Projeto",
    "custom.aprovadorprojetocliente": "Aprovador",
    "custom.keyusercliente": "Key User",
    "emfasedeencerramentotimee": "Em Fase de Encerramento",
    "pausetime": "Data de Parada",
    "requestclientenome": "Cliente",
    "requestcontatocliente": "Contato do Cliente",
    "requestdatasolicitadacliente": "Data Solicitada Pelo Cliente",
    "requestidcrm": "ID CRM",
    "requestsolicitanteinterno": "Solicitante Interno",
    "starttime": "Data de Início"
}

CAMPOS_EXCLUIDOS = {
    "horasprojeto", "horasconsumidasreal", "statushoras", "saldohoras", "detalhesforaescopo",
    "liberahorasautomatica", "qtdreplamejamento", "criticidade", "envolveqa",
    "complexidadelist", "datadiscussion", "responsaveldiscussion", "situacaopendentelist",
    "statusprojeto", "porcentagementrega", "datafinalgarantia", "motivoestouroprojeto", "niveldecobranca"
}

CAMPOS_STATUS_REPORT = [
    "statusreport", "objetivo", "principaispontosatencao",
    "acoestomadas", "proximospassos", "comentariosadicionais"
]

ORDEM_PRIORITARIA = [
    "Horas Vendidas", "Técnico", "N° Proposta", "Responsável", "Key User"
]

STATUS_CARDS_COLORS = {
    "Em Fase de Encerramento": "#8B00FF",
    "Em Garantia": "#0000FF",
    "Em Homologacao": "#808080",
    "Parado pelo Cliente": "#FFFF00",
    "Problemas": "#FF0000",
    "Problemas em Fase Crítica": "#8B0000",
    "New": "#90EE90"
}

FAROIS_CARDS_COLORS = {
    "Sem Problema": "#008000",
    "Com Problema": "#FFD700",
    "Problema Crítico": "#FF0000",
    "Indefinido": "#D3D3D3"
}

STATUS_MAPEAMENTO = {
    "Projeto em Fase Crítica": "Projeto Em Fase Crítica",
    "Projeto em Fase Critica": "Projeto Em Fase Crítica",
    "Resolved": "Em Fase de Encerramento",
    "Projeto Em Planejamento": "Em Planejamento",
    "Projeto Em Andamento": "Em Andamento",
    "Projeto Em Homologação": "Em Homologação",
    "Projeto Em Fase de Encerramento": "Em Fase de Encerramento",
    "Projeto Pausado pelo Cliente": "Pausado pelo Cliente"
}

# ========================
# MAPEAMENTO DE AREA PATH POR CLIENTE
# ========================

AREA_PATHS = {
    "arteb": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\ARTEB",
    "aurora": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\AURORA",
    "belliz": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\BELLIZ",
    "blanver": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\BLANVER",
    "camil": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\CAMIL ALIMENTOS",
    "casa giacomo": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\CASA GIACOMO",
    "combio": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\COMBIO",
    "consigaz": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\CONSIGAZ",
    "delivoro": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\DELIVORO",
    "diebold": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\DIEBOLD",
    "forza maquina": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\FORZA MAQUINA",
    "fuchs": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\FUCHS",
    "integrada": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\INTEGRADA",
    "liotecnica": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\LIOTECNICA",
    "lorenzetti": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\LORENZETTI",
    "moinho paulista": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\MOINHO PAULISTA",
    "ntt data business": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\NTT DATA BUSINESS",
    "plascar": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\PLASCAR",
    "procurement compass": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\PROCUREMENT COMPASS",
    "quali it": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\QUALI IT",
    "qualiit": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\QUALIIT",
    "santa colomba": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\SANTA COLOMBA",
    "utc": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\UTC",

    # Clientes que não estão na lista acima
    "brinks": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\BRINKS",
    "dislub": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\DISLUB",
    "petronac": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\PETRONAC",
    "ecopistas": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\ECOPISTAS",
    "copagaz": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\COPAGAZ",
    "gpa": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\GPA",
    "ale": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\ALE COMBUSTÍVEIS",
    "supergasbras": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\SUPERGASBRAS",
    "tulipa": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\TULIPA COMBUSTÍVEIS",
    "iberia": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\IBÉRIA COMBUSTÍVEIS",
    "berlan": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\BERLAN",
    "brmania": "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos\\Cliente\\BR MANIA"
}

# ========================
# MAPEAMENTO DE DOMÍNIO POR CLIENTE
# ========================

DOMINIO_PARA_CLIENTE = {
    "ale.com.br": "ale",
    "arteb.com.br": "arteb",
    "aurora.com.br": "aurora",
    "belliz.com.br": "belliz",
    "berlan.com.br": "berlan",
    "blanver.com.br": "blanver",
    "brinks.com.br": "brinks",
    "brmania.com.br": "brmania",
    "camil.com.br": "camil",
    "casagiacomo.com.br": "casa giacomo",
    "combio.com.br": "combio",
    "consigaz.com.br": "consigaz",
    "copagaz.com.br": "copagaz",
    "delivoro.com.br": "delivoro",
    "diebold.com.br": "diebold",
    "dislub.com.br": "dislub",
    "ecopistas.com.br": "ecopistas",
    "forzamaquina.com.br": "forza maquina",
    "fuchs.com": "fuchs",
    "gpa.com.br": "gpa",
    "iberia.com.br": "iberia",
    "integrada.coop.br": "integrada",
    "liotecnica.com.br": "liotecnica",
    "lorenzetti.com.br": "lorenzetti",
    "moinhopaulista.com.br": "moinho paulista",
    "nttdata.com.br": "ntt data business",
    "petronac.com.br": "petronac",
    "plascar.com.br": "plascar",
    "procurementcompass.com.br": "procurement compass",
    "qualiit.com.br": "quali it",
    "santacolomba.com.br": "santa colomba",
    "supergasbras.com.br": "supergasbras",
    "tulipa.com.br": "tulipa",
    "utc.com.br": "utc"
}


# ========================
# FUNÇÕES DE NORMALIZAÇÃO E UTILITÁRIOS
# ========================

def normalize_field_key(key):
    key = unicodedata.normalize('NFKD', key).encode('ASCII', 'ignore').decode('utf-8')
    key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
    key = key.replace('_', '')

    guid_mapping = {
        "437a562d-eac7-4d78-ae5f-c96c91590d98": "numeroproposta",
        "82489798-d409-4a56-aa0b-d1ddb37463db": "responsaveltecnico",
        "861f1dd7-10ab-430e-b2e6-cb3b6004bec1": "responsavelcliente",
    }
    return guid_mapping.get(key, key)

def deduplicar_campos(campos: dict) -> dict:
    resultado = {}
    chaves_exibidas = {}

    for chave, valor in campos.items():
        chave_normalizada = normalize_field_key(chave)
        nome_final = RENOMEAR_CAMPOS.get(chave_normalizada, chave_normalizada)

        if nome_final in resultado:
            if str(resultado[nome_final]).strip() not in ["", "0", "None", "null"]:
                continue

        if str(valor).strip() in ["", "None", "null"]:
            continue

        resultado[nome_final] = valor

    return resultado

def clean_html(raw_html):
    if not raw_html:
        return ""

    if "<" not in raw_html and ">" not in raw_html:
        return limpar_valor(raw_html)

    text = re.sub(r'</?(?:p|div)\b[^>]*>', '\n', raw_html, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^<]+?>', '', unescape(text))
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()

def format_datetime(dt_str):
    if not dt_str or str(dt_str).lower() in ['none', 'null', '']:
        return "--/--/----"
    try:
        dt_str = dt_str.split("+")[0].split("Z")[0].strip()
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y",
            "%m/%d/%Y %H:%M", "%m/%d/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt).strftime("%d/%m/%Y")
            except:
                continue
        return dt_str
    except Exception:
        return dt_str

def horas_para_hhmm(valor):
    try:
        if isinstance(valor, str) and re.match(r'^\d{1,2}:\d{2}$', valor):
            return valor
        total_minutos = int(float(valor) * 60)
        horas = total_minutos // 60
        minutos = total_minutos % 60
        return f"{horas:02d}:{minutos:02d}"
    except:
        return "00:00"

def normalize_value(label, value):
    def format_datetime_com_hora(dt_str):
        if not dt_str or str(dt_str).lower() in ['none', 'null', '']:
            return "--/--/---- às --:--"
        try:
            dt_str = dt_str.split("+")[0].split("Z")[0].strip()
            formats = [
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    return dt.strftime("%d/%m/%Y às %H:%M")
                except:
                    continue
            return dt_str
        except Exception:
            return dt_str

    if isinstance(value, dict) and 'displayName' in value:
        return value['displayName']
    if isinstance(value, str) and value.startswith("<div"):
        return clean_html(value)
    if isinstance(value, str) and "\n" in value:
        return value.strip()
    if label.lower() in ["em fase de encerramento", "data de parada", "data de início"]:
        return format_datetime_com_hora(value)
    if label.lower() in ["data solicitada pelo cliente", "requestdatasolicitadacliente"]:
        return "Sim" if str(value).lower() == "true" else "Não"
    if any(keyword in label.lower() for keyword in ["data", "date"]):
        return format_datetime(str(value))
    if label in ["Criticidade", "Complexidade"]:
        return re.sub(r'^\d+\s*-\s*', '', str(value)).strip()
    if label.startswith(("Horas", "Saldo")):
        return horas_para_hhmm(value)
    if label == "Existe Pendência":
        texto = str(value).split("-")[-1] if "-" in str(value) else str(value)
        return texto.replace("Pendencia", "Pendência")
    return str(value)

def limpar_valor(valor, padrao=""):
    if not valor or not isinstance(valor, str):
        return padrao

    texto = valor.replace("\r", "").strip()
    linhas = texto.splitlines()

    resultado = []
    paragrafo = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            if paragrafo:
                resultado.append(" ".join(paragrafo).strip())
                paragrafo = []
            resultado.append("")
        else:
            paragrafo.append(linha)

    if paragrafo:
        resultado.append(" ".join(paragrafo).strip())

    while "" in resultado and resultado.count("") > 1:
        i = resultado.index("")
        if i + 1 < len(resultado) and resultado[i + 1] == "":
            resultado.pop(i)
        else:
            break

    return "\n\n".join(resultado).strip()

def extrair_comentario_formatado(comentario: str) -> str:
    comentario = comentario.strip()

    if "\t" in comentario:
        partes = comentario.split("\t")
        if len(partes) >= 3:
            data = partes[0].strip()
            corpo = "\n".join(p.strip() for p in partes[1:-1])
            responsavel = partes[-1].strip()
            return f"{data}\n{corpo}\n{responsavel}"

    linhas = comentario.splitlines()
    linhas = [linha.strip() for linha in linhas if linha.strip()]

    if len(linhas) == 1:
        return linhas[0]

    if len(linhas) == 2:
        return f"{linhas[0]}\n{linhas[1]}"

    data = linhas[0]
    responsavel = linhas[-1] if "responsável" in linhas[-1].lower() or "responsavel" in linhas[-1].lower() else "Quali IT"
    corpo = "\n".join(linhas[1:-1]).strip()

    return f"{data}\n{corpo}\n{responsavel}"

def normalizar_status(status: str) -> str:
    status = limpar_valor(status, "").strip()
    return STATUS_MAPEAMENTO.get(status, status)

def gerar_filtros(features_df, prefixo):
    if features_df.empty:
        return html.Div("Nenhum filtro disponível.")

    filtros = {
        campo: sorted(features_df[campo].dropna().unique())
        for campo in features_df.columns
        if campo not in ["NumeroProposta", "Horas", "Projeto", "%", "Farol", "Situação", "KeyUser", "Aprovador", "Cliente", "DataHomologacao", "DataFim"]
    }

    return dbc.Accordion([
        dbc.AccordionItem([
            html.P(
                f"{valor} ({sum(features_df[filtro] == valor)})",
                id={"type": f"filtro-dinamico-{prefixo}", "campo": filtro, "valor": valor},
                style={
                    "cursor": "pointer",
                    "fontSize": "13px",
                    "color": STATUS_CARDS_COLORS.get(valor, "#198754"),
                    "marginBottom": "2px"
                }
            ) for valor in filtros[filtro]
        ], title=filtro, style={"fontSize": "13px"})
        for filtro in filtros
    ], start_collapsed=True, flush=True)

def get_card_class(status):
    mapa = {
        "Em Andamento": "verde-escuro",
        "Em Homologação": "azul",
        "Em Planejamento": "amarelo",
        "Pausado pelo Cliente": "cinza",
        "Em Fase de Encerramento": "roxo",
        "Projeto Em Fase Crítica": "vermelho",
        "New": "verde-claro",
    }
    cor = mapa.get(status, "preto")
    return f"card-hover card-borda-{cor}"

def get_card_class_farol(farol):
    farol_formatado = farol.lower().replace(" ", "-")
    return f"card-farol card-borda-{farol_formatado}"
