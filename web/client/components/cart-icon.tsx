import { ShoppingCart } from "lucide-react"
import { useCart } from "@client/context/cart-context"
import { Badge } from "@client/components/ui/badge"
import { Link } from "react-router-dom"

export default function CartIcon() {
  const { itemCount } = useCart()

  return (
    <Link to="/cart" className="relative inline-flex items-center">
      <ShoppingCart className="h-6 w-6" />
      {itemCount > 0 && (
        <Badge className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 bg-teal-600 text-white">
          {itemCount}
        </Badge>
      )}
    </Link>
  )
}

