import { useRef, useState } from 'react'
import { api } from '../lib/api'

export default function Chat() {
  const [mensagens, setMensagens] = useState([]) // {role, content} para exibir
  const [historico, setHistorico] = useState([])
  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')
  const fim = useRef(null)

  async function enviar(e) {
    e.preventDefault()
    if (!texto.trim()) return
    setErro('')
    const msg = texto
    setTexto('')
    setMensagens((m) => [...m, { role: 'user', content: msg }])
    setEnviando(true)
    try {
      const r = await api.post('/chat', { mensagem: msg, historico })
      setHistorico(r.historico)
      setMensagens((m) => [...m, { role: 'assistant', content: r.resposta }])
      setTimeout(() => fim.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (e) {
      setErro(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div>
      <h1>Assistente</h1>
      <p style={{ color: '#6b7280' }}>
        Ex.: "Gastei 200 no mercado, 2x no Nubank" · "Quanto gastei esse mês?"
      </p>
      {erro && <p className="erro">{erro}</p>}
      <div className="chat">
        {mensagens.map((m, i) => (
          <div key={i} className={`bolha ${m.role}`}>{m.content}</div>
        ))}
        {enviando && <div className="bolha assistant">…</div>}
        <div ref={fim} />
      </div>
      <form className="linha" onSubmit={enviar}>
        <input
          style={{ flex: 1 }}
          placeholder="Escreva uma mensagem…"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <button disabled={enviando}>Enviar</button>
      </form>
    </div>
  )
}
