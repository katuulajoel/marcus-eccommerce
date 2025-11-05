import { Link } from "react-router-dom"
import { ExternalLink, ShoppingCart } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import { Badge } from "@shared/components/ui/badge"
import { useCart } from "@client/context/cart-context"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"
import { useToast } from "@shared/hooks/use-toast"
import { useState } from "react"
import { fetchProductById } from "@client/services/api"

interface AIProductCardProps {
  product: {
    id: number
    name: string
    category: string
    category_id?: number
    base_price: number
    description: string
    image_url?: string
  }
}

// Helper function to construct full image URL
const getFullImageUrl = (imageUrl?: string): string => {
  if (!imageUrl) return "/placeholder.svg"
  if (imageUrl.startsWith('http')) return imageUrl

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
  const normalizedPath = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`

  return `${normalizedBase}${normalizedPath}`
}

export default function AIProductCard({ product }: AIProductCardProps) {
  const { addItem } = useCart()
  const { toast } = useToast()
  const { formattedPrice, isConverting } = useConvertedPrice({ amount: product.base_price })
  const [isAddingToCart, setIsAddingToCart] = useState(false)

  const handleAddToCart = async () => {
    setIsAddingToCart(true)

    try {
      // Fetch full product details with parts configuration using the existing helper
      const fullProduct = await fetchProductById(product.id)

      // Build configDetails from parts data
      const configDetails = fullProduct.parts?.reduce((acc: any, part: any) => {
        if (part?.part_option_details?.part_name && part?.part_option_details?.name) {
          const partKey = part.part_option_details.part_name.toLowerCase().replace(/\s+/g, '')
          acc[partKey] = {
            name: part.part_option_details.name,
            price: parseFloat(part.part_option_details.default_price || '0')
          }
        }
        return acc
      }, {})

      addItem({
        id: product.id.toString(),
        name: fullProduct.name,
        price: parseFloat(fullProduct.base_price),
        image: getFullImageUrl(fullProduct.image_url),
        quantity: 1,
        categoryId: fullProduct.category?.id || product.category_id,
        configDetails
      })

      toast({
        title: "Added to cart",
        description: `${fullProduct.name} has been added to your cart.`
      })
    } catch (error) {
      console.error('Error fetching product details:', error)
      toast({
        title: "Error",
        description: "Failed to add product to cart. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsAddingToCart(false)
    }
  }

  const displayImageUrl = getFullImageUrl(product.image_url)
  const hasImage = displayImageUrl !== "/placeholder.svg"

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <div className="relative h-32 bg-gray-100">
        {hasImage ? (
          <img
            src={displayImageUrl}
            alt={`${product.name} - ${product.category} gift`}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-sm">No image</span>
          </div>
        )}
        <Badge className="absolute top-2 right-2 bg-purple-600">
          {product.category}
        </Badge>
      </div>
      <CardContent className="p-3">
        <h4 className="font-semibold text-sm mb-1 line-clamp-1">{product.name}</h4>
        <p className="text-xs text-gray-600 mb-2 line-clamp-2">
          {product.description || "Customizable gift with premium options"}
        </p>
        <div className="flex items-center justify-between mb-2">
          <span className="text-lg font-bold text-purple-600">
            {isConverting ? "..." : formattedPrice}
          </span>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            asChild
          >
            <Link to={`/customize?product=${product.id}&category=${product.category.toLowerCase()}`}>
              <ExternalLink className="h-3 w-3 mr-1" />
              View
            </Link>
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600"
            onClick={handleAddToCart}
            disabled={isAddingToCart}
          >
            <ShoppingCart className="h-3 w-3 mr-1" />
            {isAddingToCart ? "Adding..." : "Add"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
