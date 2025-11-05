"use client"

import { X, ShoppingCart } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Badge } from "@shared/components/ui/badge"
import { useCart } from "@client/context/cart-context"
import { useToast } from "@shared/components/ui/use-toast"
import { Link } from "react-router-dom"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"

interface ProductSpecification {
  name: string
  value: string
}

interface Product {
  id: string
  name: string
  tagline: string
  description: string
  price: number
  image: string
  category: string
  features: string[]
  specifications?: ProductSpecification[]
  configuration: {
    frameType: string
    frameFinish: string
    wheels: string
    rimColor: string
    chain: string
  }
}

interface ProductDetailsModalProps {
  product: Product
  isOpen: boolean
  onClose: () => void
  parts?: Array<{ part_option_details: { name: string } }>
}

export default function ProductDetailsModal({ product, isOpen, onClose, parts = [] }: ProductDetailsModalProps) {
  const { addItem } = useCart()
  const { toast } = useToast()

  const { formattedPrice } = useConvertedPrice({ amount: product.price })

  if (!isOpen) return null

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
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-white z-10 flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold">{product.name}</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 hover:bg-gray-100 transition-colors"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
              <div className="relative h-[300px] w-full">
                <img
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  className="object-contain h-full w-full"
                />
              </div>
            </div>

            <div>
              <Badge variant="outline" className="mb-2">
                {product.category}
              </Badge>
              <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
              <p className="text-lg text-gray-500 mb-4">{product.tagline}</p>
              <p className="text-2xl font-bold mb-6">{formattedPrice}</p>
              <p className="text-gray-600 mb-6">{product.description}</p>

              <div className="border-t border-gray-200 pt-6">
                <h2 className="text-lg font-bold mb-4">Key Features</h2>
                <ul className="space-y-2">
                  {product.parts.map((part, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="text-teal-600"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                      {part.part_option_details.name}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 bg-gray-50 p-4 border-t">
          <div className="flex justify-between items-center">
            <span className="font-bold text-lg">${product.price}</span>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleAddToCart} className="flex items-center gap-2">
                <ShoppingCart className="h-4 w-4" />
                Add to Cart
              </Button>
              <Button asChild className="bg-teal-600 hover:bg-teal-700">
                <Link to={`/customize?product=${product.id}&category=${product.category}`}>Customize</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

