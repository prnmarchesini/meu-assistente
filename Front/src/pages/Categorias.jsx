import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Categorias() {
  const [itens, setItens] = useState([])
  const [nome, setNome] = useState('')
  const [erro, setErro] = useState('')

  const carregar = () => api.get('/categorias').then(setItens).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  async function criar(e) {
    e.preventDefault()
    setErro('')
    try {
      await api.post('/categorias', { nome })
      setNome('')
      carregar()
    } catch (e) { setErro(e.message) }
  }

  async function excluir(id) {
    await api.del(`/categorias/${id}`)
    carregar()
  }

  return (
    <div>
      <h1>Categorias</h1>
      {erro && <p className="erro">{erro}</p>}
      <form className="linha" onSubmit={criar}>
        <input placeholder="Nova categoria" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <button>Adicionar</button>
      </form>
      <ul className="lista">
        {itens.map((c) => (
          <li key={c.id}>{c.nome}<button onClick={() => excluir(c.id)}>excluir</button></li>
        ))}
      </ul>
    </div>
  )
}
