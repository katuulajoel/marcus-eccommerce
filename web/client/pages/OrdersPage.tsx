"use client"

import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { Package, ArrowLeft } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { axiosInstance } from "@client/context/auth-context"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import ProtectedRoute from "@client/components/protected-route"

interface Order {
  id: number
  total_price: string
  amount_paid: string
  balance_due: string
  payment_status: string
  fulfillment_status: string
  is_fulfillable: boolean
  created_at: string
  products: any[]
}

function OrdersContent() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axiosInstance.get("/orders/")
        setOrders(response.data.results || response.data)
      } catch (err: any) {
        setError("Failed to load orders")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchOrders()
  }, [])

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      partial: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      in_production: "bg-purple-100 text-purple-800",
      ready_for_pickup: "bg-teal-100 text-teal-800",
      in_delivery: "bg-indigo-100 text-indigo-800",
      delivered: "bg-green-100 text-green-800",
    }
    return colors[status] || "bg-gray-100 text-gray-800"
  }

  const formatStatus = (status: string) => {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <Link to="/" className="inline-flex items-center text-gray-600 hover:text-teal-600">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Home
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-8">My Orders</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md">{error}</div>
      )}

      {orders.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg border shadow-sm">
          <Package className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-4">No orders yet</h2>
          <p className="text-gray-600 mb-8">Start shopping to see your orders here.</p>
          <Button asChild className="bg-teal-600 hover:bg-teal-700">
            <Link to="/customize">Start Shopping</Link>
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link
              key={order.id}
              to={`/orders/${order.id}`}
              className="block bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">Order #{order.id}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.payment_status)}`}>
                      {formatStatus(order.payment_status)}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.fulfillment_status)}`}>
                      {formatStatus(order.fulfillment_status)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Placed on {new Date(order.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-2xl font-bold text-teal-600">${Number(order.total_price).toLocaleString()}</p>
                  <p className="text-sm text-gray-600">
                    Paid: ${Number(order.amount_paid).toLocaleString()}
                  </p>
                  {Number(order.balance_due) > 0 && (
                    <p className="text-sm font-medium text-red-600">
                      Balance: ${Number(order.balance_due).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default function OrdersPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-white">
        <SiteHeader />
        <main className="container mx-auto px-4 py-8">
          <OrdersContent />
        </main>
        <Footer />
      </div>
    </ProtectedRoute>
  )
}
