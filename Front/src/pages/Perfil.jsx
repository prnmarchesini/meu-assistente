import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../auth/AuthContext'

export default function Perfil() {
  const { user } = useAuth()
  const [status, setStatus] = useState(null)
  const [codigo, setCodigo] = useState(null)
  const [erro, setErro] = useState('')

  const carregar = () => api.get('/telegram/status').then(setStatus).catch((e) => setErro(e.message))
  useEffect(() => { carregar() }, [])

  async function gerar() {
    setErro('')
    try {
      setCodigo(await api.post('/telegram/gerar-codigo'))
    } catch (e) { setErro(e.message) }
  }

  async function desvincular() {
    setErro('')
    try {
      await api.post('/telegram/desvincular')
      setCodigo(null)
      carregar()
    } catch (e) { setErro(e.message) }
  }

  return (
    <div>
      <h1>Perfil</h1>
      <p>{user?.email}</p>
      {erro && <p className="erro">{erro}</p>}

      <h2>Telegram</h2>
      {status?.vinculado ? (
        <>
          <p className="ok">Telegram vinculado ✓</p>
          <button onClick={desvincular} style={{ background: '#ef4444' }}>Desvincular Telegram</button>
        </>
      ) : (
        <>
          <p>Vincule seu Telegram para lançar gastos por mensagem ou áudio.</p>
          <button onClick={gerar}>Gerar código de vínculo</button>
          {codigo && (
            <div className="aviso" style={{ marginTop: 12 }}>
              Seu código: <strong style={{ fontSize: 20 }}>{codigo.codigo}</strong><br />
              No Telegram, abra o bot e envie: <code>/start {codigo.codigo}</code>
              {codigo.deep_link && (
                <div><a href={codigo.deep_link} target="_blank" rel="noreferrer">Abrir no Telegram</a></div>
              )}
              <div><small>Expira em ~10 minutos e só pode ser usado uma vez.</small></div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
