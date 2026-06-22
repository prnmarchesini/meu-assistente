import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const brl = (v) => Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Faturas() {
  const [faturas, setFaturas] = useState([])
  const [erro, setErro] = useState('')

  const carregar = () => api.get('/faturas').then(setFaturas).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  async function marcarPaga(cartao_id, competencia) {
    try {
      await api.post('/faturas/marcar-paga', { cartao_id, competencia })
      carregar()
    } catch (e) { setErro(e.message) }
  }

  return (
    <div>
      <h1>Faturas</h1>
      {erro && <p className="erro">{erro}</p>}
      <table className="tabela">
        <thead><tr><th>Cartão</th><th>Competência</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {faturas.map((f) => (
            <tr key={f.id}>
              <td>{f.cartao_nome}</td>
              <td>{f.competencia}</td>
              <td>{f.status}</td>
              <td>
                {f.status === 'aberta' && (
                  <button onClick={() => marcarPaga(f.cartao_id, f.competencia)}>marcar paga</button>
                )}
              </td>
            </tr>
          ))}
          {faturas.length === 0 && <tr><td colSpan={4}>Nenhuma fatura em aberto.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
