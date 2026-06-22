import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Documentos() {
  const [docs, setDocs] = useState([])
  const [garantias, setGarantias] = useState([])
  const [consulta, setConsulta] = useState('')
  const [achados, setAchados] = useState(null)
  const [erro, setErro] = useState('')

  useEffect(() => {
    api.get('/documentos').then(setDocs).catch((e) => setErro(e.message))
    api.get('/garantias?dias=30').then(setGarantias).catch(() => {})
  }, [])

  async function buscar(e) {
    e.preventDefault()
    setErro('')
    try {
      setAchados(await api.post('/documentos/buscar', { consulta }))
    } catch (e) { setErro(e.message) }
  }

  return (
    <div>
      <h1>Documentos</h1>
      {erro && <p className="erro">{erro}</p>}

      <h2>Busca semântica</h2>
      <form className="linha" onSubmit={buscar}>
        <input placeholder="ex: nota do mercado de março" value={consulta} onChange={(e) => setConsulta(e.target.value)} required />
        <button>Buscar</button>
      </form>
      {achados && (
        <ul className="lista">
          {achados.map((a) => (
            <li key={a.id}>{a.fornecedor || '—'} <small>{a.tipo_documento} · {a.data_documento || ''}</small></li>
          ))}
          {achados.length === 0 && <li>Nada encontrado.</li>}
        </ul>
      )}

      <h2>Garantias vencendo (30 dias)</h2>
      <ul className="lista">
        {garantias.map((g) => (
          <li key={g.id}>{g.fornecedor || '—'} <small>fim {g.fim_garantia}</small></li>
        ))}
        {garantias.length === 0 && <li>Nenhuma garantia vencendo.</li>}
      </ul>

      <h2>Todos os documentos</h2>
      <table className="tabela">
        <thead><tr><th>Fornecedor</th><th>Tipo</th><th>Data</th><th>Garantia</th></tr></thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id}>
              <td>{d.fornecedor || '—'}</td>
              <td>{d.tipo_documento || '—'}</td>
              <td>{d.data_documento || '—'}</td>
              <td>{d.fim_garantia || '—'}</td>
            </tr>
          ))}
          {docs.length === 0 && <tr><td colSpan={4}>Nenhum documento enviado.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
