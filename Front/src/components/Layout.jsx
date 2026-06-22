import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { user, sair } = useAuth()
  const navigate = useNavigate()

  async function handleSair() {
    await sair()
    navigate('/login')
  }

  return (
    <div className="app">
      <header className="topo">
        <strong>Controle de Gastos</strong>
        <nav>
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/despesas/nova">Lançar</NavLink>
          <NavLink to="/faturas">Faturas</NavLink>
          <NavLink to="/categorias">Categorias</NavLink>
          <NavLink to="/contas">Contas</NavLink>
          <NavLink to="/cartoes">Cartões</NavLink>
        </nav>
        <span className="usuario">
          {user?.email}
          <button onClick={handleSair}>Sair</button>
        </span>
      </header>
      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  )
}
