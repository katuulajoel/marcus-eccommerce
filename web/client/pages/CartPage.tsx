"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { ArrowLeft, Trash2, Plus, Minus, ShoppingBag } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { useCart } from "@client/context/cart-context"
import SiteHeader from "@client/components/site-header"
import { Separator } from "@shared/components/ui/separator"
import { Input } from "@shared/components/ui/input"
import Footer from "@client/components/footer"

export default function CartPage() {
  const { items, removeItem, updateQuantity, totalPrice, clearCart } = useCart()
  const [promoCode, setPromoCode] = useState("")

  // Handle quantity changes
  const handleQuantityChange = (id: string, newQuantity: number) => {
    if (newQuantity > 0) {
      updateQuantity(id, newQuantity)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center text-gray-600 hover:text-teal-600">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
        </div>

        <h1 className="text-3xl font-bold mb-8">Your Shopping Cart</h1>

        {items.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-lg border shadow-sm">
            <div className="flex justify-center mb-4">
              <ShoppingBag className="h-16 w-16 text-gray-300" />
            </div>
            <h2 className="text-2xl font-semibold mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-8">Looks like you haven't added any bikes to your cart yet.</p>
            <Button asChild className="bg-teal-600 hover:bg-teal-700">
              <Link to="/customize">Start Customizing</Link>
            </Button>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
              <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
                <div className="p-6 border-b">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold">Cart Items ({items.length})</h2>
                    <Button variant="ghost" size="sm" onClick={clearCart} className="text-red-500 hover:text-red-700">
                      Clear Cart
                    </Button>
                  </div>
                </div>

                {items.map((item) => (
                  <div key={item.id} className="p-6 border-b">
                    <div className="flex flex-col md:flex-row gap-6">
                      <div className="relative h-40 w-full md:w-40 bg-gray-50 rounded-md">
                        <img
                          src={item.image || "/placeholder.svg"}
                          alt={item.name}
                          className="object-contain p-2 h-full w-full"
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between">
                          <h3 className="text-lg font-semibold">{item.name}</h3>
                          <p className="text-lg font-bold text-teal-600">${item.price.toLocaleString()}</p>
                        </div>

                        {item.configDetails && (
                          <div className="mt-2 space-y-1">
                            {Object.entries(item.configDetails).map(([category, details]) => (
                              <div key={category} className="flex justify-between text-sm">
                                <span className="text-gray-600">
                                  {category.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())}:
                                </span>
                                <span>{details.name}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="mt-4 flex items-center justify-between">
                          <div className="flex items-center">
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8 rounded-r-none"
                              onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <div className="h-8 px-3 flex items-center justify-center border-y">{item.quantity}</div>
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8 rounded-l-none"
                              onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeItem(item.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Remove
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg border shadow-sm h-fit">
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">Order Summary</h2>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span>${totalPrice.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span>Calculated at checkout</span>
                </div>

                <Separator />

                <div className="flex justify-between font-semibold">
                  <span>Total</span>
                  <span className="text-xl text-teal-600">${totalPrice.toLocaleString()}</span>
                </div>

                <div className="pt-4">
                  <div className="flex gap-2 mb-4">
                    <Input placeholder="Promo code" value={promoCode} onChange={(e) => setPromoCode(e.target.value)} />
                    <Button variant="outline">Apply</Button>
                  </div>
                  <Button className="w-full bg-teal-600 hover:bg-teal-700">Proceed to Checkout</Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}