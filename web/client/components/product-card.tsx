"use client"

import { ShoppingCart } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import { Badge } from "@shared/components/ui/badge"
import { useCart } from "@client/context/cart-context"
import { useToast } from "@shared/components/ui/use-toast"

interface ProductCardProps {
  product: {
    id: string
    name: string
    tagline: string
    price: number
    image: string
    category: string
    configuration: {
      frameType: string
      frameFinish: string
      wheels: string
      rimColor: string
      chain: string
    }
  }
  onViewDetails?: () => void
}

export default function ProductCard({ product, onViewDetails }: ProductCardProps) {
  const { addItem } = useCart()
  const { toast } = useToast()

  const handleAddToCart = () => {
    addItem({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image,
      quantity: 1,
      configuration: product.configuration,
    })

    toast({
      title: "Added to cart",
      description: `${product.name} has been added to your cart.`,
    })
  }

  return (
    <Card className="overflow-hidden transition-all duration-300 hover:shadow-lg">
      <div className="relative h-48 sm:h-64 bg-gray-50">
        <img
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          className="object-contain p-4 w-full h-full"
        />
      </div>
      <CardContent className="p-6">
        <h3 className="text-xl font-bold mb-1">{product.name}</h3>
        <p className="text-sm text-gray-500 mb-2">{product.tagline}</p>
        <p className="text-lg font-bold mb-4">${product.price}</p>
        <div className="flex flex-col sm:flex-row gap-2">
          <Button variant="outline" size="sm" className="flex-1" onClick={onViewDetails}>
            View Details
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-teal-600 hover:bg-teal-700 flex items-center justify-center gap-1"
            onClick={handleAddToCart}
          >
            <ShoppingCart className="h-3 w-3" />
            Add to Cart
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

