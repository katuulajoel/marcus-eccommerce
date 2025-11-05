import { CheckCircle, ShoppingCart, CreditCard, Package } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { cn } from "@shared/lib/utils"
import { useNavigate } from "react-router-dom"
import { useCart } from "@client/context/cart-context"
import { useEffect } from "react"

interface CartAction {
  type: 'item_added' | 'cart_updated' | 'checkout_initiated' | 'payment_pending'
  cart_items?: Array<{
    item_id: string
    product_id: number
    name: string
    price: number
    quantity: number
    line_total: number
  }>
  cart_total?: number
  item_count?: number
  message?: string
  order_id?: string
  payment_link?: string
}

interface AIActionCardProps {
  action: CartAction
  onViewCart?: () => void
  onCheckout?: () => void
}

export default function AIActionCard({ action, onViewCart, onCheckout }: AIActionCardProps) {
  const navigate = useNavigate()
  const { refreshCart } = useCart()

  // Refresh cart when action card is displayed (AI added items)
  useEffect(() => {
    if (action.type === 'item_added' || action.type === 'cart_updated') {
      refreshCart()
    }
  }, [action.type])

  const handleViewCart = () => {
    if (onViewCart) {
      onViewCart()
    } else {
      navigate('/cart')
    }
  }

  const handleCheckout = () => {
    if (onCheckout) {
      onCheckout()
    } else {
      navigate('/checkout')
    }
  }

  // Item Added or Cart Updated
  if (action.type === 'item_added' || action.type === 'cart_updated') {
    return (
      <div className="mt-3 bg-green-50 border border-green-200 rounded-lg p-4 animate-in slide-in-from-bottom-2">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-green-900 mb-1">
              {action.type === 'item_added' ? 'Added to Cart!' : 'Cart Updated'}
            </h4>

            {action.cart_items && action.cart_items.length > 0 && (
              <div className="space-y-1 mb-3">
                {action.cart_items.map((item, index) => (
                  <div key={item.item_id || index} className="text-sm text-green-800">
                    <span className="font-medium">{item.quantity}x</span> {item.name}
                    <span className="text-green-600 ml-2">
                      UGX {item.line_total?.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {action.cart_total !== undefined && (
              <div className="text-sm font-semibold text-green-900 mb-3 pb-3 border-b border-green-200">
                Cart Total: UGX {action.cart_total.toLocaleString()}
                {action.item_count !== undefined && (
                  <span className="text-green-600 font-normal ml-2">
                    ({action.item_count} {action.item_count === 1 ? 'item' : 'items'})
                  </span>
                )}
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                onClick={handleViewCart}
                variant="outline"
                className="border-green-300 text-green-700 hover:bg-green-100"
              >
                <ShoppingCart className="h-4 w-4 mr-1" />
                View Cart
              </Button>
              <Button
                size="sm"
                onClick={handleCheckout}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                Checkout Now
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Checkout Initiated
  if (action.type === 'checkout_initiated') {
    return (
      <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-4 animate-in slide-in-from-bottom-2">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
              <Package className="h-5 w-5 text-blue-600" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-blue-900 mb-1">
              Starting Checkout
            </h4>

            {action.cart_total !== undefined && (
              <p className="text-sm text-blue-800 mb-2">
                Order Total: <span className="font-semibold">UGX {action.cart_total.toLocaleString()}</span>
              </p>
            )}

            {action.message && (
              <p className="text-sm text-blue-700 mb-3">
                {action.message}
              </p>
            )}

            <Button
              size="sm"
              onClick={handleCheckout}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Continue to Checkout
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Payment Pending
  if (action.type === 'payment_pending') {
    return (
      <div className="mt-3 bg-purple-50 border border-purple-200 rounded-lg p-4 animate-in slide-in-from-bottom-2">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
              <CreditCard className="h-5 w-5 text-purple-600" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-purple-900 mb-1">
              Order Created!
            </h4>

            {action.order_id && (
              <p className="text-sm text-purple-700 mb-2">
                Order #{action.order_id}
              </p>
            )}

            {action.message && (
              <p className="text-sm text-purple-800 mb-3">
                {action.message}
              </p>
            )}

            <div className="space-y-2">
              {action.payment_link && (
                <Button
                  size="sm"
                  onClick={() => window.open(action.payment_link, '_blank')}
                  className="bg-purple-600 hover:bg-purple-700 text-white w-full"
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  Pay with Stripe
                </Button>
              )}

              <p className="text-xs text-purple-600">
                Or dial *165*3# for Mobile Money payment
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
}
