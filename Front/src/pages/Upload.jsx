import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')
  const [resultado, setResultado] = useState(null) // {documento, sugestao_despesa}
  const [revisao, setRevisao] = useState(null) // form editavel da despesa
  const [contas, setContas] = useState([])
  const [cartoes, setCartoes] = useState([])
  const [ok, setOk] = useState('')

  useEffect(() => {
    api.get('/contas').then(setContas).catch(() => {})
    api.get('/cartoes').then(setCartoes).catch(() => {})
  }, [])

  async function enviar(e) {
    e.preventDefault()
    setErro(''); setOk('')
    if (!file) return
    setEnviando(true)
    try {
      const r = await api.upload('/documentos/upload', file)
      setResultado(r)
      const s = r.sugestao_despesa
      setRevisao({
        descricao: s.descricao || '',
        valor_total: s.valor_total ?? '',
        data: s.data || new Date().toISOString().slice(0, 10),
        forma_pagamento: 'conta',
        conta_id: '',
        cartao_id: '',
        num_parcelas: 1,
      })
    } catch (e) {
      setErro(e.message)
    } finally {
      setEnviando(false)
    }
  }

  const set = (k) => (e) => setRevisao({ ...revisao, [k]: e.target.value })
  const isCartao = revisao?.forma_pagamento === 'cartao'

  async function confirmar(e) {
    e.preventDefault()
    setErro(''); setOk('')
    try {
      const despesa = await api.post('/despesas', {
        descricao: revisao.descricao,
        valor_total: revisao.valor_total,
        data: revisao.data,
        forma_pagamento: revisao.forma_pagamento,
        conta_id: isCartao ? null : revisao.conta_id || null,
        cartao_id: isCartao ? revisao.cartao_id || null : null,
        num_parcelas: isCartao ? Number(revisao.num_parcelas) : 1,
      })
      await api.post(`/documentos/${resultado.documento.id}/vincular`, {
        despesa_id: despesa.despesa.id,
      })
      setOk('Despesa criada e vinculada ao documento!')
      setResultado(null); setRevisao(null); setFile(null)
    } catch (e) {
      setErro(e.message)
    }
  }

  return (
    <div>
      <h1>Enviar nota / documento</h1>
      {erro && <p className="erro">{erro}</p>}
      {ok && <p className="ok">{ok}</p>}

      {!revisao && (
        <form className="linha" onSubmit={enviar}>
          <input type="file" accept="application/pdf,image/*" onChange={(e) => setFile(e.target.files[0])} required />
          <button disabled={enviando}>{enviando ? 'Processando…' : 'Enviar'}</button>
        </form>
      )}

      {revisao && (
        <form className="grade" onSubmit={confirmar}>
          <p style={{ gridColumn: '1 / -1' }}>
            Confira os dados extraídos pela IA antes de salvar (decisão 5/6):
          </p>
          <label>Descrição<input value={revisao.descricao} onChange={set('descricao')} required /></label>
          <label>Valor<input type="number" step="0.01" value={revisao.valor_total} onChange={set('valor_total')} required /></label>
          <label>Data<input type="date" value={revisao.data} onChange={set('data')} required /></label>
          <label>Forma de pagamento
            <select value={revisao.forma_pagamento} onChange={set('forma_pagamento')}>
              <option value="conta">Conta</option>
              <option value="cartao">Cartão</option>
            </select>
          </label>
          {isCartao ? (
            <>
              <label>Cartão
                <select value={revisao.cartao_id} onChange={set('cartao_id')} required>
                  <option value="">Selecione…</option>
                  {cartoes.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
                </select>
              </label>
              <label>Parcelas<input type="number" min={1} value={revisao.num_parcelas} onChange={set('num_parcelas')} /></label>
            </>
          ) : (
            <label>Conta
              <select value={revisao.conta_id} onChange={set('conta_id')} required>
                <option value="">Selecione…</option>
                {contas.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
              </select>
            </label>
          )}
          <button>Confirmar e salvar despesa</button>
        </form>
      )}
    </div>
  )
}
