# Registro de fontes de notícias e listas de palavras-chave

FONTES = [
    # --- Tributário ---
    {
        "nome": "Receita Federal",
        "url": "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias/RSS",
        "categoria": "Tributário",   # categoria padrão; IA pode reclassificar como Legislação
        "ativo": True,
        "tipo": "rss",
        "max_itens": 15,
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
        "nome": "NewsAPI - Tributário BR",
        "url": None,
        "categoria": "Tributário",
        "ativo": True,
        "tipo": "newsapi",
        "query": "tributário OR contabilidade OR receita federal OR reforma tributária OR IRPF OR ICMS",
        "language": "pt",
        "max_itens": 10,
    },
    # --- Legislação ---
    {
        "nome": "Senado Federal",
        "url": "https://www12.senado.leg.br/noticias/feed",
        "categoria": "Legislação",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 10,
    },
    {
        "nome": "SEFAZ-CE",
        "url": "https://www.sefaz.ce.gov.br/feed/",
        "categoria": "Legislação",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 10,
    },
    {
        "nome": "Prefeitura de Fortaleza",
        "url": "https://www.fortaleza.ce.gov.br/?format=feed&type=rss",
        "categoria": "Legislação",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 10,
    },
    # --- Contabilidade ---
    {
        "nome": "Portal Contábeis",
        "url": "https://www.contabeis.com.br/noticias/rss/",
        "categoria": "Contabilidade",
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
    # --- Jurídico ---
    {
        "nome": "JOTA Jornalismo",
        "url": "https://www.jota.info/feed",
        "categoria": "Jurídico",
        "ativo": True,
        "tipo": "rss",
        "max_itens": 15,
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
    # Previdenciário
    "previdenciário", "previdenciaria", "previdenciário",
    "INSS", "aposentadoria",
    "pensão por morte", "pensao por morte",
    "auxílio-doença", "auxilio-doenca", "auxílio acidente",
    "salário-maternidade", "salario-maternidade",
    "BPC", "LOAS",
    "contribuição previdenciária", "contribuicao previdenciaria",
    "RGPS", "RPPS",
    "benefício previdenciário", "beneficio previdenciario",
    "tempo de contribuição", "fator previdenciário",
    "planejamento previdenciário",
    "perícia médica INSS", "pericia medica INSS",
    "revisão de benefício", "revisao de beneficio",
    "direito previdenciário", "direito previdenciario",
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

# Palavras que indicam conteúdo policial/criminal SEM relevância fiscal ou contábil.
# Se encontradas no TÍTULO, a notícia é rejeitada independentemente da fonte.
PALAVRAS_CHAVE_EXCLUSAO = [
    "contrabando", "contrabandeado", "contrabandeados", "contrabandeada",
    "narcotráfico", "narcotrafico",
    "tráfico de drogas", "trafico de drogas",
    "tráfico de entorpecentes", "trafico de entorpecentes",
    "entorpecente", "entorpecentes",
    "drogas apreendidas", "droga apreendida",
    "medicamentos apreendidos", "medicamento apreendido",
    "cigarros apreendidos", "cigarro apreendido",
    "armas apreendidas", "arma apreendida",
    "mercadoria contrabandeada", "mercadorias contrabandeadas",
    "homicídio", "homicidio",
    "assassinato",
    "sequestro",
    "mandado de prisão", "mandado de prisao",
    "preso em flagrante",
    "operação policial",
    "traficante", "traficantes",
]

# Mapeamento de cores por categoria para uso no email e PDF
CORES_CATEGORIA = {
    "Tributário":   "#003087",  # azul
    "Legislação":   "#00695C",  # verde escuro
    "Contabilidade":"#2E7D32",  # verde
    "Jurídico":     "#4A148C",  # roxo
}

# Ordem de exibição das categorias na news semanal
ORDEM_CATEGORIAS = [
    "Tributário",
    "Legislação",
    "Contabilidade",
    "Jurídico",
]
