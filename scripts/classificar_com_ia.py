"""
Classificação inteligente de notícias com Claude AI.

Segunda camada após o filtro por palavras-chave: o Claude avalia
relevância real, define prioridade com contexto e gera sugestões de
pauta criativas para a equipe de redes sociais da Agência FOLKS.

Se ANTHROPIC_API_KEY não estiver configurada, as notícias passam sem
modificação (fallback para classificação por palavras-chave).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import log_erro, log_info

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Máximo de artigos por chamada à API (segurança de tokens)
BATCH_SIZE = 40

_PROMPT_SISTEMA = """\
Você é especialista em contabilidade e direito tributário brasileiro.
Sua função é filtrar e classificar notícias para a newsletter semanal da Agência FOLKS,
enviada a escritórios de contabilidade e advocacia tributária.

Para cada notícia informe:

1. relevante (bool)
   TRUE  → tem aplicação prática direta para contadores ou advogados tributaristas:
            leis, decretos, INs, prazos fiscais, decisões STF/STJ/CARF com repercussão
            tributária, eSocial, SPED, obrigações acessórias, alíquotas, regimes tributários.
   FALSE → descartar: notícia policial/criminal sem cunho fiscal, apreensão de mercadorias,
            contrabando, política sem impacto tributário direto, esportes, cultura, etc.

2. prioridade (só se relevante=true)
   "Alto"  → nova lei/decreto/IN já publicada, prazo fiscal urgente, decisão STF/STJ
              de efeito imediato, mudança obrigatória com impacto nos clientes agora.
   "Médio" → projeto de lei em andamento, orientação/esclarecimento da Receita,
              atualização de alíquota, regulamentação, discussão no Congresso.
   "Baixo" → retrospectiva, tendência, curiosidade fiscal, conteúdo informativo
              sem urgência imediata.

3. sugestao_pauta (só se relevante=true, máx 140 caracteres, inclua emoji)
   Ideia criativa e objetiva para a equipe criar um card ou vídeo curto.
   Exemplos de formato: "🚨 Alerta: [tema] — o que muda para seus clientes?"
                        "📊 5 pontos sobre [tema] que todo contador precisa saber"
                        "💡 Dica: como [tema] impacta o Simples Nacional"

Responda APENAS com JSON válido, sem texto fora do JSON.\
"""


def _chamar_claude(artigos_indexados: list) -> list:
    """Envia um batch para o Claude Haiku e retorna a lista de resultados."""
    try:
        import anthropic
    except ImportError:
        log_erro("[IA] Pacote 'anthropic' não instalado. Execute: pip install anthropic")
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Monta payload reduzido (economiza tokens)
    entrada = [
        {
            "idx": a["idx"],
            "titulo": a["titulo"],
            "resumo": a.get("resumo", "")[:300],
            "fonte": a.get("fonte", ""),
            "categoria": a.get("categoria", ""),
        }
        for a in artigos_indexados
    ]

    prompt = (
        f"Classifique as {len(entrada)} notícias abaixo.\n"
        "Formato da resposta:\n"
        '{"resultados": ['
        '{"idx": 0, "relevante": true, "prioridade": "Alto", "sugestao_pauta": "..."},'
        '{"idx": 1, "relevante": false},'
        "...]}\n\n"
        f"Notícias:\n{json.dumps(entrada, ensure_ascii=False, indent=2)}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=_PROMPT_SISTEMA,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Remove blocos de código markdown se o modelo os incluir
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    resultado = json.loads(raw.strip())
    return resultado.get("resultados", [])


def classificar_noticias(noticias: list) -> list:
    """
    Refina relevância, prioridade e sugestão de pauta com Claude AI.

    As notícias já devem ter prioridade/sugestao_pauta preenchidos como
    fallback (via palavras-chave). O Claude pode:
      - Rejeitar artigos irrelevantes (relevante=false)
      - Ajustar a prioridade para cima ou para baixo
      - Substituir a sugestão de pauta por uma versão mais criativa

    Retorna apenas as notícias que o Claude considera relevantes.
    """
    if not ANTHROPIC_API_KEY:
        log_info("[IA] ANTHROPIC_API_KEY não configurada — usando classificação por palavras-chave.")
        return noticias

    if not noticias:
        return noticias

    log_info(f"[IA] Enviando {len(noticias)} notícias para classificação com Claude...")

    artigos_indexados = [{**n, "idx": i} for i, n in enumerate(noticias)]
    todos_resultados: list = []

    for inicio in range(0, len(artigos_indexados), BATCH_SIZE):
        batch = artigos_indexados[inicio: inicio + BATCH_SIZE]
        num_batch = inicio // BATCH_SIZE + 1
        log_info(f"[IA] Batch {num_batch}: {len(batch)} artigos")
        try:
            resultados = _chamar_claude(batch)
            todos_resultados.extend(resultados)
        except Exception as e:
            log_erro(f"[IA] Falha no batch {num_batch} — mantendo fallback para este batch", e)
            # Mantém todos os artigos do batch com valores de palavras-chave
            todos_resultados.extend([{"idx": a["idx"], "relevante": True} for a in batch])

    mapa = {r["idx"]: r for r in todos_resultados}
    noticias_finais = []
    rejeitadas = 0

    for i, n in enumerate(noticias):
        r = mapa.get(i, {"relevante": True})  # ausente → mantém por segurança
        if not r.get("relevante", True):
            rejeitadas += 1
            continue
        n["prioridade"] = r.get("prioridade", n.get("prioridade", "Baixo"))
        if r.get("sugestao_pauta"):
            n["sugestao_pauta"] = r["sugestao_pauta"]
        noticias_finais.append(n)

    log_info(
        f"[IA] Concluído: {len(noticias_finais)} relevantes, {rejeitadas} rejeitadas pela IA."
    )
    return noticias_finais
