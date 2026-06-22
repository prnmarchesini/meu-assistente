"""Testes do vinculo e do webhook do Telegram (Passo 6).

Sem token real: o envio de mensagens e o orquestrador sao monkeypatchados.
O vinculo e exercitado contra o banco (transacao revertida).
"""
import pytest

from app.servicos import telegram_vinculo as tv
from app.servicos.comuns import RegraNegocioError
from app.telegram import webhook


def test_gerar_e_consumir_codigo_vincula(cur, user_id):
    cod = tv.gerar_codigo(cur, user_id)
    assert len(cod["codigo"]) == 6
    vinculado = tv.consumir_codigo(cur, cod["codigo"], 999001)
    assert vinculado == user_id
    assert tv.usuario_por_chat(cur, 999001) == user_id
    assert tv.status(cur, user_id)["vinculado"] is True


def test_codigo_uso_unico(cur, user_id):
    cod = tv.gerar_codigo(cur, user_id)
    tv.consumir_codigo(cur, cod["codigo"], 999002)
    with pytest.raises(RegraNegocioError):
        tv.consumir_codigo(cur, cod["codigo"], 999003)  # ja usado


def test_codigo_expirado(cur, user_id):
    cod = tv.gerar_codigo(cur, user_id)
    cur.execute("update telegram_codigos set expira_em = now() - interval '1 minute' where id=%s", (cod["id"],))
    with pytest.raises(RegraNegocioError):
        tv.consumir_codigo(cur, cod["codigo"], 999004)


def test_desvincular(cur, user_id):
    cod = tv.gerar_codigo(cur, user_id)
    tv.consumir_codigo(cur, cod["codigo"], 999005)
    tv.desvincular(cur, user_id)
    assert tv.usuario_por_chat(cur, 999005) is None
    assert tv.status(cur, user_id)["vinculado"] is False


# ── Webhook ──
@pytest.fixture()
def captura(monkeypatch):
    enviadas = []
    monkeypatch.setattr(webhook.bot, "enviar_mensagem", lambda chat_id, texto: enviadas.append((chat_id, texto)))
    return enviadas


def test_webhook_chat_nao_vinculado_instrui(cur, captura):
    webhook.handle_update(cur, {"message": {"chat": {"id": 555}, "text": "ola"}})
    assert captura and "vinculado" in captura[-1][1].lower()


def test_webhook_start_com_codigo_vincula(cur, user_id, captura):
    cod = tv.gerar_codigo(cur, user_id)
    webhook.handle_update(cur, {"message": {"chat": {"id": 556}, "text": f"/start {cod['codigo']}"}})
    assert "vinculada" in captura[-1][1].lower()
    assert tv.usuario_por_chat(cur, 556) == user_id


def test_webhook_texto_delega_ao_orquestrador(cur, user_id, captura, monkeypatch):
    cod = tv.gerar_codigo(cur, user_id)
    tv.consumir_codigo(cur, cod["codigo"], 557)
    monkeypatch.setattr(
        webhook.orquestrador, "conversar",
        lambda cur, uid, msg, hist: {"resposta": "resposta-stub", "historico": [{"role": "user", "content": msg}]},
    )
    webhook.handle_update(cur, {"message": {"chat": {"id": 557}, "text": "quanto gastei?"}})
    assert captura[-1] == (557, "resposta-stub")
