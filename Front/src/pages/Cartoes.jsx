import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const vazio = { nome: '', dia_fechamento: 1, dia_vencimento: 10, bandeira: '', limite: '' }

export default function Cartoes() {
  const [itens, setItens] = useState([])
  const [form, setForm] = useState(vazio)
  const [erro, setErro] = useState('')

  const carregar = () => api.get('/cartoes').then(setItens).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  async function criar(e) {
    e.preventDefault()
    setErro('')
    try {
      await api.post('/cartoes', {
        nome: form.nome,
        dia_fechamento: Number(form.dia_fechamento),
        dia_vencimento: Number(form.dia_vencimento),
        bandeira: form.bandeira || null,
        limite: form.limite ? Number(form.limite) : null,
      })
      setForm(vazio)
      carregar()
    } catch (e) { setErro(e.message) }
  }

  async function excluir(id) {
    await api.del(`/cartoes/${id}`)
    carregar()
  }

  return (
    <div>
      <h1>Cartões</h1>
      {erro && <p className="erro">{erro}</p>}
      <form className="grade" onSubmit={criar}>
        <label>Nome<input value={form.nome} onChange={set('nome')} required /></label>
        <label>Dia fechamento<input type="number" min={1} max={31} value={form.dia_fechamento} onChange={set('dia_fechamento')} required /></label>
        <label>Dia vencimento<input type="number" min={1} max={31} value={form.dia_vencimento} onChange={set('dia_vencimento')} required /></label>
        <label>Bandeira<input value={form.bandeira} onChange={set('bandeira')} /></label>
        <label>Limite<input type="number" step="0.01" value={form.limite} onChange={set('limite')} /></label>
        <button>Adicionar cartão</button>
      </form>
      <ul className="lista">
        {itens.map((c) => (
          <li key={c.id}>
            {c.nome} <small>fecha dia {c.dia_fechamento}, vence dia {c.dia_vencimento}</small>
            <button onClick={() => excluir(c.id)}>excluir</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
