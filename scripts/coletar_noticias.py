"""
Script de coleta diária de notícias.
Executado pelo GitHub Actions todo dia às 07h BRT.
"""

import os
import sys
import time
from datetime import datetime

import feedparser
import requests

# Garante que os imports relativos funcionam tanto localmente quanto no Actions
sys.path.insert(0, os.path.dirname(__file__))

from analisar_noticias import calcular_prioridade, gerar_sugestao_pauta
from filtrar_noticias import filtrar_lista
from fontes import FONTES
from utils import (
    BRT,
    NOTICIAS_DIR,
    formatar_data,
    gerar_id,
    carregar_ids_existentes,
    log_erro,
    log_info,
    obter_data_hoje,
    salvar_noticias,
    strip_html,
)

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Timeout para requisições HTTP (segundos)
HTTP_TIMEOUT = 15


def _parsear_rss(fonte: dict, ids_existentes: set) -> list:
    """Faz parse de um feed RSS/RDF e retorna lista de notícias novas."""
    noticias = []
    try:
        feed = feedparser.parse(fonte["url"], agent="automacao-noticias/1.0")
        if feed.bozo and not feed.entries:
            log_erro(f"[{fonte['nome']}] Feed mal-formado ou inacessível")
            return []

        for entry in feed.entries[: fonte["max_itens"]]:
            titulo = strip_html(entry.get("title", "")).strip()
            url = entry.get("link", "").strip()
            if not titulo or not url:
                continue

            noticia_id = gerar_id(titulo, url)
            if noticia_id in ids_existentes:
                continue

            resumo = strip_html(
                entry.get("summary", "")
                or entry.get("description", "")
                or entry.get("content", [{}])[0].get("value", "")
            )[:500]

            data_pub = formatar_data(
                entry.get("published_parsed")
                or entry.get("updated_parsed")
                or entry.get("dc_date")
                or ""
            )

            noticias.append({
                "id": noticia_id,
                "titulo": titulo,
                "resumo": resumo,
                "url": url,
                "fonte": fonte["nome"],
                "categoria": fonte["categoria"],
                "data_publicacao": data_pub,
                "data_coleta": datetime.now(BRT).strftime("%Y-%m-%d %H:%M:%S"),
            })

    except Exception as e:
        log_erro(f"[{fonte['nome']}] Falha ao processar RSS", e)
    return noticias


def _parsear_newsapi(fonte: dict, ids_existentes: set) -> list:
    """Consulta a NewsAPI e retorna lista de notícias novas."""
    if not NEWSAPI_KEY:
        log_info("[NewsAPI] Chave não configurada — fonte ignorada.")
        return []

    noticias = []
    try:
        params = {
            "q": fonte["query"],
            "language": fonte.get("language", "pt"),
            "sortBy": "publishedAt",
            "pageSize": fonte["max_itens"],
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(NEWSAPI_URL, params=params, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for article in data.get("articles", []):
            titulo = strip_html(article.get("title", "") or "").strip()
            url = (article.get("url", "") or "").strip()
            if not titulo or not url or titulo == "[Removed]":
                continue

            noticia_id = gerar_id(titulo, url)
            if noticia_id in ids_existentes:
                continue

            resumo = strip_html(
                article.get("description", "") or article.get("content", "") or ""
            )[:500]

            noticias.append({
                "id": noticia_id,
                "titulo": titulo,
                "resumo": resumo,
                "url": url,
                "fonte": fonte["nome"],
                "categoria": fonte["categoria"],
                "data_publicacao": formatar_data(article.get("publishedAt", "")),
                "data_coleta": datetime.now(BRT).strftime("%Y-%m-%d %H:%M:%S"),
            })

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            log_erro("[NewsAPI] Limite de requisições atingido — ignorando hoje.")
        else:
            log_erro("[NewsAPI] Erro HTTP", e)
    except Exception as e:
        log_erro("[NewsAPI] Falha inesperada", e)

    return noticias


def main():
    data_hoje = obter_data_hoje()
    caminho_saida = os.path.join(NOTICIAS_DIR, f"{data_hoje}.json")
    log_info(f"Iniciando coleta para {data_hoje}")

    ids_existentes = carregar_ids_existentes(dias=30)
    log_info(f"IDs existentes carregados: {len(ids_existentes)}")

    todas_noticias = []
    fontes_ativas = [f for f in FONTES if f.get("ativo")]

    for fonte in fontes_ativas:
        log_info(f"Coletando: {fonte['nome']}")
        if fonte["tipo"] == "newsapi":
            brutas = _parsear_newsapi(fonte, ids_existentes)
        else:
            brutas = _parsear_rss(fonte, ids_existentes)

        # Aplica filtro de relevância
        filtradas = filtrar_lista(brutas)

        # Calcula prioridade e sugestão de pauta
        for n in filtradas:
            n["prioridade"] = calcular_prioridade(n)
            n["sugestao_pauta"] = gerar_sugestao_pauta(n)
            ids_existentes.add(n["id"])  # evita duplicatas entre fontes no mesmo dia

        todas_noticias.extend(filtradas)
        log_info(f"  → {len(filtradas)} notícias novas de {fonte['nome']}")

        # Pequena pausa para não sobrecarregar as fontes
        time.sleep(1)

    # Ordena por prioridade e depois por data (mais recente primeiro)
    ordem_prioridade = {"Alto": 0, "Médio": 1, "Baixo": 2}
    todas_noticias.sort(
        key=lambda n: (
            ordem_prioridade.get(n.get("prioridade", "Baixo"), 2),
            n.get("data_publicacao", ""),
        ),
        reverse=False,
    )
    # Inverte a data dentro de cada prioridade (mais recente primeiro)
    todas_noticias.sort(
        key=lambda n: (
            ordem_prioridade.get(n.get("prioridade", "Baixo"), 2),
            n.get("data_publicacao", ""),
        )
    )

    salvar_noticias(todas_noticias, caminho_saida)
    log_info(
        f"Coleta concluída: {len(todas_noticias)} notícias salvas em {caminho_saida}"
    )


if __name__ == "__main__":
    main()
