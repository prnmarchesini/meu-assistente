import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { entrar } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setErro('')
    setEnviando(true)
    const { error } = await entrar(email, senha)
    setEnviando(false)
    if (error) setErro(error.message)
    else navigate('/')
  }

  return (
    <div className="centro">
      <form className="cartao" onSubmit={onSubmit}>
        <h1>Entrar</h1>
        {erro && <p className="erro">{erro}</p>}
        <label>E-mail<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Senha<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required /></label>
        <button disabled={enviando}>{enviando ? 'Entrando…' : 'Entrar'}</button>
        <div className="links">
          <Link to="/cadastro">Criar conta</Link>
          <Link to="/esqueci-senha">Esqueci a senha</Link>
        </div>
      </form>
    </div>
  )
}
