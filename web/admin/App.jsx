import { Routes, Route, Navigate } from "react-router-dom"
import DashboardLayout from "@admin/layouts/DashboardLayout"
import Products from "@admin/pages/Products"
import Parts from "@admin/pages/Parts"
import PartOptions from "@admin/pages/PartOptions"
import PriceRules from "@admin/pages/PriceRules"
import IncompatibilityRules from "@admin/pages/IncompatibilityRules"
import Orders from "@admin/pages/Orders"
import Customers from "@admin/pages/Customers"
import PreconfiguredProducts from "@admin/pages/PreconfiguredProducts"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard/products" replace />} />
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route path="products" element={<Products />} />
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