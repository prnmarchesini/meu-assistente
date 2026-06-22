"""Rate limit simples em memoria (janela deslizante).

Suficiente para uma instancia (caso do MVP no Railway). Para multiplas instancias,
trocar por um backend compartilhado (ex.: Redis).
"""
import time
from collections import defaultdict, deque

_baldes: dict[str, deque] = defaultdict(deque)


def permitir(chave: str, limite: int = 30, janela_s: int = 60) -> bool:
    agora = time.time()
    dq = _baldes[chave]
    while dq and dq[0] <= agora - janela_s:
        dq.popleft()
    if len(dq) >= limite:
        return False
    dq.append(agora)
    return True
