import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Cadastro from './pages/Cadastro'
import Cartoes from './pages/Cartoes'
import Categorias from './pages/Categorias'
import Contas from './pages/Contas'
import Dashboard from './pages/Dashboard'
import EsqueciSenha from './pages/EsqueciSenha'
import Faturas from './pages/Faturas'
import Login from './pages/Login'
import NovaDespesa from './pages/NovaDespesa'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/cadastro" element={<Cadastro />} />
      <Route path="/esqueci-senha" element={<EsqueciSenha />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/despesas/nova" element={<NovaDespesa />} />
        <Route path="/faturas" element={<Faturas />} />
        <Route path="/categorias" element={<Categorias />} />
        <Route path="/contas" element={<Contas />} />
        <Route path="/cartoes" element={<Cartoes />} />
      </Route>
    </Routes>
  )
}
