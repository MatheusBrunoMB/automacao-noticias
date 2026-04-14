"""
Calcula o índice de prioridade de cada notícia e gera uma sugestão de pauta
para a equipe de conteúdo da agência.
"""

from fontes import (
    PALAVRAS_CHAVE_ALTA_PRIORIDADE,
    PALAVRAS_CHAVE_MEDIA_PRIORIDADE,
)


def _contem(texto: str, palavras: list) -> bool:
    t = texto.lower()
    return any(p.lower() in t for p in palavras)


def calcular_prioridade(noticia: dict) -> str:
    """
    Retorna "Alto", "Médio" ou "Baixo".

    Regras (em ordem de precedência):
    1. Alto  — palavra de alta prioridade no TÍTULO, ou fonte = "Receita Federal"
    2. Médio — palavra de média prioridade no título/resumo,
               ou categoria em {"Tributário", "Legislação"}
    3. Baixo — demais casos
    """
    titulo = noticia.get("titulo", "")
    resumo = noticia.get("resumo", "")
    fonte = noticia.get("fonte", "")
    categoria = noticia.get("categoria", "")

    if fonte == "Receita Federal" or _contem(titulo, PALAVRAS_CHAVE_ALTA_PRIORIDADE):
        return "Alto"

    texto_completo = f"{titulo} {resumo}"
    if (
        _contem(texto_completo, PALAVRAS_CHAVE_MEDIA_PRIORIDADE)
        or categoria in ("Tributário", "Legislação")
    ):
        return "Médio"

    return "Baixo"


# Templates de sugestão de pauta por (prioridade, categoria)
_TEMPLATES = {
    ("Alto", "Receita Federal"):  "🚨 URGENTE — {titulo}: explique o impacto direto para seus clientes",
    ("Alto", "Legislação"):       "📋 Nova legislação ou prazo: crie um checklist sobre "{titulo}"",
    ("Alto", "Tributário"):       "⚠️ Alerta tributário: o que muda para seus clientes com "{titulo}"",
    ("Alto", "Contabilidade"):    "🔔 Atenção: "{titulo}" — card com os pontos de atenção do contador",
    ("Alto", "Jurídico"):         "⚖️ Decisão importante: simplifique "{titulo}" para leigos",
    ("Médio", "Receita Federal"): "📌 Atualização da Receita Federal: "{titulo}" — o que você precisa saber",
    ("Médio", "Tributário"):      "💡 Entenda "{titulo}" — card educativo para redes sociais",
    ("Médio", "Contabilidade"):   "📊 Dica contábil: simplifique "{titulo}" em 5 pontos práticos",
    ("Médio", "Legislação"):      "📜 Legislação em pauta: "{titulo}" — explique de forma acessível",
    ("Médio", "Jurídico"):        "⚖️ Jurídico descomplicado: o que significa "{titulo}" na prática",
    ("Baixo", "Receita Federal"): "📰 Contexto: "{titulo}" — pode ser legenda ou enquete no Instagram",
    ("Baixo", "Tributário"):      "📰 Notícia de contexto: "{titulo}" — ótima para enquete ou curiosidade",
    ("Baixo", "Contabilidade"):   "📰 Conteúdo informativo: "{titulo}" — bom para post de engajamento",
    ("Baixo", "Legislação"):      "📰 Legislação para conhecer: "{titulo}" — post tipo 'Você sabia?'",
    ("Baixo", "Jurídico"):        "📰 Contexto jurídico: "{titulo}" — pode ser usado em carrossel educativo",
}

_TEMPLATE_PADRAO = "📰 Notícia relevante: "{titulo}" — avalie o potencial de conteúdo para seus clientes"


def gerar_sugestao_pauta(noticia: dict) -> str:
    """Retorna uma string com a sugestão de pauta para a equipe de conteúdo."""
    prioridade = noticia.get("prioridade", "Baixo")
    categoria = noticia.get("categoria", "")
    titulo = noticia.get("titulo", "")

    template = _TEMPLATES.get((prioridade, categoria), _TEMPLATE_PADRAO)
    return template.format(titulo=titulo)
