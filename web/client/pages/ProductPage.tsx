"use client"

import { useParams, Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import SiteHeader from "../components/site-header"
import ProductActions from "../components/product-actions"
import { getProductById } from "../data/bikes"
import Footer from "../components/footer"

export default function ProductPage() {
  const { id } = useParams<{ id: string }>()
  const product = getProductById(id || "")

  if (!product) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Product Not Found</h1>
        <p className="mb-8">The product you're looking for doesn't exist or has been removed.</p>
        <Button asChild>
          <Link to="/">Return to Home</Link>
        </Button>
      </div>
    )
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

        <div className="grid md:grid-cols-2 gap-12 mb-16">
          <div className="bg-gray-50 rounded-lg p-8 flex items-center justify-center">
            <div className="relative h-[400px] w-full">
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
            <h1 className="text-3xl md:text-4xl font-bold mb-2">{product.name}</h1>
            <p className="text-xl text-gray-500 mb-4">{product.tagline}</p>
            <p className="text-3xl font-bold mb-6">${product.price}</p>
            <p className="text-gray-600 mb-8">{product.description}</p>

            <ProductActions product={product} />

            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-bold mb-4">Key Features</h2>
              <ul className="space-y-2">
                {product.features.map((feature, index) => (
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
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-12 mb-16">
          <h2 className="text-2xl font-bold mb-8">Technical Specifications</h2>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-4">
            {product.specifications?.map((spec, index) => (
              <div key={index} className="py-3 border-b border-gray-100">
                <div className="flex justify-between">
                  <span className="font-medium">{spec.name}</span>
                  <span className="text-gray-600">{spec.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-8 text-center mb-16">
          <h2 className="text-2xl font-bold mb-4">Want to make it your own?</h2>
          <p className="text-gray-600 max-w-2xl mx-auto mb-6">
            Start with this bike as a base and customize it to your exact specifications. Change components, colors, and
            more to create your perfect ride.
          </p>
          <Button asChild size="lg" className="bg-teal-600 hover:bg-teal-700">
            <Link to={`/customize?config=${product.id}`}>Start Customizing</Link>
          </Button>
        </div>
      </main>

      <Footer />
    </div>
  )
}