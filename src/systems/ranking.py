import os
from datetime import datetime

_PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
RANKING_FILE = os.path.join(_PROJ_ROOT, "data", "ranking.txt")

def carregar_ranking(max_registros=5):
    if not os.path.exists(RANKING_FILE):
        return []
    regs = []
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split(";")
            if len(partes) >= 3:
                try:
                    regs.append({
                        "nome":  partes[0],
                        "pontos": int(partes[1]),
                        "data":  partes[2],
                    })
                except ValueError:
                    pass
    regs.sort(key=lambda r: r["pontos"], reverse=True)
    return regs[:max_registros]

def salvar_ranking(nome, pontos):
    nome = (nome or "Anônimo").replace(";", "-")[:20]
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    os.makedirs(os.path.dirname(RANKING_FILE), exist_ok=True)
    with open(RANKING_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nome};{pontos};{data}\n")

def melhor_pontuacao():
    r = carregar_ranking(1)
    return r[0]["pontos"] if r else 0