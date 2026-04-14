import hashlib
import json
import re
import os
from datetime import datetime, timedelta

import pytz
from dateutil import parser as dateutil_parser

BRT = pytz.timezone("America/Sao_Paulo")
NOTICIAS_DIR = os.path.join(os.path.dirname(__file__), "..", "noticias")


def obter_data_hoje() -> str:
    """Retorna a data atual no fuso horário de Brasília (YYYY-MM-DD)."""
    return datetime.now(BRT).strftime("%Y-%m-%d")


def gerar_id(titulo: str, url: str) -> str:
    """Gera um ID único e determinístico a partir do título e URL."""
    conteudo = f"{titulo}{url}".encode("utf-8")
    return hashlib.sha256(conteudo).hexdigest()[:16]


def strip_html(texto: str) -> str:
    """Remove tags HTML e normaliza espaços em branco."""
    if not texto:
        return ""
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def formatar_data(data_str) -> str:
    """
    Tenta converter uma string de data (ou struct_time do feedparser) para
    o formato 'YYYY-MM-DD HH:MM:SS' no fuso de Brasília.
    Retorna a data/hora atual em BRT caso falhe.
    """
    agora = datetime.now(BRT).strftime("%Y-%m-%d %H:%M:%S")
    if not data_str:
        return agora
    try:
        # feedparser pode retornar um struct_time (time.struct_time)
        if hasattr(data_str, "tm_year"):
            import calendar
            ts = calendar.timegm(data_str)
            dt = datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(BRT)
        else:
            dt = dateutil_parser.parse(str(data_str))
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            dt = dt.astimezone(BRT)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return agora


def carregar_ids_existentes(dias: int = 30) -> set:
    """
    Lê os JSONs dos últimos `dias` dias e retorna um conjunto de IDs
    já coletados para deduplicação.
    """
    ids = set()
    hoje = datetime.now(BRT).date()
    for i in range(dias):
        data = (hoje - timedelta(days=i)).strftime("%Y-%m-%d")
        caminho = os.path.join(NOTICIAS_DIR, f"{data}.json")
        if os.path.exists(caminho):
            try:
                with open(caminho, encoding="utf-8") as f:
                    noticias = json.load(f)
                for n in noticias:
                    if "id" in n:
                        ids.add(n["id"])
            except Exception:
                pass
    return ids


def salvar_noticias(noticias: list, caminho: str) -> None:
    """Persiste a lista de notícias em um arquivo JSON com encoding UTF-8."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)


def log_info(msg: str) -> None:
    ts = datetime.now(BRT).strftime("%H:%M:%S")
    print(f"[{ts}] INFO  {msg}")


def log_erro(msg: str, exc: Exception = None) -> None:
    ts = datetime.now(BRT).strftime("%H:%M:%S")
    detalhe = f" — {exc}" if exc else ""
    print(f"[{ts}] ERRO  {msg}{detalhe}")
