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
from io import BytesIO

import pytz
from jinja2 import Environment, FileSystemLoader
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from xhtml2pdf import pisa

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


def _gerar_pdf(html: str) -> bytes:
    """Converte HTML em PDF usando xhtml2pdf e retorna os bytes."""
    buffer = BytesIO()
    pisa.CreatePDF(html.encode("utf-8"), dest=buffer)
    return buffer.getvalue()


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
    pdf_bytes = _gerar_pdf(html)

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
