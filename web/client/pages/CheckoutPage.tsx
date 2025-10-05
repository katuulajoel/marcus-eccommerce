"use client"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowLeft, CreditCard, Smartphone } from "lucide-react"
import { loadStripe } from "@stripe/stripe-js"
import { Elements } from "@stripe/react-stripe-js"
import { Button } from "@shared/components/ui/button"
import { Input } from "@shared/components/ui/input"
import { Label } from "@shared/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@shared/components/ui/radio-group"
import { Separator } from "@shared/components/ui/separator"
import { useCart } from "@client/context/cart-context"
import { axiosInstance } from "@client/context/auth-context"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import ProtectedRoute from "@client/components/protected-route"
import StripePaymentForm from "@client/components/stripe-payment-form"

interface ShippingAddress {
  recipient_name: string
  phone_number: string
  address_line1: string
  address_line2: string
  city: string
  state_province: string
  postal_code: string
  country: string
}

function CheckoutContent() {
  const navigate = useNavigate()
  const { items, totalPrice, clearCart } = useCart()

  const [step, setStep] = useState<"address" | "payment" | "stripe_payment" | "processing">("address")
  const [shippingAddress, setShippingAddress] = useState<ShippingAddress>({
    recipient_name: "",
    phone_number: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state_province: "",
    postal_code: "",
    country: "Uganda",
  })
  const [paymentGateway, setPaymentGateway] = useState("stripe")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [orderId, setOrderId] = useState<number | null>(null)
  const [transactionId, setTransactionId] = useState<number | null>(null)
  const [stripePromise, setStripePromise] = useState<any>(null)
  const [clientSecret, setClientSecret] = useState<string | null>(null)

  const handleAddressSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setStep("payment")
  }

  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    setStep("processing")

    try {
      // Create order
      const orderData = {
        shipping_address: shippingAddress,
        products: items.map((item) => ({
          name: item.name,
          price: item.price,
          quantity: item.quantity,
          configuration: item.configDetails || {},
        })),
      }

      const orderResponse = await axiosInstance.post("/orders/", orderData)
      const order = orderResponse.data
      setOrderId(order.id)

      // Initiate payment
      const paymentResponse = await axiosInstance.post("/payments/initiate/", {
        order_id: order.id,
        gateway: paymentGateway,
        amount: totalPrice,
        currency: "USD",
      })

      // Handle payment gateway response
      if (paymentResponse.data.action_required) {
        const { action_data } = paymentResponse.data

        if (paymentGateway === "stripe") {
          // Store transaction ID for verification later
          setTransactionId(paymentResponse.data.id)

          // Load Stripe with publishable key and show payment form
          const stripe = await loadStripe(action_data.publishable_key)
          setStripePromise(stripe)
          setClientSecret(action_data.client_secret)
          setStep("stripe_payment")
          setLoading(false)
        } else if (paymentGateway === "mtn_momo" || paymentGateway === "airtel_money") {
          alert(`${action_data.instructions}`)

          // Poll for payment status
          startPaymentPolling(paymentResponse.data.id, order.id)
        }
      } else {
        // Payment completed immediately
        clearCart()
        navigate(`/orders/${order.id}`)
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Checkout failed. Please try again.")
      setStep("payment")
      setLoading(false)
    }
  }

  const handleStripeSuccess = async (paymentIntentId: string) => {
    try {
      // Verify payment on backend to record it in the database
      await axiosInstance.post("/payments/verify/", {
        transaction_id: transactionId,
      })

      clearCart()
      navigate(`/orders/${orderId}`)
    } catch (err: any) {
      console.error("Payment verification error:", err)
      setError("Payment succeeded but verification failed. Please check your order.")
      // Still navigate to order page even if verification fails
      clearCart()
      navigate(`/orders/${orderId}`)
    }
  }

  const handleStripeError = (errorMessage: string) => {
    setError(errorMessage)
    setStep("payment")
  }

  const startPaymentPolling = async (transactionId: number, orderId: number) => {
    const maxAttempts = 30
    let attempts = 0

    const poll = setInterval(async () => {
      attempts++

      try {
        const response = await axiosInstance.post("/payments/verify/", {
          transaction_id: transactionId,
        })

        const { verification_result } = response.data

        if (verification_result.success) {
          clearInterval(poll)
          clearCart()
          navigate(`/orders/${orderId}`)
        } else if (verification_result.status === "failed") {
          clearInterval(poll)
          setError(`Payment failed: ${verification_result.error}`)
          setStep("payment")
        }
      } catch (err) {
        console.error("Polling error:", err)
      }

      if (attempts >= maxAttempts) {
        clearInterval(poll)
        setError("Payment verification timed out. Please check your order status.")
        navigate(`/orders/${orderId}`)
      }
    }, 3000)
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">Your cart is empty</p>
        <Button onClick={() => navigate("/")} className="bg-teal-600 hover:bg-teal-700">
          Continue Shopping
        </Button>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <Button variant="ghost" onClick={() => navigate("/cart")} className="p-0">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cart
        </Button>
      </div>

      <h1 className="text-3xl font-bold mb-8">Checkout</h1>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          {/* Address Step */}
          {step === "address" && (
            <div className="bg-white rounded-lg border shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-6">Shipping Address</h2>

              <form onSubmit={handleAddressSubmit} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="recipient_name">Full Name *</Label>
                    <Input
                      id="recipient_name"
                      value={shippingAddress.recipient_name}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, recipient_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone_number">Phone Number *</Label>
                    <Input
                      id="phone_number"
                      type="tel"
                      value={shippingAddress.phone_number}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, phone_number: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address_line1">Address Line 1 *</Label>
                  <Input
                    id="address_line1"
                    value={shippingAddress.address_line1}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, address_line1: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="address_line2">Address Line 2</Label>
                  <Input
                    id="address_line2"
                    value={shippingAddress.address_line2}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, address_line2: e.target.value })}
                  />
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      value={shippingAddress.city}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, city: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="state_province">State/Province</Label>
                    <Input
                      id="state_province"
                      value={shippingAddress.state_province}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, state_province: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="postal_code">Postal Code</Label>
                    <Input
                      id="postal_code"
                      value={shippingAddress.postal_code}
                      onChange={(e) => setShippingAddress({ ...shippingAddress, postal_code: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="country">Country *</Label>
                  <Input
                    id="country"
                    value={shippingAddress.country}
                    onChange={(e) => setShippingAddress({ ...shippingAddress, country: e.target.value })}
                    required
                  />
                </div>

                <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700">
                  Continue to Payment
                </Button>
              </form>
            </div>
          )}

          {/* Payment Step */}
          {step === "payment" && (
            <div className="bg-white rounded-lg border shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-6">Payment Method</h2>

              {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{error}</div>}

              <form onSubmit={handlePaymentSubmit} className="space-y-4">
                <RadioGroup value={paymentGateway} onValueChange={setPaymentGateway}>
                  <div className="flex items-center space-x-2 border rounded-lg p-4 cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="stripe" id="checkout-stripe" />
                    <Label htmlFor="checkout-stripe" className="flex-1 cursor-pointer">
                      <div className="flex items-center">
                        <CreditCard className="h-5 w-5 mr-2" />
                        <div>
                          <p className="font-medium">Credit/Debit Card</p>
                          <p className="text-xs text-gray-500">Secure payment with Stripe</p>
                        </div>
                      </div>
                    </Label>
                  </div>

                  <div className="flex items-center space-x-2 border rounded-lg p-4 cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="mtn_momo" id="checkout-mtn" />
                    <Label htmlFor="checkout-mtn" className="flex-1 cursor-pointer">
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
                    <RadioGroupItem value="airtel_money" id="checkout-airtel" />
                    <Label htmlFor="checkout-airtel" className="flex-1 cursor-pointer">
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
                  <Button type="button" variant="outline" onClick={() => setStep("address")} className="flex-1">
                    Back
                  </Button>
                  <Button type="submit" disabled={loading} className="flex-1 bg-teal-600 hover:bg-teal-700">
                    {loading ? "Processing..." : "Complete Order"}
                  </Button>
                </div>
              </form>
            </div>
          )}

          {/* Stripe Payment Step */}
          {step === "stripe_payment" && clientSecret && stripePromise && (
            <div className="bg-white rounded-lg border shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-6">Enter Payment Details</h2>

              {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{error}</div>}

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
                  totalAmount={totalPrice}
                />
              </Elements>

              <Button
                variant="outline"
                onClick={() => setStep("payment")}
                className="w-full mt-4"
              >
                Choose Different Payment Method
              </Button>
            </div>
          )}

          {/* Processing Step */}
          {step === "processing" && (
            <div className="bg-white rounded-lg border shadow-sm p-6 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-teal-600 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold mb-2">Processing Payment...</h2>
              <p className="text-gray-600">Please wait while we process your payment</p>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-lg border shadow-sm h-fit p-6">
          <h3 className="text-lg font-semibold mb-4">Order Summary</h3>

          <div className="space-y-3 mb-4">
            {items.map((item) => (
              <div key={item.id} className="flex justify-between text-sm">
                <span className="text-gray-600">
                  {item.name} x {item.quantity}
                </span>
                <span className="font-medium">${(item.price * item.quantity).toLocaleString()}</span>
              </div>
            ))}
          </div>

          <Separator className="my-4" />

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal</span>
              <span>${totalPrice.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Shipping</span>
              <span>Calculated at delivery</span>
            </div>
          </div>

          <Separator className="my-4" />

          <div className="flex justify-between font-semibold text-lg">
            <span>Total</span>
            <span className="text-teal-600">${totalPrice.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CheckoutPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-white">
        <SiteHeader />
        <main className="container mx-auto px-4 py-8">
          <CheckoutContent />
        </main>
        <Footer />
      </div>
    </ProtectedRoute>
  )
}
