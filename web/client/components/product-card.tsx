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
    parts?: Array<{
      id: number
      part_option: number
      part_option_details: {
        id: number
        part_name: string
        name: string
        default_price: string
        image_url: string | null
      }
      preconfigured_product: number
    }>
  }
  onViewDetails?: () => void
}

export default function ProductCard({ product, onViewDetails }: ProductCardProps) {
  const { addItem } = useCart()
  const { toast } = useToast()

  const handleAddToCart = () => {
    // Build configDetails from parts data if available
    const configDetails = product.parts?.reduce((acc, part) => {
      if (part?.part_option_details?.part_name && part?.part_option_details?.name) {
        const partKey = part.part_option_details.part_name.toLowerCase().replace(/\s+/g, '')
        acc[partKey] = {
          name: part.part_option_details.name,
          price: parseFloat(part.part_option_details.default_price || '0')
        }
      }
      return acc
    }, {} as Record<string, { name: string; price: number }>)

    addItem({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image,
      quantity: 1,
      configuration: product.configuration,
      configDetails,
    })

    toast({
      title: "Added to cart",
      description: `${product.name} has been added to your cart.`,
    })
  }

  return (
    <Card className="overflow-hidden transition-all duration-300 hover:shadow-lg">
      <div className="relative h-48 sm:h-64 bg-gray-50 flex items-center justify-center">
        <img
          src={product.image || "/placeholder.svg"}
          alt={`${product.name} product thumbnail`}
          className="object-contain w-full h-full p-4 max-w-full max-h-full"
          onError={(e) => {
            e.currentTarget.src = "/placeholder.svg"
            e.currentTarget.classList.add('opacity-40')
          }}
          loading="lazy"
        />
        {!product.image && (
          <div className="absolute bottom-2 right-2 bg-gray-200 rounded px-2 py-1">
            <span className="text-xs text-gray-500">No image</span>
          </div>
        )}
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

