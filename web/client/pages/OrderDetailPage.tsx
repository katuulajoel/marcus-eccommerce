"use client"

import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowLeft, Package, CreditCard, Smartphone } from "lucide-react"
import { loadStripe } from "@stripe/stripe-js"
import { Elements } from "@stripe/react-stripe-js"
import { Button } from "@shared/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@shared/components/ui/dialog"
import { Label } from "@shared/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@shared/components/ui/radio-group"
import { axiosInstance } from "@client/context/auth-context"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import ProtectedRoute from "@client/components/protected-route"
import StripePaymentForm from "@client/components/stripe-payment-form"

interface Order {
  id: number
  total_price: string
  amount_paid: string
  balance_due: string
  minimum_required_amount: string
  payment_status: string
  fulfillment_status: string
  is_fulfillable: boolean
  created_at: string
  products: OrderProduct[]
  payments: Payment[]
}

interface OrderProduct {
  id: number
  base_product_name: string
  custom_name: string | null
  items: OrderItem[]
}

interface OrderItem {
  id: number
  part_name: string
  option_name: string
  final_price: string
  minimum_payment_required: string
}

interface Payment {
  id: number
  amount: string
  payment_method: string
  payment_date: string
  paid_by: string
  transaction_reference: string
}

function OrderDetailContent() {
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false)
  const [selectedGateway, setSelectedGateway] = useState("stripe")
  const [paymentLoading, setPaymentLoading] = useState(false)
  const [transactionId, setTransactionId] = useState<number | null>(null)
  const [stripeDialogOpen, setStripeDialogOpen] = useState(false)
  const [stripePromise, setStripePromise] = useState<any>(null)
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const [mtnMomoDialogOpen, setMtnMomoDialogOpen] = useState(false)
  const [mtnPhoneNumber, setMtnPhoneNumber] = useState("")
  const [mtnWaitingDialogOpen, setMtnWaitingDialogOpen] = useState(false)
  const [pollingAttempts, setPollingAttempts] = useState(0)

  useEffect(() => {
    fetchOrder()
  }, [id])

  const fetchOrder = async () => {
    try {
      const response = await axiosInstance.get(`/orders/${id}/`)
      setOrder(response.data)
    } catch (err: any) {
      setError("Failed to load order")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStripeSuccess = async (paymentIntentId: string) => {
    try {
      // Verify payment on backend to record it in the database
      await axiosInstance.post("/payments/verify/", {
        transaction_id: transactionId,
      })

      setStripeDialogOpen(false)
      setClientSecret(null)
      setStripePromise(null)
      setTransactionId(null)
      fetchOrder() // Refresh order to show updated payment status
    } catch (err: any) {
      console.error("Payment verification error:", err)
      alert("Payment succeeded but verification failed. Refreshing order status...")
      setStripeDialogOpen(false)
      fetchOrder()
    }
  }

  const handleStripeError = (errorMessage: string) => {
    alert(errorMessage)
    setStripeDialogOpen(false)
  }

  const handlePayment = async () => {
    if (!order) return

    // For MTN MoMo, show phone collection dialog first
    if (selectedGateway === "mtn_momo" || selectedGateway === "airtel_money") {
      setPaymentDialogOpen(false)
      setMtnMomoDialogOpen(true)
      return
    }

    // For other gateways (Stripe), proceed with payment
    await initiatePayment()
  }

  const initiatePayment = async (phoneNumber?: string) => {
    if (!order) return

    setPaymentLoading(true)
    try {
      // MTN MoMo and Airtel Money require EUR for sandbox testing
      const currency = (selectedGateway === "mtn_momo" || selectedGateway === "airtel_money") ? "EUR" : "USD"

      const response = await axiosInstance.post("/payments/initiate/", {
        order_id: order.id,
        gateway: selectedGateway,
        amount: order.balance_due,
        currency: currency,
        customer_phone: phoneNumber, // Include phone for MTN MoMo
      })

      console.log("Payment initiation response:", response.data)
      console.log("action_required:", response.data.action_required)
      console.log("selectedGateway:", selectedGateway)

      // Check if payment failed immediately
      if (response.data.status === "failed") {
        const errorMessage = response.data.error_message || "Payment failed"
        alert(errorMessage)
        setMtnMomoDialogOpen(false)
        setPaymentDialogOpen(false)
        setPaymentLoading(false)
        return
      }

      // Handle different gateway responses
      if (response.data.action_required) {
        const { action_data } = response.data

        if (selectedGateway === "stripe") {
          // Store transaction ID for verification later
          setTransactionId(response.data.id)

          // Load Stripe and show payment form
          const stripe = await loadStripe(action_data.publishable_key)
          setStripePromise(stripe)
          setClientSecret(action_data.client_secret)
          setPaymentDialogOpen(false)
          setStripeDialogOpen(true)
          setPaymentLoading(false)
          return
        } else if (selectedGateway === "mtn_momo" || selectedGateway === "airtel_money") {
          console.log("MTN MoMo payment initiated, showing waiting dialog")
          // Close phone dialog and show waiting dialog
          setMtnMomoDialogOpen(false)
          setMtnWaitingDialogOpen(true)
          setTransactionId(response.data.id)
          setPollingAttempts(0)
          setPaymentLoading(false)

          // Poll for payment status
          startPaymentPolling(response.data.id)
          return
        }
      }

      setPaymentDialogOpen(false)
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.response?.data?.message || "Payment initiation failed"
      console.error("Payment initiation error:", err)
      alert(errorMessage)
      setMtnMomoDialogOpen(false)
      setMtnWaitingDialogOpen(false)
    } finally {
      setPaymentLoading(false)
    }
  }

  const handleMtnMomoSubmit = async () => {
    if (!mtnPhoneNumber) {
      alert("Please enter your phone number")
      return
    }

    // Basic phone validation (adjust pattern as needed)
    if (!/^[0-9]{10,15}$/.test(mtnPhoneNumber.replace(/[\s\-\+]/g, ''))) {
      alert("Please enter a valid phone number")
      return
    }

    await initiatePayment(mtnPhoneNumber)
  }

  const startPaymentPolling = async (transactionId: number) => {
    const maxAttempts = 30
    let attempts = 0

    const poll = setInterval(async () => {
      attempts++
      setPollingAttempts(attempts)

      try {
        const response = await axiosInstance.post("/payments/verify/", {
          transaction_id: transactionId,
        })

        const { verification_result } = response.data

        if (verification_result.success) {
          clearInterval(poll)
          setMtnWaitingDialogOpen(false)
          alert("Payment successful!")
          fetchOrder() // Refresh order data
          setMtnPhoneNumber("") // Reset phone number
        } else if (verification_result.status === "failed") {
          clearInterval(poll)
          setMtnWaitingDialogOpen(false)
          alert(`Payment failed: ${verification_result.error}`)
          setMtnPhoneNumber("") // Reset phone number
        }
      } catch (err) {
        console.error("Polling error:", err)
      }

      if (attempts >= maxAttempts) {
        clearInterval(poll)
        setMtnWaitingDialogOpen(false)
        alert("Payment verification timed out. Please check your order status.")
        setMtnPhoneNumber("") // Reset phone number
      }
    }, 3000) // Poll every 3 seconds
  }

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

  if (error || !order) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || "Order not found"}</p>
        <Link to="/orders">
          <Button className="mt-4">Back to Orders</Button>
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <Link to="/orders" className="inline-flex items-center text-gray-600 hover:text-teal-600">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Orders
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          {/* Order Header */}
          <div className="bg-white rounded-lg border shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <h1 className="text-2xl font-bold">Order #{order.id}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.payment_status)}`}>
                {formatStatus(order.payment_status)}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.fulfillment_status)}`}>
                {formatStatus(order.fulfillment_status)}
              </span>
            </div>
            <p className="text-gray-600">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
          </div>

          {/* Order Items */}
          {order.products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">
                {product.custom_name || product.base_product_name}
              </h3>
              <div className="space-y-2">
                {product.items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-gray-600">
                      {item.part_name}: <span className="font-medium text-gray-900">{item.option_name}</span>
                    </span>
                    <span className="font-medium">${Number(item.final_price).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Payment History */}
          {order.payments.length > 0 && (
            <div className="bg-white rounded-lg border shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Payment History</h3>
              <div className="space-y-3">
                {order.payments.map((payment) => (
                  <div key={payment.id} className="flex justify-between items-center py-2 border-b last:border-0">
                    <div>
                      <p className="font-medium">${Number(payment.amount).toLocaleString()}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(payment.payment_date).toLocaleDateString()} - {payment.payment_method}
                      </p>
                      {payment.transaction_reference && (
                        <p className="text-xs text-gray-500">Ref: {payment.transaction_reference}</p>
                      )}
                    </div>
                    <span className="text-green-600 text-sm font-medium">Completed</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-lg border shadow-sm h-fit p-6 space-y-4">
          <h3 className="text-lg font-semibold">Order Summary</h3>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Amount</span>
              <span className="font-medium">${Number(order.total_price).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Amount Paid</span>
              <span className="font-medium text-green-600">${Number(order.amount_paid).toLocaleString()}</span>
            </div>
            {Number(order.balance_due) > 0 && (
              <>
                <div className="border-t pt-2 flex justify-between">
                  <span className="text-gray-900 font-medium">Balance Due</span>
                  <span className="font-bold text-red-600">${Number(order.balance_due).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Minimum Required</span>
                  <span>${Number(order.minimum_required_amount).toLocaleString()}</span>
                </div>
              </>
            )}
          </div>

          {Number(order.balance_due) > 0 && (
            <Button onClick={() => setPaymentDialogOpen(true)} className="w-full bg-teal-600 hover:bg-teal-700">
              <CreditCard className="h-4 w-4 mr-2" />
              Make Payment
            </Button>
          )}
        </div>
      </div>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Choose Payment Method</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Amount to pay: <span className="font-bold text-lg">${Number(order.balance_due).toLocaleString()}</span>
            </p>

            <RadioGroup value={selectedGateway} onValueChange={setSelectedGateway}>
              <div className="flex items-center space-x-2 border rounded-lg p-4 cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="stripe" id="stripe" />
                <Label htmlFor="stripe" className="flex-1 cursor-pointer">
                  <div className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2" />
                    <div>
                      <p className="font-medium">Credit/Debit Card</p>
                      <p className="text-xs text-gray-500">Pay with Stripe</p>
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 border rounded-lg p-4 cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="mtn_momo" id="mtn_momo" />
                <Label htmlFor="mtn_momo" className="flex-1 cursor-pointer">
                  <div className="flex items-center">
                    <Smartphone className="h-5 w-5 mr-2" />
                    <div>
                      <p className="font-medium">MTN Mobile Money</p>
                      <p className="text-xs text-gray-500">Pay with your MTN number</p>
                    </div>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 border rounded-lg p-4 cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="airtel_money" id="airtel_money" />
                <Label htmlFor="airtel_money" className="flex-1 cursor-pointer">
                  <div className="flex items-center">
                    <Smartphone className="h-5 w-5 mr-2" />
                    <div>
                      <p className="font-medium">Airtel Money</p>
                      <p className="text-xs text-gray-500">Pay with your Airtel number</p>
                    </div>
                  </div>
                </Label>
              </div>
            </RadioGroup>

            <div className="flex gap-2 pt-4">
              <Button variant="outline" onClick={() => setPaymentDialogOpen(false)} className="flex-1">
                Cancel
              </Button>
              <Button onClick={handlePayment} disabled={paymentLoading} className="flex-1 bg-teal-600 hover:bg-teal-700">
                {paymentLoading ? "Processing..." : "Continue to Payment"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Stripe Payment Dialog */}
      <Dialog open={stripeDialogOpen} onOpenChange={setStripeDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Enter Payment Details</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Amount to pay: <span className="font-bold text-lg">${Number(order?.balance_due || 0).toLocaleString()}</span>
            </p>

            {clientSecret && stripePromise && (
              <Elements
                stripe={stripePromise}
                options={{
                  clientSecret,
                  appearance: {
                    theme: "stripe",
                    variables: {
                      colorPrimary: "#0d9488",
                    },
                  },
                }}
              >
                <StripePaymentForm
                  onSuccess={handleStripeSuccess}
                  onError={handleStripeError}
                  totalAmount={Number(order?.balance_due || 0)}
                />
              </Elements>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* MTN MoMo Phone Collection Dialog */}
      <Dialog open={mtnMomoDialogOpen} onOpenChange={setMtnMomoDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Enter Your MTN Mobile Money Number</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Amount to pay: <span className="font-bold text-lg">${Number(order?.balance_due || 0).toLocaleString()}</span>
            </p>

            <div className="space-y-2">
              <Label htmlFor="mtn-phone">Phone Number</Label>
              <input
                id="mtn-phone"
                type="tel"
                placeholder="0248888736"
                value={mtnPhoneNumber}
                onChange={(e) => setMtnPhoneNumber(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
              <p className="text-xs text-gray-500">
                Enter your MTN Mobile Money number (e.g., 024XXXXXXX for Ghana)
              </p>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setMtnMomoDialogOpen(false)
                  setMtnPhoneNumber("")
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleMtnMomoSubmit}
                disabled={paymentLoading}
                className="flex-1 bg-teal-600 hover:bg-teal-700"
              >
                {paymentLoading ? "Processing..." : "Submit"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* MTN MoMo Waiting Dialog */}
      <Dialog open={mtnWaitingDialogOpen} onOpenChange={(open) => !open && setMtnWaitingDialogOpen(false)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Waiting for Payment Approval</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="flex flex-col items-center justify-center py-6">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-teal-600 mb-4"></div>
              <p className="text-center text-gray-700 font-medium mb-2">
                A payment request has been sent to your phone
              </p>
              <p className="text-center text-sm text-gray-600 mb-4">
                Please check your phone and enter your PIN to authorize the payment
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 w-full">
                <p className="text-xs text-blue-800 text-center">
                  Checking payment status... ({pollingAttempts}/30)
                </p>
              </div>
            </div>

            <p className="text-xs text-gray-500 text-center">
              This may take up to 90 seconds. Please do not close this window.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default function OrderDetailPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-white">
        <SiteHeader />
        <main className="container mx-auto px-4 py-8">
          <OrderDetailContent />
        </main>
        <Footer />
      </div>
    </ProtectedRoute>
  )
}
