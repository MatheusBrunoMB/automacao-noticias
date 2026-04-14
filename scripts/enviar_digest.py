"""
Script de digest semanal.
Executado pelo GitHub Actions toda segunda-feira às 08h BRT.
Compila notícias da semana, gera PDF + XLSX e envia por email.
"""

import json
import os
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO  # usado pelo openpyxl

import pytz
from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(__file__))
from fontes import CORES_CATEGORIA, ORDEM_CATEGORIAS
from utils import BRT, NOTICIAS_DIR, log_erro, log_info

DIGESTS_DIR = os.path.join(os.path.dirname(__file__), "..", "digests")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

GMAIL_REMETENTE = os.environ.get("GMAIL_REMETENTE", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
DESTINATARIOS_STR = os.environ.get("DESTINATARIOS", "")

# Cores de fill para Excel por prioridade
_EXCEL_CORES = {
    "Alto":  "FFCCCC",  # vermelho claro
    "Médio": "FFF9C4",  # amarelo claro
    "Baixo": "F5F5F5",  # cinza claro
}

MAX_POR_CATEGORIA = 10


def _carregar_noticias_semana() -> list:
    """Lê os JSONs dos últimos 7 dias e retorna lista mesclada sem duplicatas."""
    hoje = datetime.now(BRT).date()
    todas = {}
    for i in range(7):
        data = (hoje - timedelta(days=i)).strftime("%Y-%m-%d")
        caminho = os.path.join(NOTICIAS_DIR, f"{data}.json")
        if not os.path.exists(caminho):
            continue
        try:
            with open(caminho, encoding="utf-8") as f:
                noticias = json.load(f)
            for n in noticias:
                if n.get("id") and n["id"] not in todas:
                    todas[n["id"]] = n
        except Exception as e:
            log_erro(f"Erro ao ler {caminho}", e)
    return list(todas.values())


def _agrupar_por_categoria(noticias: list) -> dict:
    """
    Agrupa notícias por categoria, ordena cada grupo por prioridade e data,
    e limita a MAX_POR_CATEGORIA itens.
    """
    ordem_prio = {"Alto": 0, "Médio": 1, "Baixo": 2}
    grupos: dict = {cat: [] for cat in ORDEM_CATEGORIAS}

    for n in noticias:
        cat = n.get("categoria", "")
        if cat in grupos:
            grupos[cat].append(n)

    for cat in grupos:
        grupos[cat].sort(
            key=lambda x: (
                ordem_prio.get(x.get("prioridade", "Baixo"), 2),
                x.get("data_publicacao", ""),
            )
        )
        grupos[cat] = grupos[cat][:MAX_POR_CATEGORIA]

    return grupos


def _gerar_html(grupos: dict, semana_inicio: str, semana_fim: str, total: int) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("email_digest.html")
    return template.render(
        grupos=grupos,
        ordem_categorias=ORDEM_CATEGORIAS,
        cores_categoria=CORES_CATEGORIA,
        semana_inicio=semana_inicio,
        semana_fim=semana_fim,
        total_noticias=total,
    )


def _gerar_pdf(grupos: dict, semana_inicio: str, semana_fim: str, total: int) -> bytes:
    """Gera PDF do digest usando fpdf2 (puro Python, sem dependências de sistema)."""
    ordem_prio = {"Alto": 0, "Médio": 1, "Baixo": 2}
    icone_prio = {"Alto": "[ALTO]", "Médio": "[MEDIO]", "Baixo": "[BAIXO]"}
    cor_prio = {
        "Alto":  (229, 57, 53),
        "Médio": (249, 168, 37),
        "Baixo": (158, 158, 158),
    }

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # Cabeçalho
    pdf.set_fill_color(0, 48, 135)
    pdf.rect(0, 0, 210, 38, "F")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 10)
    pdf.cell(210, 8, "Digest Semanal de Noticias", align="C", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(210, 6, f"Contabilidade & Direito Tributario — {semana_inicio} a {semana_fim}", align="C", ln=True)
    pdf.cell(210, 6, f"Total: {total} noticias coletadas", align="C", ln=True)
    pdf.ln(12)

    pdf.set_text_color(0, 0, 0)

    for cat in ORDEM_CATEGORIAS:
        itens = grupos.get(cat, [])
        if not itens:
            continue

        # Título da categoria
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 9, f"  {cat}  ({len(itens)} noticias)", ln=True, fill=True)
        pdf.ln(3)

        for n in itens:
            prio = n.get("prioridade", "Baixo")
            r, g, b = cor_prio.get(prio, (158, 158, 158))

            # Badge de prioridade
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(r, g, b)
            pdf.cell(0, 5, icone_prio.get(prio, ""), ln=True)

            # Título
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(26, 26, 46)
            titulo = n.get("titulo", "")
            pdf.multi_cell(0, 5, titulo)

            # Fonte e data
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 5, f"{n.get('fonte', '')}  |  {n.get('data_publicacao', '')[:10]}", ln=True)

            # Resumo
            resumo = n.get("resumo", "")[:280]
            if resumo:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(70, 70, 70)
                pdf.multi_cell(0, 5, resumo)

            # Sugestão de pauta
            pauta = n.get("sugestao_pauta", "")
            if pauta:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(80, 80, 140)
                pdf.multi_cell(0, 5, f"Pauta: {pauta}")

            # URL
            pdf.set_font("Helvetica", "U", 8)
            pdf.set_text_color(0, 80, 200)
            url = n.get("url", "")
            if url:
                pdf.cell(0, 5, url[:90], ln=True, link=url)

            pdf.set_draw_color(220, 220, 220)
            pdf.line(15, pdf.get_y() + 2, 195, pdf.get_y() + 2)
            pdf.ln(6)
            pdf.set_text_color(0, 0, 0)

    return bytes(pdf.output())


def _gerar_xlsx(noticias: list) -> bytes:
    """Gera planilha Excel com duas abas: todas as notícias e pauta da semana."""
    wb = Workbook()

    cabecalhos = [
        "Prioridade", "Categoria", "Título", "Resumo",
        "Fonte", "Data", "URL", "Sugestão de Pauta",
    ]

    ordem_prio = {"Alto": 0, "Médio": 1, "Baixo": 2}
    noticias_ordenadas = sorted(
        noticias,
        key=lambda x: (
            ordem_prio.get(x.get("prioridade", "Baixo"), 2),
            x.get("data_publicacao", ""),
        ),
    )

    def _preencher_aba(ws, dados):
        # Cabeçalho
        ws.append(cabecalhos)
        for col_idx, _ in enumerate(cabecalhos, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1a1a2e")
            cell.alignment = Alignment(horizontal="center", wrap_text=True)

        # Dados
        for n in dados:
            row = [
                n.get("prioridade", ""),
                n.get("categoria", ""),
                n.get("titulo", ""),
                n.get("resumo", ""),
                n.get("fonte", ""),
                n.get("data_publicacao", "")[:10],
                n.get("url", ""),
                n.get("sugestao_pauta", ""),
            ]
            ws.append(row)
            prio = n.get("prioridade", "Baixo")
            fill_color = _EXCEL_CORES.get(prio, "FFFFFF")
            for col_idx in range(1, len(cabecalhos) + 1):
                cell = ws.cell(row=ws.max_row, column=col_idx)
                cell.fill = PatternFill("solid", fgColor=fill_color)
                cell.alignment = Alignment(wrap_text=True, vertical="top")

        # Ajusta largura das colunas
        larguras = [12, 14, 45, 55, 20, 12, 50, 60]
        for i, largura in enumerate(larguras, 1):
            ws.column_dimensions[get_column_letter(i)].width = largura

    # Aba 1: Todas as notícias
    ws1 = wb.active
    ws1.title = "Todas as Notícias"
    _preencher_aba(ws1, noticias_ordenadas)

    # Aba 2: Pauta da Semana (só Alto e Médio)
    ws2 = wb.create_sheet("Pauta da Semana")
    pauta = [n for n in noticias_ordenadas if n.get("prioridade") in ("Alto", "Médio")]
    _preencher_aba(ws2, pauta)

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _enviar_email(
    html_body: str,
    pdf_bytes: bytes,
    xlsx_bytes: bytes,
    assunto: str,
    destinatarios: list,
):
    """Envia o email com attachments via Gmail SMTP. Tenta até 3 vezes."""
    msg = MIMEMultipart("mixed")
    msg["From"] = GMAIL_REMETENTE
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = assunto

    # Parte alternativa (texto simples + HTML)
    alt = MIMEMultipart("alternative")
    texto_simples = "Digest semanal disponível. Abra este email em um cliente que suporte HTML."
    alt.attach(MIMEText(texto_simples, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    # Anexo PDF
    pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_part.add_header("Content-Disposition", "attachment", filename="digest_semanal.pdf")
    msg.attach(pdf_part)

    # Anexo XLSX
    xlsx_part = MIMEApplication(
        xlsx_bytes,
        _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    xlsx_part.add_header("Content-Disposition", "attachment", filename="pauta_semanal.xlsx")
    msg.attach(xlsx_part)

    for tentativa in range(1, 4):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(GMAIL_REMETENTE, GMAIL_APP_PASSWORD)
                smtp.sendmail(GMAIL_REMETENTE, destinatarios, msg.as_string())
            log_info(f"Email enviado com sucesso para {destinatarios}")
            return
        except Exception as e:
            log_erro(f"Tentativa {tentativa}/3 falhou", e)
            if tentativa < 3:
                time.sleep(5)

    raise RuntimeError("Falha ao enviar email após 3 tentativas.")


def main():
    log_info("Iniciando compilação do digest semanal")

    hoje = datetime.now(BRT).date()
    semana_inicio = (hoje - timedelta(days=6)).strftime("%d/%m/%Y")
    semana_fim = hoje.strftime("%d/%m/%Y")
    data_arquivo = hoje.strftime("%Y-%m-%d")

    noticias = _carregar_noticias_semana()
    log_info(f"Total de notícias carregadas: {len(noticias)}")

    if not noticias:
        log_info("Nenhuma notícia encontrada para a semana. Digest não enviado.")
        return

    grupos = _agrupar_por_categoria(noticias)
    total = sum(len(v) for v in grupos.values())

    # Gera artefatos
    log_info("Gerando HTML...")
    html = _gerar_html(grupos, semana_inicio, semana_fim, total)

    log_info("Gerando PDF...")
    pdf_bytes = _gerar_pdf(grupos, semana_inicio, semana_fim, total)

    log_info("Gerando planilha XLSX...")
    xlsx_bytes = _gerar_xlsx(noticias)

    # Salva arquivos localmente (commitados no repo como arquivo)
    os.makedirs(DIGESTS_DIR, exist_ok=True)
    with open(os.path.join(DIGESTS_DIR, f"{data_arquivo}_digest.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(DIGESTS_DIR, f"{data_arquivo}_digest.pdf"), "wb") as f:
        f.write(pdf_bytes)
    with open(os.path.join(DIGESTS_DIR, f"{data_arquivo}_pauta.xlsx"), "wb") as f:
        f.write(xlsx_bytes)
    log_info(f"Arquivos salvos em {DIGESTS_DIR}")

    # Envia email
    if not GMAIL_REMETENTE or not GMAIL_APP_PASSWORD or not DESTINATARIOS_STR:
        log_info("Credenciais de email não configuradas — email não enviado.")
        return

    destinatarios = [e.strip() for e in DESTINATARIOS_STR.split(",") if e.strip()]
    assunto = (
        f"[Digest Semanal] Notícias Contabilidade e Tributário "
        f"— {semana_inicio} a {semana_fim}"
    )
    _enviar_email(html, pdf_bytes, xlsx_bytes, assunto, destinatarios)
    log_info("Digest semanal concluído com sucesso.")


if __name__ == "__main__":
    main()
