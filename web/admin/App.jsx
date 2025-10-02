import { Routes, Route, Navigate } from "react-router-dom"
import DashboardLayout from "@admin/layouts/DashboardLayout"
import Categories from "@admin/pages/Categories"
import Parts from "@admin/pages/Parts"
import PartOptions from "@admin/pages/PartOptions"
import PriceRules from "@admin/pages/PriceRules"
import IncompatibilityRules from "@admin/pages/IncompatibilityRules"
import Orders from "@admin/pages/Orders"
import Customers from "@admin/pages/Customers"
import PreconfiguredProducts from "@admin/pages/PreconfiguredProducts"
import Login from "@admin/pages/Login"
import ProtectedRoute from "@admin/components/ProtectedRoute"
import { useAuth } from "@admin/context/auth-context"

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route
        path="/"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard/categories" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="categories" element={<Categories />} />
        <Route path="parts" element={<Parts />} />
        <Route path="part-options" element={<PartOptions />} />
        <Route path="price-rules" element={<PriceRules />} />
        <Route path="incompatibility-rules" element={<IncompatibilityRules />} />
        <Route path="orders" element={<Orders />} />
        <Route path="customers" element={<Customers />} />
        <Route path="preconfigured" element={<PreconfiguredProducts />} />
      </Route>
    </Routes>
  )
}

export default App