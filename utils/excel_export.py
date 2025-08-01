import io
import pandas as pd
from datetime import datetime

def gerar_excel_status_report(df, cliente_nome="TODOS", is_admin=True):
    df = df.copy()
    df = df.drop(columns=["FarolTexto", "ID"], errors="ignore")

    if not is_admin:
        df = df.drop(columns=["Cliente"], errors="ignore")

    df = df.rename(columns={
        "NumeroProposta": "Nº de Proposta",
        "Horas": "Horas",
        "Projeto": "Projeto",
        "%": "%",
        "FarolIcone": "Farol",
        "Situação": "Situação",
        "Status": "Status",
        "Responsavel": "Responsável",
        "PMO": "PMO",
        "DataInicio": "Data de Início",
        "DataFimOriginal": "Data Fim Original",
        "DataHomologacao": "Data de Homologação",
        "DataFim": "Data Estimada",
        "KeyUser": "Key User",
        "Aprovador": "Aprovador",
        "Cliente": "Cliente"
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Status Report", index=False, startrow=4)
        workbook = writer.book
        worksheet = writer.sheets["Status Report"]

        titulo = f"Status Report ({cliente_nome}) - {datetime.now().strftime('%d/%m/%Y')}"
        merge_format = workbook.add_format({
            "bold": True, "font_size": 14,
            "align": "center", "valign": "vcenter",
            "fg_color": "#198754", "font_color": "white"
        })
        worksheet.merge_range(0, 0, 2, len(df.columns) - 1, titulo, merge_format)

        # Estilo padrão
        base_format = workbook.add_format({"align": "center", "valign": "vcenter", "text_wrap": True})
        for i in range(len(df.columns)):
            worksheet.set_column(i, i, 20, base_format)

        # Ajuste especial para coluna "Situação"
        if "Situação" in df.columns:
            col = df.columns.get_loc("Situação")
            worksheet.set_column(col, col, 50, base_format)

        # Cores para Farol
        if "Farol" in df.columns:
            farol_cores = {"🟢": "#28a745", "🟡": "#ffc107", "🔴": "#dc3545", "⚪": "#6c757d"}
            formatos = {
                icone: workbook.add_format({
                    "align": "center",
                    "valign": "vcenter",
                    "font_color": cor,
                    "bold": True,
                    "bg_color": "#ffffff",
                    "font_size": 20
                }) for icone, cor in farol_cores.items()
            }
            col_idx = df.columns.get_loc("Farol")
            for row_num, val in enumerate(df["Farol"], start=5):
                worksheet.write(row_num, col_idx, val, formatos.get(val, base_format))

    output.seek(0)
    return output
