"""
Filtra notícias pelo nicho de contabilidade e direito tributário.
Fontes especializadas (Receita Federal, Contábeis, Notícias Fiscais, CFC)
são aceitas com critério mais amplo; fontes gerais (JOTA, Senado)
exigem match no título.
"""

from fontes import PALAVRAS_CHAVE_INCLUSAO, PALAVRAS_CHAVE_EXCLUSAO

# Fontes já especializadas no nicho — filtro mais permissivo
FONTES_ESPECIALIZADAS = {
    "Receita Federal",
    "Portal Contábeis",
    "Notícias Fiscais",
    "CFC - Conselho Federal de Contabilidade",
    "SEFAZ-CE",
    "Prefeitura de Fortaleza",
}


def _contem_palavra_chave(texto: str, palavras: list) -> bool:
    texto_lower = texto.lower()
    return any(p.lower() in texto_lower for p in palavras)


def eh_relevante(noticia: dict) -> bool:
    """
    Retorna True se a notícia for relevante para o nicho.

    Critérios:
    - Rejeita imediatamente se o TÍTULO contém palavra de exclusão (policial/crime).
    - Fontes especializadas: aceita se título OU resumo contém palavra-chave de inclusão.
    - Fontes gerais (JOTA, Senado, NewsAPI): exige match no título.
    """
    titulo = noticia.get("titulo", "")
    resumo = noticia.get("resumo", "")
    fonte = noticia.get("fonte", "")

    # Filtro de exclusão — rejeita conteúdo policial/criminal sem relevância contábil
    if _contem_palavra_chave(titulo, PALAVRAS_CHAVE_EXCLUSAO):
        return False

    titulo_ok = _contem_palavra_chave(titulo, PALAVRAS_CHAVE_INCLUSAO)

    if fonte in FONTES_ESPECIALIZADAS:
        resumo_ok = _contem_palavra_chave(resumo, PALAVRAS_CHAVE_INCLUSAO)
        return titulo_ok or resumo_ok

    # Para fontes gerais, o título precisa bater
    return titulo_ok


def filtrar_lista(noticias: list) -> list:
    """Aplica `eh_relevante` em uma lista e retorna apenas as aprovadas."""
    return [n for n in noticias if eh_relevante(n)]
