"use client"

import { useEffect, useState } from "react"
import { useSearchParams, Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import BikeCustomizer from "@client/components/bike-customizer"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import { preConfiguredBikes } from "@client/data/bikes"

export default function CustomizePage() {
  const [searchParams] = useSearchParams()
  const configId = searchParams.get("config")
  const [initialConfig, setInitialConfig] = useState(null)
  const [productName, setProductName] = useState("")
  const [productImage, setProductImage] = useState("")
  const [productId, setProductId] = useState("")
  const [filteredBikes, setFilteredBikes] = useState([])
  const categoryParam = searchParams.get("category")

  useEffect(() => {
    // If a category is specified, filter the bikes accordingly
    if (categoryParam) {
      const categoryBikes = Object.entries(preConfiguredBikes)
        .filter(([_, bike]) => bike.category?.toLowerCase() === categoryParam.toLowerCase())
        .reduce((acc, [id, bike]) => {
          acc[id] = bike
          return acc
        }, {})

      setFilteredBikes(Object.keys(categoryBikes))
    }
  }, [categoryParam])

  useEffect(() => {
    if (configId && preConfiguredBikes[configId]) {
      setInitialConfig(preConfiguredBikes[configId].configuration)
      setProductName(preConfiguredBikes[configId].name)
      setProductImage(preConfiguredBikes[configId].image || "")
      setProductId(configId)
    }
  }, [configId])

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

        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            {categoryParam
              ? `${categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1)} Bikes`
              : "Build Your Dream Bike"}
          </h1>
          {productName ? (
            <p className="text-gray-600 max-w-2xl mx-auto">
              You're customizing the <span className="font-semibold">{productName}</span>. Feel free to modify any
              options to create your perfect ride.
            </p>
          ) : categoryParam ? (
            <p className="text-gray-600 max-w-2xl mx-auto">
              Browse our selection of {categoryParam.toLowerCase()} bikes or customize one to your preferences.
            </p>
          ) : (
            <p className="text-gray-600 max-w-2xl mx-auto">
              Customize every aspect of your bicycle to create the perfect ride for your style and needs. Select from
              premium components and watch your creation come to life.
            </p>
          )}
        </div>

        <BikeCustomizer
          initialConfiguration={initialConfig}
          productName={productName}
          productImage={productImage}
          productId={productId || "custom-bike"}
        />
      </main>

      <Footer />
    </div>
  )
}