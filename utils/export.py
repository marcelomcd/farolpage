# utils/export.py
from utils.helpers import (
    clean_html, format_datetime, normalize_value,
    RENOMEAR_CAMPOS, normalize_field_key,
    CAMPOS_EXCLUIDOS, CAMPOS_STATUS_REPORT, ORDEM_PRIORITARIA
)

from io import StringIO
from datetime import datetime
import re


def gerar_html_completo(work_item_data, revisions_data):
    buffer = StringIO()
    write = buffer.write

    fields = work_item_data.get("fields", {})
    wi_id = work_item_data.get("id", "-")
    titulo = fields.get("System.Title", "-")
    state = fields.get("System.State", "-")
    area = fields.get("System.AreaPath", "-")
    created = format_datetime(fields.get("System.CreatedDate", "-"))

    link = f"https://dev.azure.com/qualiit/Quali%20IT%20-%20Inova%C3%A7%C3%A3o%20e%20Tecnologia/_boards/board/t/Quali%20IT%20!%20Gestao%20de%20Projeto/Features?workitem={wi_id}"

    write("<html><head><meta charset='utf-8'><style>")
    write("""
        body {
            font-family: Arial;
            background-color: #0E1117;
            color: #FFFFFF;
            padding: 30px;
        }
        h1, h2, h3 { color: #FFFFFF; }
        a { color: #58a6ff; text-decoration: none; }
        .section { margin-bottom: 40px; }
        .campo { margin-bottom: 10px; }
        .label { font-weight: bold; color: #e3a008; }
        .comment { background-color: #161b22; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .responsavel { font-style: italic; color: #888; margin-top: 5px; }
        hr { border-top: 1px solid #30363d; margin: 25px 0; }
    """)
    write("</style></head><body>")

    write(f"<h1>{wi_id} - {titulo}</h1>")
    write(f"<p><a href='{link}' target='_blank'>🔗 Abrir no Azure DevOps</a></p>")
    write(f"<p><b>Estado:</b> {state} | <b>Área:</b> {area} | <b>Criado em:</b> {created}</p>")
    write("<hr>")

    write("<div class='section'><h2>📝 Status Report</h2>")
    for k, v in fields.items():
        if any(chave in k.lower() for chave in CAMPOS_STATUS_REPORT):
            key_label = RENOMEAR_CAMPOS.get(normalize_field_key(k.split('.')[-1]), k.split('.')[-1])
            valor = clean_html(str(v)).replace("\n", "<br>")
            write(f"<div class='campo'><span class='label'>{key_label}:</span> {valor}</div>")
    write("</div>")

    write("<div class='section'><h2>📋 Campos Personalizados</h2>")
    custom_fields = []
    for k, v in fields.items():
        if k.startswith(("Custom.", "Extension.")) and not any(chave in k.lower() for chave in CAMPOS_STATUS_REPORT):
            key_id = normalize_field_key(k.split('.')[-1])
            if key_id in CAMPOS_EXCLUIDOS:
                continue
            label = RENOMEAR_CAMPOS.get(key_id, k.split('.')[-1])
            valor = normalize_value(label, v)
            custom_fields.append((label, valor))

    prioritarios = [item for nome in ORDEM_PRIORITARIA for item in custom_fields if item[0] == nome]
    restantes = sorted([item for item in custom_fields if item[0] not in ORDEM_PRIORITARIA], key=lambda x: x[0].lower())
    todos = prioritarios + restantes

    for label, valor in todos:
        write(f"<div class='campo'><span class='label'>{label}:</span> {valor}</div>")
    write("</div>")

    write("<div class='section'><h2>💬 Comentários</h2>")
    comentarios = _extrair_comentarios(revisions_data)
    for data, texto, resp in comentarios:
        texto_html = texto.replace("\n", "<br>")
        write(f"<div class='comment'><b>{data}</b><br>{texto_html}<div class='responsavel'>Responsável: {resp}</div></div>")
    write("</div>")

    write("</body></html>")
    return buffer.getvalue()

def _extrair_comentarios(revisions):
    comentarios = []

    def normalize_date(data_str, fallback_year="2025"):
        data_str = data_str.replace(".", "/")
        parts = re.split(r"[/\\s]", data_str.strip())
        day = parts[0].zfill(2) if len(parts) >= 1 else "01"
        month = parts[1].zfill(2) if len(parts) >= 2 else "01"
        year = parts[2] if len(parts) >= 3 else fallback_year
        year = f"20{year}" if len(year) == 2 else year
        return f"{day}/{month}/{year}"

    def detect_responsavel(texto):
        texto = texto.strip().lower()
        if "quali it / consigaz" in texto:
            return "Quali IT / Consigaz"
        if "consigaz / quali it" in texto:
            return "Consigaz / Quali IT"
        if "quali it" in texto:
            return "Quali IT"
        if "consigaz" in texto:
            return "Consigaz"
        return "Responsável: N/A"

    def parse_table_style(text):
        linhas = [l.strip() for l in text.split('\n') if '|' in l and not l.startswith('|---')]
        for linha in linhas:
            cols = [col.strip().strip('*') for col in linha.split('|') if col.strip()]
            if len(cols) == 3:
                data = normalize_date(cols[0])
                comentario = cols[1]
                responsavel = detect_responsavel(cols[2])
                comentarios.append((data, comentario, responsavel))

    def parse_block_style(text, fallback_year):
        blocos = re.split(r'(?=(?:^|\n)(\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?))', text.strip())
        blocos = [b.strip() for b in blocos if b.strip()]
        i = 0
        while i < len(blocos) - 1:
            data_raw = blocos[i]
            conteudo = blocos[i + 1]
            data = normalize_date(data_raw, fallback_year)
            linhas = [linha.strip() for linha in conteudo.split('\n') if linha.strip()]
            responsavel = detect_responsavel(linhas[-1]) if linhas else "Responsável: N/A"
            comentario = "\n".join(linhas[:-1]) if len(linhas) > 1 else conteudo
            comentarios.append((data, comentario.strip(), responsavel))
            i += 2

    for rev in revisions:
        hist = rev.get("fields", {}).get("System.History")
        if not hist:
            continue
        texto = clean_html(hist).strip()
        changed_date = format_datetime(rev.get("fields", {}).get("System.ChangedDate"))
        current_year = changed_date.split("/")[-1] if changed_date != "--/--/----" else "2025"
        if "|" in texto:
            parse_table_style(texto)
        else:
            parse_block_style(texto, fallback_year=current_year)

        seen = set()
    final = []
    for data, texto, resp in comentarios:
        key = (data, texto.strip(), resp)
        if key not in seen:
            seen.add(key)
            final.append((data, texto.strip(), resp))

    final.sort(
        key=lambda x: datetime.strptime(x[0], "%d/%m/%Y") if re.match(r"\d{2}/\d{2}/\d{4}", x[0])
        else datetime.min,
        reverse=True
    )

    return final