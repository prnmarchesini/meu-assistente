import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const hoje = () => new Date().toISOString().slice(0, 10)

export default function NovaDespesa() {
  const [contas, setContas] = useState([])
  const [cartoes, setCartoes] = useState([])
  const [categorias, setCategorias] = useState([])
  const [form, setForm] = useState({
    descricao: '', valor_total: '', data: hoje(), forma_pagamento: 'conta',
    conta_id: '', cartao_id: '', num_parcelas: 1, categoria_id: '',
  })
  const [erro, setErro] = useState('')
  const [ok, setOk] = useState('')

  useEffect(() => {
    api.get('/contas').then(setContas)
    api.get('/cartoes').then(setCartoes)
    api.get('/categorias').then(setCategorias)
  }, [])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  const isCartao = form.forma_pagamento === 'cartao'

  async function onSubmit(e) {
    e.preventDefault()
    setErro(''); setOk('')
    try {
      const payload = {
        descricao: form.descricao,
        valor_total: form.valor_total,
        data: form.data,
        forma_pagamento: form.forma_pagamento,
        categoria_id: form.categoria_id || null,
        conta_id: isCartao ? null : form.conta_id || null,
        cartao_id: isCartao ? form.cartao_id || null : null,
        num_parcelas: isCartao ? Number(form.num_parcelas) : 1,
      }
      const r = await api.post('/despesas', payload)
      setOk(`Despesa criada${r.parcelas.length ? ` em ${r.parcelas.length}x` : ''}.`)
      setForm({ ...form, descricao: '', valor_total: '', num_parcelas: 1 })
    } catch (e) { setErro(e.message) }
  }

  return (
    <div>
      <h1>Lançar despesa</h1>
      {erro && <p className="erro">{erro}</p>}
      {ok && <p className="ok">{ok}</p>}
      <form className="grade" onSubmit={onSubmit}>
        <label>Descrição<input value={form.descricao} onChange={set('descricao')} required /></label>
        <label>Valor<input type="number" step="0.01" min="0.01" value={form.valor_total} onChange={set('valor_total')} required /></label>
        <label>Data<input type="date" value={form.data} onChange={set('data')} required /></label>
        <label>Forma de pagamento
          <select value={form.forma_pagamento} onChange={set('forma_pagamento')}>
            <option value="conta">Conta</option>
            <option value="cartao">Cartão</option>
          </select>
        </label>
        {isCartao ? (
          <>
            <label>Cartão
              <select value={form.cartao_id} onChange={set('cartao_id')} required>
                <option value="">Selecione…</option>
                {cartoes.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
              </select>
            </label>
            <label>Parcelas<input type="number" min={1} value={form.num_parcelas} onChange={set('num_parcelas')} /></label>
          </>
        ) : (
          <label>Conta
            <select value={form.conta_id} onChange={set('conta_id')} required>
              <option value="">Selecione…</option>
              {contas.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          </label>
        )}
        <label>Categoria (opcional)
          <select value={form.categoria_id} onChange={set('categoria_id')}>
            <option value="">Sem categoria</option>
            {categorias.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
          </select>
        </label>
        <button>Salvar despesa</button>
      </form>
    </div>
  )
}
