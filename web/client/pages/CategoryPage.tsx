"use client"

import { Button } from "@shared/components/ui/button"

import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import ProductCard from "@client/components/product-card"
import SiteHeader from "@client/components/site-header"
import ProductDetailsModal from "@client/components/product-details-modal"
import { bikesByCategory, categoryTitles, categoryDescriptions } from "@client/data/bikes"
import Footer from "@client/components/footer"

export default function CategoryPage() {
  const { category } = useParams<{ category: string }>()
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Check if category exists
  const categoryKey = category?.toLowerCase() as keyof typeof bikesByCategory
  const bikes = bikesByCategory[categoryKey] || []
  const title = categoryTitles[categoryKey] || `${categoryKey?.charAt(0).toUpperCase() + categoryKey?.slice(1)} Bikes`
  const description = categoryDescriptions[categoryKey] || ""

  const openProductDetails = (product: any) => {
    setSelectedProduct(product)
    setIsModalOpen(true)
  }

  const closeProductDetails = () => {
    setIsModalOpen(false)
  }

  if (!bikes.length) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Category Not Found</h1>
        <p className="mb-8">The category you're looking for doesn't exist or has been removed.</p>
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

        <div className="mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{title}</h1>
          <p className="text-gray-600 max-w-3xl">{description}</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {bikes.map((bike) => (
            <ProductCard key={bike.id} product={bike} onViewDetails={() => openProductDetails(bike)} />
          ))}
        </div>
      </main>

      {selectedProduct && (
        <ProductDetailsModal product={selectedProduct} isOpen={isModalOpen} onClose={closeProductDetails} />
      )}

      <Footer />
    </div>
  )
}