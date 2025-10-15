"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { ArrowLeft, ShoppingBag } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { useCart } from "@client/context/cart-context"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"
import SiteHeader from "@client/components/site-header"
import { Separator } from "@shared/components/ui/separator"
import { Input } from "@shared/components/ui/input"
import Footer from "@client/components/footer"
import CartItem from "@client/components/cart-item"

export default function CartPage() {
  const { items, removeItem, updateQuantity, totalPrice, clearCart } = useCart()
  const [promoCode, setPromoCode] = useState("")

  // Convert prices at component level to avoid hooks violation
  const { formattedPrice: formattedTotalPrice, isConverting: isTotalConverting } = useConvertedPrice({ amount: totalPrice })

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
            <p className="text-gray-600 mb-8">Looks like you haven't added any items to your cart yet.</p>
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
                  <CartItem
                    key={item.id}
                    item={item}
                    onQuantityChange={handleQuantityChange}
                    onRemove={removeItem}
                  />
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
                  <span>
                    {isTotalConverting ? 'Loading...' : formattedTotalPrice}
                  </span>
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
                  <span className="text-xl text-teal-600">
                    {isTotalConverting ? 'Loading...' : formattedTotalPrice}
                  </span>
                </div>

                <div className="pt-4">
                  <div className="flex gap-2 mb-4">
                    <Input 
                      placeholder="Promo code" 
                      value={promoCode} 
                      onChange={(e) => setPromoCode(e.target.value)} 
                    />
                    <Button variant="outline">Apply</Button>
                  </div>
                  <Button asChild className="w-full bg-teal-600 hover:bg-teal-700">
                    <Link to="/checkout">Proceed to Checkout</Link>
                  </Button>
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
