import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Cadastro() {
  const { cadastrar } = useAuth()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [ok, setOk] = useState(false)
  const [enviando, setEnviando] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setErro('')
    setEnviando(true)
    const { error } = await cadastrar(email, senha)
    setEnviando(false)
    if (error) setErro(error.message)
    else setOk(true)
  }

  if (ok) {
    return (
      <div className="centro">
        <div className="cartao">
          <h1>Quase lá!</h1>
          <p>Enviamos um e-mail de confirmação para <strong>{email}</strong>. Confirme para ativar a conta.</p>
          <Link to="/login">Voltar ao login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="centro">
      <form className="cartao" onSubmit={onSubmit}>
        <h1>Criar conta</h1>
        {erro && <p className="erro">{erro}</p>}
        <label>E-mail<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
        <label>Senha<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required minLength={6} /></label>
        <button disabled={enviando}>{enviando ? 'Criando…' : 'Criar conta'}</button>
        <div className="links"><Link to="/login">Já tenho conta</Link></div>
      </form>
    </div>
  )
}
