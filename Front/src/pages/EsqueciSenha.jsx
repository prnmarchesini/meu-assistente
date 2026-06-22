import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function EsqueciSenha() {
  const { resetarSenha } = useAuth()
  const [email, setEmail] = useState('')
  const [enviado, setEnviado] = useState(false)
  const [erro, setErro] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    setErro('')
    const { error } = await resetarSenha(email)
    if (error) setErro(error.message)
    else setEnviado(true)
  }

  return (
    <div className="centro">
      <form className="cartao" onSubmit={onSubmit}>
        <h1>Recuperar senha</h1>
        {enviado ? (
          <p>Se houver conta para <strong>{email}</strong>, enviamos um link de redefinição.</p>
        ) : (
          <>
            {erro && <p className="erro">{erro}</p>}
            <label>E-mail<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
            <button>Enviar link</button>
          </>
        )}
        <div className="links"><Link to="/login">Voltar ao login</Link></div>
      </form>
    </div>
  )
}
