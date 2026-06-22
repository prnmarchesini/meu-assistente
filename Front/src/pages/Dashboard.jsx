import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const brl = (v) => Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Dashboard() {
  const [dados, setDados] = useState(null)
  const [erro, setErro] = useState('')
  const [precisaSeed, setPrecisaSeed] = useState(false)

  async function carregar() {
    try {
      const [d, cats] = await Promise.all([api.get('/dashboard'), api.get('/categorias')])
      setDados(d)
      setPrecisaSeed(cats.length === 0)
    } catch (e) {
      setErro(e.message)
    }
  }

  useEffect(() => {
    carregar()
  }, [])

  async function seed() {
    await api.post('/seed-categorias', {})
    setPrecisaSeed(false)
  }

  if (erro) return <p className="erro">{erro}</p>
  if (!dados) return <p>Carregando…</p>

  return (
    <div>
      <h1>Dashboard</h1>
      {precisaSeed && (
        <div className="aviso">
          Começar com categorias comuns (Mercado, Transporte, Saúde…)?{' '}
          <button onClick={seed}>Criar categorias</button>
        </div>
      )}
      <div className="cards">
        <div className="card">
          <span>Total gasto no mês</span>
          <strong>{brl(dados.total_mes)}</strong>
        </div>
        <div className="card">
          <span>Próxima fatura</span>
          {dados.proxima_fatura ? (
            <strong>
              {dados.proxima_fatura.cartao_nome} — {brl(dados.proxima_fatura.total)}<br />
              <small>vence {dados.proxima_fatura.vencimento}</small>
            </strong>
          ) : (
            <strong>—</strong>
          )}
        </div>
        <div className="card">
          <span>Garantias vencendo (30 dias)</span>
          <strong>{dados.garantias_a_vencer.length}</strong>
        </div>
      </div>

      <h2>Últimas despesas</h2>
      <table className="tabela">
        <thead><tr><th>Data</th><th>Descrição</th><th>Categoria</th><th>Valor</th></tr></thead>
        <tbody>
          {dados.ultimas_despesas.map((d) => (
            <tr key={d.id}>
              <td>{d.data}</td>
              <td>{d.descricao}</td>
              <td>{d.categoria_nome || '—'}</td>
              <td>{brl(d.valor_total)}</td>
            </tr>
          ))}
          {dados.ultimas_despesas.length === 0 && (
            <tr><td colSpan={4}>Nenhuma despesa ainda.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
