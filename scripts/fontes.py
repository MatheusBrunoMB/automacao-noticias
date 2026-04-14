# Registro de fontes de notícias e listas de palavras-chave

FONTES = [
    {
        "nome": "Receita Federal",
        "url": "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias/RSS",
        "categoria": "Receita Federal",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 15,
    },
    {
        "nome": "Portal Contábeis",
        "url": "https://www.contabeis.com.br/noticias/rss/",
        "categoria": "Contabilidade",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 20,
    },
    {
        "nome": "Notícias Fiscais",
        "url": "https://noticiasfiscais.com.br/feed/",
        "categoria": "Tributário",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 20,
    },
    {
        "nome": "CFC - Conselho Federal de Contabilidade",
        "url": "https://cfc.org.br/feed/",
        "categoria": "Contabilidade",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 10,
    },
    {
        "nome": "JOTA Jornalismo",
        "url": "https://www.jota.info/feed",
        "categoria": "Jurídico",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 15,
    },
    {
        "nome": "Senado Federal",
        "url": "https://www12.senado.leg.br/noticias/feed",
        "categoria": "Legislação",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 10,
    },
    {
        "nome": "NewsAPI - Tributário BR",
        "url": None,
        "categoria": "Tributário",
        "ativo": True,
        "tipo": "newsapi",
        "query": "tributário OR contabilidade OR receita federal OR reforma tributária OR IRPF OR ICMS",
        "language": "pt",
        "max_itens": 10,
    },
]

# Termos que tornam uma notícia relevante para o nicho
PALAVRAS_CHAVE_INCLUSAO = [
    "tributário", "tributario", "tributária", "tributaria",
    "imposto", "impostos",
    "receita federal",
    "contabilidade", "contábil", "contabil", "contabilista", "contador",
    "fiscal", "fiscalização", "fiscalizacao",
    "IRPF", "IRPJ", "CSLL",
    "ICMS", "ISS", "IPI",
    "PIS", "COFINS", "PIS/COFINS",
    "IBS", "CBS",
    "reforma tributária", "reforma tributaria",
    "nota fiscal", "NF-e", "NFS-e",
    "MEI", "microempreendedor",
    "simples nacional",
    "lucro presumido", "lucro real",
    "SPED", "eSocial", "EFD", "DCTF", "DIRF", "DEFIS",
    "PGFN", "dívida ativa",
    "legislação fiscal", "legislacao fiscal",
    "lei complementar",
    "instrução normativa", "instrucao normativa",
    "STF tributário", "STJ tributário",
    "direito tributário", "direito tributario",
    "obrigação acessória", "obrigacao acessoria",
    "parcelamento", "anistia fiscal", "remissão fiscal",
    "sonegação", "sonegacao",
    "prazo fiscal", "declaração", "declaracao",
    "FGTS", "previdência", "previdencia",
    "alíquota", "aliquota", "base de cálculo",
    "escrituração", "escrita fiscal",
    "auditoria fiscal",
    "planejamento tributário", "elisão fiscal",
    "compliance fiscal",
]

# Palavras que indicam notícia de ALTA prioridade (impacto imediato nos clientes)
PALAVRAS_CHAVE_ALTA_PRIORIDADE = [
    "prazo", "vencimento", "encerramento",
    "nova lei", "novo decreto", "nova instrução normativa",
    "reforma tributária",
    "obrigatoriedade", "obrigatório",
    "multa", "penalidade", "autuação",
    "julgamento", "decisão do STF", "decisão do STJ",
    "aprovado", "promulgado", "publicado no diário oficial",
    "alerta", "atenção",
    "mudança", "alteração", "atualização urgente",
    "suspensão", "liminar",
    "parcelamento especial", "programa de regularização",
    "REFIS", "transação tributária",
    "prazo final", "último dia",
    "instrução normativa",
    "portaria",
    "resolução CFC",
]

# Palavras que indicam notícia de MÉDIA prioridade (relevante mas sem urgência imediata)
PALAVRAS_CHAVE_MEDIA_PRIORIDADE = [
    "atualização", "atualizacao",
    "esclarecimento", "orientação", "orientacao",
    "alíquota", "aliquota",
    "tributação", "tributacao",
    "regulamentação", "regulamentacao",
    "projeto de lei",
    "proposta",
    "discussão", "debate",
    "impacto",
    "planejamento",
    "tendência", "tendencia",
    "STF", "STJ", "CARF",
    "receita", "arrecadação",
    "déficit", "superávit fiscal",
    "fisco",
]

# Mapeamento de cores por categoria para uso no email e PDF
CORES_CATEGORIA = {
    "Receita Federal": "#003087",
    "Contabilidade":   "#2E7D32",
    "Tributário":      "#E65100",
    "Jurídico":        "#4A148C",
    "Legislação":      "#00695C",
}

# Ordem de exibição das categorias no digest
ORDEM_CATEGORIAS = [
    "Receita Federal",
    "Tributário",
    "Legislação",
    "Contabilidade",
    "Jurídico",
]
