"""
Gera o PDF da apresentação para o cliente.
Execute na pasta raiz do projeto:
    python apresentacao/gerar_pdf.py
"""

import os
import sys
from fpdf import FPDF, XPos, YPos

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
RAIZ      = os.path.join(BASE_DIR, "..")
LOGO_PATH = os.path.join(RAIZ, "logo-folks.png")
SAIDA     = os.path.join(BASE_DIR, "apresentacao_cliente.pdf")

# Paleta FOLKS
VINHO   = (61,   8,   7)
RED     = (169,  23,  10)
BEIGE   = (255, 252, 233)
GRAY    = (244, 244, 244)
WHITE   = (255, 255, 255)
DARK    = (26,  26,  26)
MID     = (85,  85,  85)
LIGHT   = (153, 153, 153)

# Cores de categoria
CAT_CORES = {
    "Tributário":    (0,   48, 135),
    "Legislação":    (0,  105,  92),
    "Contabilidade": (46, 125,  50),
    "Jurídico":      (74,  20, 140),
}

NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}


def _t(texto: str) -> str:
    """Sanitiza para latin-1 (Helvetica do fpdf2)."""
    sub = {
        "\u2014": "-", "\u2013": "-",
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...",
    }
    for k, v in sub.items():
        texto = texto.replace(k, v)
    return texto.encode("latin-1", errors="replace").decode("latin-1")


class PDF(FPDF):
    # ── helpers de cor ───────────────────────────────────────
    def fill(self, rgb): self.set_fill_color(*rgb)
    def ink(self, rgb):  self.set_text_color(*rgb)
    def draw(self, rgb): self.set_draw_color(*rgb)

    # ── bloco colorido de largura total ──────────────────────
    def band(self, y, h, color):
        self.fill(color)
        self.rect(0, y, 210, h, "F")

    # ── rótulo de seção ──────────────────────────────────────
    def label(self, texto, color=RED):
        self.set_font("Helvetica", "B", 8)
        self.ink(color)
        self.cell(0, 5, _t(texto.upper()), **NL)
        self.ln(1)

    # ── título grande ────────────────────────────────────────
    def h1(self, texto, color=DARK):
        self.set_font("Helvetica", "B", 22)
        self.ink(color)
        self.multi_cell(0, 9, _t(texto), **NL)
        self.ln(2)

    # ── título médio ─────────────────────────────────────────
    def h2(self, texto, color=DARK):
        self.set_font("Helvetica", "B", 13)
        self.ink(color)
        self.multi_cell(0, 6, _t(texto), **NL)
        self.ln(1)

    # ── parágrafo ────────────────────────────────────────────
    def p(self, texto, color=MID, size=10):
        self.set_font("Helvetica", "", size)
        self.ink(color)
        self.multi_cell(0, 5, _t(texto), **NL)
        self.ln(2)

    # ── linha horizontal ─────────────────────────────────────
    def hline(self, color=GRAY, margin=15):
        self.draw(color)
        self.line(margin, self.get_y(), 210 - margin, self.get_y())
        self.ln(4)

    # ── card com borda lateral colorida ──────────────────────
    def card(self, titulo, desc, accent=RED, y_offset=0):
        x0  = self.get_x()
        y0  = self.get_y()
        w   = self.epw
        # borda lateral
        self.fill(accent)
        self.rect(x0, y0, 3, 22, "F")
        # título
        self.set_xy(x0 + 6, y0 + 2)
        self.set_font("Helvetica", "B", 10)
        self.ink(DARK)
        self.cell(w - 6, 5, _t(titulo), **NL)
        self.set_x(x0 + 6)
        # descrição
        self.set_font("Helvetica", "", 8.5)
        self.ink(MID)
        self.multi_cell(w - 6, 4.5, _t(desc), **NL)
        self.ln(4)

    # ── badge de prioridade ──────────────────────────────────
    def badge(self, texto, bg, fg=WHITE):
        self.fill(bg)
        self.ink(fg)
        self.set_font("Helvetica", "B", 8)
        bw = self.get_string_width(texto) + 8
        self.rect(self.get_x(), self.get_y(), bw, 6, "F")
        self.cell(bw, 6, _t(texto))
        self.ink(DARK)


def capa(pdf: PDF):
    pdf.add_page()
    # fundo bege
    pdf.band(0, 297, BEIGE)
    # borda inferior vermelha
    pdf.fill(RED)
    pdf.rect(0, 293, 210, 4, "F")
    # logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=75, y=52, h=24)
        pdf.set_y(84)
    else:
        pdf.set_y(64)
    # supertítulo
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(93, 13, 6)   # vermelho escurecido (55% do RED)
    pdf.cell(0, 6, "APRESENTACAO DE SOLUCAO", align="C", **NL)
    pdf.ln(6)
    # título
    pdf.set_font("Helvetica", "B", 36)
    pdf.ink(RED)
    pdf.cell(0, 14, "Automacao de", align="C", **NL)
    pdf.ink(VINHO)
    pdf.cell(0, 14, "Noticias", align="C", **NL)
    pdf.ln(8)
    # subtítulo
    pdf.set_font("Helvetica", "", 13)
    pdf.ink((100, 40, 38))
    pdf.set_x(30)
    pdf.multi_cell(150, 6,
        "Inteligencia de conteudo automatica para escritorios de "
        "contabilidade e advocacia tributaria e previdenciaria.",
        align="C")
    pdf.ln(14)
    # badge
    pdf.set_font("Helvetica", "B", 9)
    pdf.ink(BEIGE)
    bw = 100
    pdf.set_x((210 - bw) / 2)
    pdf.fill(RED)
    pdf.rect((210 - bw) / 2, pdf.get_y(), bw, 8, "F")
    pdf.cell(bw, 8, "Desenvolvido pela Agencia FOLKS", align="C", **NL)


def desafio(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("O Desafio", RED)
    pdf.h1("Manter-se atualizado\nda muito trabalho.")
    pdf.p(
        "O universo contabil e juridico muda constantemente - novas leis, prazos, "
        "decisoes do STJ e STF, instrucoes normativas da Receita Federal. "
        "Acompanhar tudo isso exige horas de pesquisa diaria que poderiam ser "
        "dedicadas aos clientes.",
    )
    pdf.hline()

    for titulo, desc in [
        ("Dezenas de fontes",
         "Sao 8 portais especializados para monitorar diariamente, alem de feeds do "
         "governo e do Senado Federal."),
        ("Filtrar o que importa",
         "Nem tudo que e publicado e relevante para o seu nicho. Separar o que "
         "interessa do que nao interessa consome tempo."),
        ("Transformar em conteudo",
         "Depois de selecionar, ainda e preciso transformar a noticia em pauta para "
         "redes sociais, videos e comunicados."),
    ]:
        pdf.card(titulo, desc)


def solucao(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("A Solucao", RED)
    pdf.h1("Criamos um sistema que faz\nesse trabalho por voce.")
    pdf.p(
        "A automacao monitora as principais fontes de noticias do setor, filtra apenas "
        "o que e relevante para contabilidade, tributario e previdenciario, e entrega "
        "tudo organizado toda semana diretamente na sua caixa de entrada."
    )
    pdf.hline()

    itens = [
        ("Inteligencia Artificial",
         "Cada noticia e avaliada por IA especializada em direito tributario e "
         "previdenciario, que define relevancia, prioridade e sugere pautas."),
        ("100% Automatico",
         "Nenhuma acao manual necessaria. O sistema roda sozinho todo dia e envia "
         "o resumo completo toda segunda-feira de manha."),
        ("Noticias com prioridade",
         "Cada noticia recebe Alto, Medio ou Baixo para que sua equipe saiba "
         "exatamente o que e urgente e o que e informativo."),
        ("Sugestoes de pauta prontas",
         "Junto com cada noticia, a IA entrega uma sugestao criativa de pauta "
         "para card ou video curto, ja formatada para uso imediato."),
    ]
    for titulo, desc in itens:
        pdf.card(titulo, desc)


def fontes(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("De Onde Vem as Noticias", RED)
    pdf.h1("8 fontes especializadas\nmonitoradas automaticamente.")
    pdf.p(
        "O sistema acessa diariamente os portais mais relevantes para contabilidade, "
        "tributario, legislacao e direito previdenciario - incluindo fontes oficiais."
    )

    lista = [
        ("Receita Federal",                      "Tributario - Oficial Federal"),
        ("Portal Contabeis",                     "Contabilidade"),
        ("Noticias Fiscais",                      "Tributario"),
        ("CFC - Conselho Federal de Contabilidade","Contabilidade - Oficial"),
        ("JOTA Jornalismo",                      "Juridico"),
        ("Senado Federal",                       "Legislacao - Oficial Federal"),
        ("SEFAZ-CE",                             "Legislacao - Oficial Ceara"),
        ("Prefeitura de Fortaleza",              "Legislacao - Oficial Municipal"),
        ("NewsAPI",                              "Tributario - Buscador nacional"),
    ]

    col_w = (pdf.epw - 8) / 2
    x_left  = pdf.l_margin
    x_right = pdf.l_margin + col_w + 8
    y_start = pdf.get_y()

    for i, (nome, cat) in enumerate(lista):
        x = x_left if i % 2 == 0 else x_right
        y = y_start + (i // 2) * 18
        # borda
        pdf.fill(RED)
        pdf.rect(x, y, 3, 14, "F")
        # fundo
        pdf.fill(GRAY)
        pdf.rect(x + 3, y, col_w - 3, 14, "F")
        # texto
        pdf.set_xy(x + 6, y + 2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.ink(DARK)
        pdf.cell(col_w - 8, 4.5, _t(nome), **NL)
        pdf.set_x(x + 6)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ink(LIGHT)
        pdf.cell(col_w - 8, 4, _t(cat), **NL)


def fluxo(pdf: PDF):
    pdf.add_page()
    # fundo vinho na metade superior
    pdf.band(0, 148, VINHO)
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    # ── Como funciona ────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.ink((180, 140, 130))
    pdf.cell(0, 5, "COMO FUNCIONA", **NL)
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 20)
    pdf.ink(BEIGE)
    pdf.cell(0, 9, "Do monitoramento ao seu email", **NL)
    pdf.set_font("Helvetica", "B", 20)
    pdf.ink((232, 121, 94))
    pdf.cell(0, 9, "em 4 etapas.", **NL)
    pdf.ln(6)

    etapas = [
        ("1", "Coleta",   "Todo dia as 7h o sistema acessa os 8 portais"),
        ("2", "Filtro",   "Apenas noticias do nicho contabil e juridico passam"),
        ("3", "IA",       "A IA avalia, prioriza e gera sugestao de pauta"),
        ("4", "Entrega",  "Toda segunda as 8h o digest chega no seu email"),
    ]
    step_w = pdf.epw / 4
    y_step = pdf.get_y()
    for i, (num, titulo, desc) in enumerate(etapas):
        x = pdf.l_margin + i * step_w
        # círculo
        pdf.fill(RED)
        pdf.ellipse(x + step_w / 2 - 9, y_step, 18, 10, "F")
        pdf.set_xy(x, y_step)
        pdf.set_font("Helvetica", "B", 11)
        pdf.ink(BEIGE)
        pdf.cell(step_w, 10, num, align="C")
        # seta
        if i < 3:
            pdf.set_font("Helvetica", "", 12)
            pdf.ink((200, 160, 150))
            pdf.set_xy(x + step_w - 4, y_step + 1)
            pdf.cell(8, 8, ">", align="C")
        # título
        pdf.set_xy(x, y_step + 12)
        pdf.set_font("Helvetica", "B", 9)
        pdf.ink(BEIGE)
        pdf.cell(step_w, 5, _t(titulo), align="C")
        # desc
        pdf.set_xy(x + 2, y_step + 18)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ink((200, 185, 175))
        pdf.multi_cell(step_w - 4, 4, _t(desc), align="C",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Calendário ───────────────────────────────────────────
    pdf.set_y(148 + 10)
    pdf.set_margins(18, 0, 18)

    pdf.label("Calendario de Execucao", RED)
    pdf.h1("Automatico. Toda semana. Sem falhas.")

    half = (pdf.epw - 8) / 2
    y_cal = pdf.get_y()

    for i, (hora, titulo, desc, freq) in enumerate([
        ("07:00", "Coleta de Noticias",
         "O sistema busca noticias em todos os portais monitorados e as "
         "salva com prioridade classificada pela IA.",
         "TODO DIA"),
        ("08:00", "Envio do Digest Semanal",
         "As melhores noticias da semana sao compiladas e enviadas por email "
         "com PDF e planilha de pauta para a equipe de conteudo.",
         "TODA SEGUNDA-FEIRA"),
    ]):
        x = pdf.l_margin + i * (half + 8)
        pdf.fill(GRAY)
        pdf.rect(x, y_cal, half, 52, "F")
        pdf.fill(RED)
        pdf.rect(x, y_cal, half, 3, "F")

        pdf.set_xy(x + 6, y_cal + 7)
        pdf.set_font("Helvetica", "B", 22)
        pdf.ink(RED)
        pdf.cell(half - 8, 10, hora)

        pdf.set_xy(x + 6, y_cal + 19)
        pdf.set_font("Helvetica", "B", 10)
        pdf.ink(DARK)
        pdf.multi_cell(half - 8, 5, _t(titulo),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(x + 6, pdf.get_y())
        pdf.set_font("Helvetica", "", 8)
        pdf.ink(MID)
        pdf.multi_cell(half - 8, 4.5, _t(desc),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # badge frequência
        pdf.set_xy(x + 6, y_cal + 44)
        pdf.fill(RED)
        fw = pdf.get_string_width(freq) + 8
        pdf.rect(x + 6, y_cal + 44, fw, 5.5, "F")
        pdf.set_font("Helvetica", "B", 7)
        pdf.ink(BEIGE)
        pdf.cell(fw, 5.5, freq)


def entregaveis(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("O Que Voce Recebe", RED)
    pdf.h1("Tres entregas toda\nsegunda-feira.")
    pdf.p("Um unico email com tudo que sua equipe precisa para a semana de conteudo.")
    pdf.hline()

    for icone, titulo, desc in [
        ("[ EMAIL HTML ]",
         "Email HTML formatado",
         "Email visualmente organizado com todas as noticias da semana, agrupadas por "
         "categoria e ordenadas por prioridade. Cada noticia vem com badge de "
         "prioridade colorido, resumo, fonte, data e sugestao de pauta."),
        ("PDF",
         "PDF para arquivo e impressao",
         "Versao em PDF do digest completo, ideal para arquivamento, leitura offline "
         "ou distribuicao interna. Contem todas as noticias com prioridades e "
         "sugestoes de pauta."),
        ("EXCEL",
         "Planilha Excel — Pauta da Semana",
         "Planilha pronta para uso pela equipe de conteudo, com colunas de formato "
         "sugerido (Feed, Reels, Stories), gancho da legenda, desenvolvimento, CTA, "
         "hashtags e sugestao visual. Basta abrir e comecar a produzir."),
    ]:
        y0 = pdf.get_y()
        pdf.fill(GRAY)
        pdf.rect(pdf.l_margin, y0, pdf.epw, 32, "F")
        pdf.fill(RED)
        pdf.rect(pdf.l_margin, y0, 3, 32, "F")
        pdf.set_xy(pdf.l_margin + 8, y0 + 4)
        pdf.set_font("Helvetica", "B", 7)
        pdf.ink(RED)
        pdf.cell(25, 5, icone)
        pdf.set_xy(pdf.l_margin + 8, y0 + 10)
        pdf.set_font("Helvetica", "B", 11)
        pdf.ink(DARK)
        pdf.multi_cell(pdf.epw - 10, 5.5, _t(titulo),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(pdf.l_margin + 8, pdf.get_y())
        pdf.set_font("Helvetica", "", 8.5)
        pdf.ink(MID)
        pdf.multi_cell(pdf.epw - 10, 4.5, _t(desc),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)


def categorias_e_prioridades(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    # ── Categorias ───────────────────────────────────────────
    pdf.label("Categorias de Noticias", RED)
    pdf.h1("Tudo organizado por area de atuacao.")
    pdf.p("As noticias sao classificadas em quatro categorias cobrindo as principais areas do escritorio.")

    cats = [
        ("Tributario",    CAT_CORES["Tributário"],
         "IRPF, IRPJ, ICMS, ISS, PIS/COFINS, CSLL\nSimples Nacional, Reforma tributaria\nReceita Federal, Prazos e obrigacoes\neSocial, SPED, NF-e"),
        ("Legislacao",    CAT_CORES["Legislação"],
         "Novas leis e decretos\nInstrucoes normativas e portarias\nProjetos de lei em votacao\nSEFAZ-CE e Prefeitura de Fortaleza"),
        ("Contabilidade", CAT_CORES["Contabilidade"],
         "Normas do CFC e CRC\nAuditoria fiscal e escrituracao\nPlanejamento contabil\nNovas obrigacoes e tecnologia"),
        ("Juridico",      CAT_CORES["Jurídico"],
         "Decisoes STF e STJ\nINSS e aposentadoria\nBeneficios previdenciarios\nDireito empresarial e CARF"),
    ]
    cat_w = (pdf.epw - 6) / 4
    y_cat = pdf.get_y()
    for i, (nome, cor, itens) in enumerate(cats):
        x = pdf.l_margin + i * (cat_w + 2)
        pdf.fill(GRAY)
        pdf.rect(x, y_cat, cat_w, 52, "F")
        pdf.fill(cor)
        pdf.rect(x, y_cat, cat_w, 4, "F")
        pdf.set_xy(x + 4, y_cat + 6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.ink(cor)
        pdf.cell(cat_w - 6, 5, _t(nome))
        pdf.set_xy(x + 4, y_cat + 13)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ink(MID)
        pdf.multi_cell(cat_w - 6, 4.5, _t(itens),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Prioridades ───────────────────────────────────────────
    pdf.set_y(y_cat + 58)
    pdf.label("Sistema de Prioridades", RED)
    pdf.h1("Saiba o que e urgente sem precisar ler tudo.")

    prios = [
        ("ALTO",  (169,23,10),  (255,236,236),
         "Impacto imediato",
         "Nova lei publicada, prazo fiscal urgente, decisao definitiva do STF/STJ, "
         "instrucao normativa ja em vigor. Exige comunicacao rapida com clientes."),
        ("MEDIO", (230,81,0),   (255,248,225),
         "Relevante - acompanhar",
         "Projeto de lei em votacao, orientacao da Receita ou INSS, nova tese "
         "tributaria em discussao nos tribunais. Importante mas sem urgencia imediata."),
        ("BAIXO", (117,117,117),(245,245,245),
         "Informativo - contexto",
         "Retrospectivas, tendencias do setor, curiosidades tributarias. Excelente "
         "para pautas de redes sociais mais leves e didaticas."),
    ]
    for badge_txt, badge_fg, badge_bg, titulo, desc in prios:
        y0 = pdf.get_y()
        pdf.fill(GRAY)
        pdf.rect(pdf.l_margin, y0, pdf.epw, 20, "F")
        # badge
        pdf.fill(badge_bg)
        bw = 22
        pdf.rect(pdf.l_margin + 4, y0 + 6, bw, 7, "F")
        pdf.set_xy(pdf.l_margin + 4, y0 + 6)
        pdf.set_font("Helvetica", "B", 7)
        pdf.ink(badge_fg)
        pdf.cell(bw, 7, badge_txt, align="C")
        # título + desc
        pdf.set_xy(pdf.l_margin + 30, y0 + 3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.ink(DARK)
        pdf.cell(pdf.epw - 32, 5, _t(titulo))
        pdf.set_xy(pdf.l_margin + 30, y0 + 9)
        pdf.set_font("Helvetica", "", 8)
        pdf.ink(MID)
        pdf.multi_cell(pdf.epw - 32, 4, _t(desc),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)


def aplicacoes(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("Aplicacoes Praticas", RED)
    pdf.h1("O que sua equipe pode\nfazer com isso.")
    pdf.p(
        "O digest nao e so informacao - e a base de uma estrategia de "
        "conteudo completa para o escritorio."
    )
    pdf.hline()

    itens = [
        ("Conteudo para redes sociais",
         "Cada noticia vem com sugestao de gancho, desenvolvimento e CTA prontos "
         "para virar um card ou Reels no Instagram e LinkedIn."),
        ("Roteiros de video",
         "Noticias de prioridade Alta e Media sao otimas para videos curtos de "
         "posicionamento e atualizacao para clientes."),
        ("Planejamento semanal",
         "A planilha Excel entregue toda segunda serve como grade de pauta pronta "
         "para a semana, eliminando a reuniao de briefing."),
        ("Comunicados aos clientes",
         "Noticias de prioridade Alta indicam quando o escritorio precisa alertar "
         "sua base sobre mudancas urgentes."),
        ("Arquivo de referencia",
         "O PDF semanal forma um acervo historico de noticias relevantes do setor, "
         "util para consulta e comparacao ao longo do tempo."),
        ("Autoridade de mercado",
         "Publicar conteudo atualizado e relevante posiciona o escritorio como "
         "referencia no segmento para clientes e prospects."),
    ]
    for titulo, desc in itens:
        pdf.card(titulo, desc)

    # Rodapé final
    pdf.ln(4)
    pdf.hline(RED)
    pdf.set_font("Helvetica", "", 9)
    pdf.ink(LIGHT)
    pdf.cell(0, 5,
        "Automatizando o que pode ser automatizado para voce focar no que realmente importa.",
        align="C", **NL)
    pdf.set_font("Helvetica", "B", 9)
    pdf.ink(RED)
    pdf.cell(0, 5, "Agencia FOLKS", align="C", **NL)


def main():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)

    capa(pdf)
    desafio(pdf)
    solucao(pdf)
    fontes(pdf)
    fluxo(pdf)
    entregaveis(pdf)
    categorias_e_prioridades(pdf)
    aplicacoes(pdf)

    pdf.output(SAIDA)
    print(f"PDF gerado: {SAIDA}")


if __name__ == "__main__":
    main()
