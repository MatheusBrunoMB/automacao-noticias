"""
Gera o PDF da apresentação para o cliente.
Execute na pasta raiz do projeto:
    python apresentacao/gerar_pdf.py
"""

import os
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

CAT_CORES = {
    "Tributário":    (0,   48, 135),
    "Legislação":    (0,  105,  92),
    "Contabilidade": (46, 125,  50),
    "Jurídico":      (74,  20, 140),
}

NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}

# Nome da fonte registrada — sobrescrito em _setup_fonts() se TTF encontrado
FONT = "Helvetica"


def _find_font(*names) -> str | None:
    """Procura arquivo TTF em pastas padrão do Windows e Linux."""
    dirs = [
        r"C:\Windows\Fonts",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/freefont",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype",
        "/usr/share/fonts",
    ]
    for d in dirs:
        for name in names:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None


def _setup_fonts(pdf: "PDF"):
    """Registra fonte TrueType Unicode; atualiza global FONT."""
    global FONT
    reg  = _find_font("arial.ttf",   "LiberationSans-Regular.ttf", "DejaVuSans.ttf")
    bold = _find_font("arialbd.ttf", "LiberationSans-Bold.ttf",    "DejaVuSans-Bold.ttf")
    ital = _find_font("ariali.ttf",  "LiberationSans-Italic.ttf",  "DejaVuSans-Oblique.ttf")
    if reg:
        pdf.add_font("F", "",  reg)
    if bold:
        pdf.add_font("F", "B", bold)
    if ital:
        pdf.add_font("F", "I", ital)
    if reg:
        FONT = "F"
        print(f"[fonte] Unicode TTF registrada: {reg}")
    else:
        print("[fonte] TTF não encontrado — usando Helvetica (sem acentos)")


class PDF(FPDF):
    def fill(self, rgb): self.set_fill_color(*rgb)
    def ink(self, rgb):  self.set_text_color(*rgb)
    def draw(self, rgb): self.set_draw_color(*rgb)

    def band(self, y, h, color):
        self.fill(color)
        self.rect(0, y, 210, h, "F")

    def label(self, texto, color=RED):
        self.set_font(FONT, "B", 8)
        self.ink(color)
        self.cell(0, 5, texto.upper(), **NL)
        self.ln(1)

    def h1(self, texto, color=DARK):
        self.set_font(FONT, "B", 22)
        self.ink(color)
        self.multi_cell(0, 9, texto, **NL)
        self.ln(2)

    def h2(self, texto, color=DARK):
        self.set_font(FONT, "B", 13)
        self.ink(color)
        self.multi_cell(0, 6, texto, **NL)
        self.ln(1)

    def p(self, texto, color=MID, size=10):
        self.set_font(FONT, "", size)
        self.ink(color)
        self.multi_cell(0, 5, texto, **NL)
        self.ln(2)

    def hline(self, color=GRAY, margin=15):
        self.draw(color)
        self.line(margin, self.get_y(), 210 - margin, self.get_y())
        self.ln(4)

    def card(self, titulo, desc, accent=RED):
        x0 = self.get_x()
        y0 = self.get_y()
        w  = self.epw
        self.fill(accent)
        self.rect(x0, y0, 3, 22, "F")
        self.set_xy(x0 + 6, y0 + 2)
        self.set_font(FONT, "B", 10)
        self.ink(DARK)
        self.cell(w - 6, 5, titulo, **NL)
        self.set_x(x0 + 6)
        self.set_font(FONT, "", 8.5)
        self.ink(MID)
        self.multi_cell(w - 6, 4.5, desc, **NL)
        self.ln(4)


def capa(pdf: PDF):
    pdf.add_page()
    pdf.band(0, 297, BEIGE)
    pdf.fill(RED)
    pdf.rect(0, 293, 210, 4, "F")

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=75, y=52, h=24)
        pdf.set_y(84)
    else:
        pdf.set_y(64)

    pdf.set_font(FONT, "", 8)
    pdf.set_text_color(93, 13, 6)
    pdf.cell(0, 6, "APRESENTAÇÃO DE SOLUÇÃO", align="C", **NL)
    pdf.ln(6)

    pdf.set_font(FONT, "B", 36)
    pdf.ink(RED)
    pdf.cell(0, 14, "Automação de", align="C", **NL)
    pdf.ink(VINHO)
    pdf.cell(0, 14, "Notícias", align="C", **NL)
    pdf.ln(8)

    pdf.set_font(FONT, "", 13)
    pdf.ink((100, 40, 38))
    pdf.set_x(30)
    pdf.multi_cell(150, 6,
        "Inteligência de conteúdo automática para escritórios de "
        "contabilidade e advocacia tributária e previdenciária.",
        align="C")
    pdf.ln(14)

    pdf.set_font(FONT, "B", 9)
    pdf.ink(BEIGE)
    bw = 100
    pdf.set_x((210 - bw) / 2)
    pdf.fill(RED)
    pdf.rect((210 - bw) / 2, pdf.get_y(), bw, 8, "F")
    pdf.cell(bw, 8, "Desenvolvido pela Agência FOLKS", align="C", **NL)


def desafio(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("O Desafio", RED)
    pdf.h1("Manter-se atualizado\ndá muito trabalho.")
    pdf.p(
        "O universo contábil e jurídico muda constantemente — novas leis, prazos, "
        "decisões do STJ e STF, instruções normativas da Receita Federal. "
        "Acompanhar tudo isso exige horas de pesquisa diária que poderiam ser "
        "dedicadas aos clientes."
    )
    pdf.hline()

    for titulo, desc in [
        ("Dezenas de fontes",
         "São 8 portais especializados para monitorar diariamente, além de feeds do "
         "governo e do Senado Federal."),
        ("Filtrar o que importa",
         "Nem tudo que é publicado é relevante para o seu nicho. Separar o que "
         "interessa do que não interessa consome tempo."),
        ("Transformar em conteúdo",
         "Depois de selecionar, ainda é preciso transformar a notícia em pauta para "
         "redes sociais, vídeos e comunicados."),
    ]:
        pdf.card(titulo, desc)


def solucao(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("A Solução", RED)
    pdf.h1("Criamos um sistema que faz\nesse trabalho por você.")
    pdf.p(
        "A automação monitora as principais fontes de notícias do setor, filtra apenas "
        "o que é relevante para contabilidade, tributário e previdenciário, e entrega "
        "tudo organizado toda semana diretamente na sua caixa de entrada."
    )
    pdf.hline()

    for titulo, desc in [
        ("Inteligência Artificial",
         "Cada notícia é avaliada por IA especializada em direito tributário e "
         "previdenciário, que define relevância, prioridade e sugere pautas."),
        ("100% Automático",
         "Nenhuma ação manual necessária. O sistema roda sozinho todo dia e envia "
         "o resumo completo toda segunda-feira de manhã."),
        ("Notícias com prioridade",
         "Cada notícia recebe Alto, Médio ou Baixo para que sua equipe saiba "
         "exatamente o que é urgente e o que é informativo."),
        ("Sugestões de pauta prontas",
         "Junto com cada notícia, a IA entrega uma sugestão criativa de pauta "
         "para card ou vídeo curto, já formatada para uso imediato."),
    ]:
        pdf.card(titulo, desc)


def fontes(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("De Onde Vêm as Notícias", RED)
    pdf.h1("8 fontes especializadas\nmonitoradas automaticamente.")
    pdf.p(
        "O sistema acessa diariamente os portais mais relevantes para contabilidade, "
        "tributário, legislação e direito previdenciário — incluindo fontes oficiais."
    )

    lista = [
        ("Receita Federal",                       "Tributário · Oficial Federal"),
        ("Portal Contábeis",                      "Contabilidade"),
        ("Notícias Fiscais",                      "Tributário"),
        ("CFC — Conselho Federal de Contabilidade","Contabilidade · Oficial"),
        ("JOTA Jornalismo",                       "Jurídico"),
        ("Senado Federal",                        "Legislação · Oficial Federal"),
        ("SEFAZ-CE",                              "Legislação · Oficial Ceará"),
        ("Prefeitura de Fortaleza",               "Legislação · Oficial Municipal"),
        ("NewsAPI",                               "Tributário · Buscador nacional"),
    ]

    col_w  = (pdf.epw - 8) / 2
    x_left  = pdf.l_margin
    x_right = pdf.l_margin + col_w + 8
    y_start = pdf.get_y()

    for i, (nome, cat) in enumerate(lista):
        x = x_left if i % 2 == 0 else x_right
        y = y_start + (i // 2) * 18
        pdf.fill(RED);  pdf.rect(x, y, 3, 14, "F")
        pdf.fill(GRAY); pdf.rect(x + 3, y, col_w - 3, 14, "F")
        pdf.set_xy(x + 6, y + 2)
        pdf.set_font(FONT, "B", 9); pdf.ink(DARK)
        pdf.cell(col_w - 8, 4.5, nome, **NL)
        pdf.set_x(x + 6)
        pdf.set_font(FONT, "", 7.5); pdf.ink(LIGHT)
        pdf.cell(col_w - 8, 4, cat, **NL)


def fluxo(pdf: PDF):
    pdf.add_page()
    pdf.band(0, 148, VINHO)
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.set_font(FONT, "B", 8)
    pdf.ink((180, 140, 130))
    pdf.cell(0, 5, "COMO FUNCIONA", **NL)
    pdf.ln(1)
    pdf.set_font(FONT, "B", 20)
    pdf.ink(BEIGE)
    pdf.cell(0, 9, "Do monitoramento ao seu e-mail", **NL)
    pdf.ink((232, 121, 94))
    pdf.cell(0, 9, "em 4 etapas.", **NL)
    pdf.ln(6)

    etapas = [
        ("1", "Coleta",   "Todo dia às 7h o sistema\nacessa os 8 portais"),
        ("2", "Filtro",   "Apenas notícias do nicho\ncontábil e jurídico passam"),
        ("3", "IA",       "A IA avalia, prioriza\ne gera sugestão de pauta"),
        ("4", "Entrega",  "Toda segunda às 8h o\ndigest chega no seu e-mail"),
    ]
    step_w = pdf.epw / 4
    y_step = pdf.get_y()
    for i, (num, titulo, desc) in enumerate(etapas):
        x = pdf.l_margin + i * step_w
        pdf.fill(RED)
        pdf.ellipse(x + step_w / 2 - 9, y_step, 18, 10, "F")
        pdf.set_xy(x, y_step)
        pdf.set_font(FONT, "B", 11); pdf.ink(BEIGE)
        pdf.cell(step_w, 10, num, align="C")
        if i < 3:
            pdf.set_font(FONT, "", 12); pdf.ink((200, 160, 150))
            pdf.set_xy(x + step_w - 4, y_step + 1)
            pdf.cell(8, 8, ">", align="C")
        pdf.set_xy(x, y_step + 12)
        pdf.set_font(FONT, "B", 9); pdf.ink(BEIGE)
        pdf.cell(step_w, 5, titulo, align="C")
        pdf.set_xy(x + 2, y_step + 18)
        pdf.set_font(FONT, "", 7.5); pdf.ink((200, 185, 175))
        pdf.multi_cell(step_w - 4, 4, desc, align="C",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(148 + 10)
    pdf.set_margins(18, 0, 18)
    pdf.label("Calendário de Execução", RED)
    pdf.h1("Automático. Toda semana. Sem falhas.")

    half  = (pdf.epw - 8) / 2
    y_cal = pdf.get_y()

    for i, (hora, titulo, desc, freq) in enumerate([
        ("07:00", "Coleta de Notícias",
         "O sistema busca notícias em todos os portais monitorados e as "
         "salva com prioridade classificada pela IA.",
         "TODO DIA"),
        ("08:00", "Envio do Digest Semanal",
         "As melhores notícias da semana são compiladas e enviadas por e-mail "
         "com PDF e planilha de pauta para a equipe de conteúdo.",
         "TODA SEGUNDA-FEIRA"),
    ]):
        x = pdf.l_margin + i * (half + 8)
        pdf.fill(GRAY); pdf.rect(x, y_cal, half, 52, "F")
        pdf.fill(RED);  pdf.rect(x, y_cal, half, 3, "F")

        pdf.set_xy(x + 6, y_cal + 7)
        pdf.set_font(FONT, "B", 22); pdf.ink(RED)
        pdf.cell(half - 8, 10, hora)

        pdf.set_xy(x + 6, y_cal + 19)
        pdf.set_font(FONT, "B", 10); pdf.ink(DARK)
        pdf.multi_cell(half - 8, 5, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(x + 6, pdf.get_y())
        pdf.set_font(FONT, "", 8); pdf.ink(MID)
        pdf.multi_cell(half - 8, 4.5, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(x + 6, y_cal + 44)
        pdf.fill(RED)
        fw = pdf.get_string_width(freq) + 8
        pdf.rect(x + 6, y_cal + 44, fw, 5.5, "F")
        pdf.set_font(FONT, "B", 7); pdf.ink(BEIGE)
        pdf.cell(fw, 5.5, freq)


def entregaveis(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("O Que Você Recebe", RED)
    pdf.h1("Três entregas toda\nsegunda-feira.")
    pdf.p("Um único e-mail com tudo que sua equipe precisa para a semana de conteúdo.")
    pdf.hline()

    for icone, titulo, desc in [
        ("[ E-MAIL HTML ]",
         "E-mail HTML formatado",
         "E-mail visualmente organizado com todas as notícias da semana, agrupadas por "
         "categoria e ordenadas por prioridade. Cada notícia vem com badge de "
         "prioridade colorido, resumo, fonte, data e sugestão de pauta."),
        ("[ PDF ]",
         "PDF para arquivo e impressão",
         "Versão em PDF do digest completo, ideal para arquivamento, leitura offline "
         "ou distribuição interna. Contém todas as notícias com prioridades e "
         "sugestões de pauta."),
        ("[ EXCEL ]",
         "Planilha Excel — Pauta da Semana",
         "Planilha pronta para uso pela equipe de conteúdo, com colunas de formato "
         "sugerido (Feed, Reels, Stories), gancho da legenda, desenvolvimento, CTA, "
         "hashtags e sugestão visual. Basta abrir e começar a produzir."),
    ]:
        y0 = pdf.get_y()
        pdf.fill(GRAY); pdf.rect(pdf.l_margin, y0, pdf.epw, 32, "F")
        pdf.fill(RED);  pdf.rect(pdf.l_margin, y0, 3, 32, "F")
        pdf.set_xy(pdf.l_margin + 8, y0 + 4)
        pdf.set_font(FONT, "B", 7); pdf.ink(RED)
        pdf.cell(30, 5, icone)
        pdf.set_xy(pdf.l_margin + 8, y0 + 10)
        pdf.set_font(FONT, "B", 11); pdf.ink(DARK)
        pdf.multi_cell(pdf.epw - 10, 5.5, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(pdf.l_margin + 8, pdf.get_y())
        pdf.set_font(FONT, "", 8.5); pdf.ink(MID)
        pdf.multi_cell(pdf.epw - 10, 4.5, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)


def categorias_e_prioridades(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("Categorias de Notícias", RED)
    pdf.h1("Tudo organizado por área de atuação.")
    pdf.p("As notícias são classificadas em quatro categorias cobrindo as principais áreas do escritório.")

    cats = [
        ("Tributário",    CAT_CORES["Tributário"],
         "IRPF, IRPJ, ICMS, ISS\nPIS/COFINS, CSLL\nSimples Nacional\nReforma tributária\nReceita Federal\nPrazos e obrigações\neSocial, SPED, NF-e"),
        ("Legislação",    CAT_CORES["Legislação"],
         "Novas leis e decretos\nInstruções normativas\nProjetos de lei\nSEFAZ-CE\nPrefeitura de Fortaleza\nLegislação previdenciária"),
        ("Contabilidade", CAT_CORES["Contabilidade"],
         "Normas do CFC e CRC\nAuditoria fiscal\nEscrituração contábil\nPlanejamento contábil\nNovas obrigações\nTecnologia contábil"),
        ("Jurídico",      CAT_CORES["Jurídico"],
         "Decisões STF e STJ\nINSS e aposentadoria\nBenefícios previdenciários\nDireito empresarial\nCARF\nPlanejamento sucessório"),
    ]
    cat_w  = (pdf.epw - 6) / 4
    y_cat  = pdf.get_y()
    for i, (nome, cor, itens) in enumerate(cats):
        x = pdf.l_margin + i * (cat_w + 2)
        pdf.fill(GRAY); pdf.rect(x, y_cat, cat_w, 52, "F")
        pdf.fill(cor);  pdf.rect(x, y_cat, cat_w, 4, "F")
        pdf.set_xy(x + 4, y_cat + 6)
        pdf.set_font(FONT, "B", 9); pdf.ink(cor)
        pdf.cell(cat_w - 6, 5, nome)
        pdf.set_xy(x + 4, y_cat + 13)
        pdf.set_font(FONT, "", 7.5); pdf.ink(MID)
        pdf.multi_cell(cat_w - 6, 4.5, itens, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(y_cat + 58)
    pdf.label("Sistema de Prioridades", RED)
    pdf.h1("Saiba o que é urgente sem precisar ler tudo.")

    for badge_txt, badge_fg, badge_bg, titulo, desc in [
        ("ALTO",  (169,23,10),  (255,236,236),
         "Impacto imediato — ação necessária",
         "Nova lei publicada, prazo fiscal urgente, decisão definitiva do STF/STJ, "
         "instrução normativa já em vigor. Exige comunicação rápida com clientes."),
        ("MÉDIO", (230,81,0),   (255,248,225),
         "Relevante — acompanhar de perto",
         "Projeto de lei em votação, orientação da Receita ou INSS, nova tese "
         "tributária em discussão nos tribunais. Importante, sem urgência imediata."),
        ("BAIXO", (117,117,117),(245,245,245),
         "Informativo — contexto e educação",
         "Retrospectivas, tendências do setor, curiosidades tributárias. Excelente "
         "para pautas de redes sociais mais leves e didáticas."),
    ]:
        y0 = pdf.get_y()
        pdf.fill(GRAY); pdf.rect(pdf.l_margin, y0, pdf.epw, 20, "F")
        pdf.fill(badge_bg)
        bw = 22
        pdf.rect(pdf.l_margin + 4, y0 + 6, bw, 7, "F")
        pdf.set_xy(pdf.l_margin + 4, y0 + 6)
        pdf.set_font(FONT, "B", 7); pdf.ink(badge_fg)
        pdf.cell(bw, 7, badge_txt, align="C")
        pdf.set_xy(pdf.l_margin + 30, y0 + 3)
        pdf.set_font(FONT, "B", 10); pdf.ink(DARK)
        pdf.cell(pdf.epw - 32, 5, titulo)
        pdf.set_xy(pdf.l_margin + 30, y0 + 9)
        pdf.set_font(FONT, "", 8); pdf.ink(MID)
        pdf.multi_cell(pdf.epw - 32, 4, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)


def aplicacoes(pdf: PDF):
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_y(18)

    pdf.label("Aplicações Práticas", RED)
    pdf.h1("O que sua equipe pode\nfazer com isso.")
    pdf.p(
        "O digest não é só informação — é a base de uma estratégia de "
        "conteúdo completa para o escritório."
    )
    pdf.hline()

    for titulo, desc in [
        ("Conteúdo para redes sociais",
         "Cada notícia vem com sugestão de gancho, desenvolvimento e CTA prontos "
         "para virar um card ou Reels no Instagram e LinkedIn."),
        ("Roteiros de vídeo",
         "Notícias de prioridade Alta e Média são ótimas para vídeos curtos de "
         "posicionamento e atualização para clientes."),
        ("Planejamento semanal",
         "A planilha Excel entregue toda segunda serve como grade de pauta pronta "
         "para a semana, eliminando a reunião de briefing."),
        ("Comunicados aos clientes",
         "Notícias de prioridade Alta indicam quando o escritório precisa alertar "
         "sua base sobre mudanças urgentes."),
        ("Arquivo de referência",
         "O PDF semanal forma um acervo histórico de notícias relevantes do setor, "
         "útil para consulta e comparação ao longo do tempo."),
        ("Autoridade de mercado",
         "Publicar conteúdo atualizado e relevante posiciona o escritório como "
         "referência no segmento para clientes e prospects."),
    ]:
        pdf.card(titulo, desc)

    pdf.ln(4)
    pdf.hline(RED)
    pdf.set_font(FONT, "", 9); pdf.ink(LIGHT)
    pdf.cell(0, 5,
        "Automatizando o que pode ser automatizado para você focar no que realmente importa.",
        align="C", **NL)
    pdf.set_font(FONT, "B", 9); pdf.ink(RED)
    pdf.cell(0, 5, "Agência FOLKS", align="C", **NL)


def main():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    _setup_fonts(pdf)

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
