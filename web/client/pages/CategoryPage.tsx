"use client"

import { Button } from "@shared/components/ui/button"
import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import ProductCard from "@client/components/product-card"
import SiteHeader from "@client/components/site-header"
import ProductDetailsModal from "@client/components/product-details-modal"
import Footer from "@client/components/footer"
import { useQuery } from "@tanstack/react-query"
import { fetchProductsByCategory } from "@client/services/api"

export default function CategoryPage() {
  const { category } = useParams<{ category: string }>()
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Fetch products for the category
  const { data: rawProducts, isLoading, isError } = useQuery({
    queryKey: ["productsByCategory", category],
    queryFn: () => fetchProductsByCategory(Number(category)),
    enabled: !!category,
  })

  // Parse the API data
  const products = rawProducts
    ? rawProducts.map((product) => ({
        id: product.id,
        name: product.name,
        price: parseFloat(product.base_price),
        image: product.image_url,
        description: product.description,
        parts: product.parts,
        category: product.category_details.name,
        category_details: product.category_details,
      }))
    : []

  const openProductDetails = (product: any) => {
    setSelectedProduct(product)
    setIsModalOpen(true)
  }

  const closeProductDetails = () => {
    setIsModalOpen(false)
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p>Loading products...</p>
      </div>
    )
  }

  if (isError || !products.length) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Category Not Found</h1>
        <p className="mb-8">The category you're looking for doesn't exist or has no products.</p>
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
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{products[0]?.category_details?.name || "Category"}</h1>
          <p className="text-gray-600 max-w-3xl">{products[0]?.category_details?.description || ""}</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onViewDetails={() => openProductDetails(product)}
            />
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