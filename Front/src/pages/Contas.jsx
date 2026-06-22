import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Contas() {
  const [itens, setItens] = useState([])
  const [nome, setNome] = useState('')
  const [tipo, setTipo] = useState('corrente')
  const [erro, setErro] = useState('')

  const carregar = () => api.get('/contas').then(setItens).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  async function criar(e) {
    e.preventDefault()
    setErro('')
    try {
      await api.post('/contas', { nome, tipo })
      setNome('')
      carregar()
    } catch (e) { setErro(e.message) }
  }

  async function excluir(id) {
    await api.del(`/contas/${id}`)
    carregar()
  }

  return (
    <div>
      <h1>Contas</h1>
      {erro && <p className="erro">{erro}</p>}
      <form className="linha" onSubmit={criar}>
        <input placeholder="Nome da conta" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="corrente">Corrente</option>
          <option value="poupanca">Poupança</option>
          <option value="dinheiro">Dinheiro</option>
        </select>
        <button>Adicionar</button>
      </form>
      <ul className="lista">
        {itens.map((c) => (
          <li key={c.id}>{c.nome} <small>({c.tipo || 'sem tipo'})</small><button onClick={() => excluir(c.id)}>excluir</button></li>
        ))}
      </ul>
    </div>
  )
}
