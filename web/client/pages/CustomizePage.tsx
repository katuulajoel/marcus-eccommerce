"use client"

import { useEffect, useState } from "react"
import { useSearchParams, Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2 } from "lucide-react"
import BikeCustomizer from "@client/components/bike-customizer"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import { preConfiguredBikes } from "@client/data/bikes"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import { Alert, AlertDescription } from "@shared/components/ui/alert"
import { fetchCategories } from "@client/services/api"

// Default image for categories without images
const DEFAULT_CATEGORY_IMAGE = "/placeholder.svg?height=200&width=300"

export default function CustomizePage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const configId = searchParams.get("config")
  const categoryParam = searchParams.get("category")
  
  const [initialConfig, setInitialConfig] = useState(null)
  const [productName, setProductName] = useState("")
  const [productImage, setProductImage] = useState("")
  const [productId, setProductId] = useState("")
  const [filteredBikes, setFilteredBikes] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(categoryParam)
  
  // New state for API data
  const [categories, setCategories] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Fetch categories from API when component mounts
  useEffect(() => {
    const getCategories = async () => {
      try {
        setIsLoading(true)
        const categoriesData = await fetchCategories()
        
        // Map the API data to include an image field for display
        const enhancedCategories = categoriesData.map(category => ({
          ...category,
          image: category.image_url || DEFAULT_CATEGORY_IMAGE
        }))
        
        setCategories(enhancedCategories)
        setError(null)
      } catch (err) {
        console.error("Failed to fetch categories:", err)
        setError("Failed to load categories. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }
    
    getCategories()
  }, [])
  
  // Function to handle category selection
  const selectCategory = (categoryName) => {
    setSelectedCategory(categoryName)
    navigate(`/customize?category=${categoryName.toLowerCase()}`)
  }

  useEffect(() => {
    // If a category is specified, filter the bikes accordingly
    if (categoryParam) {
      setSelectedCategory(categoryParam)
      
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
      
      // If there's a pre-configured bike but no category, set the category from the bike
      if (!categoryParam && preConfiguredBikes[configId].category) {
        setSelectedCategory(preConfiguredBikes[configId].category)
      }
    }
  }, [configId, categoryParam])

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
            {selectedCategory
              ? `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Products`
              : "Build Your Dream Product"}
          </h1>
          {productName ? (
            <p className="text-gray-600 max-w-2xl mx-auto">
              You're customizing the <span className="font-semibold">{productName}</span>. Feel free to modify any
              options to create your perfect product.
            </p>
          ) : selectedCategory ? (
            <p className="text-gray-600 max-w-2xl mx-auto">
              Browse our selection of {selectedCategory.toLowerCase()} products or customize one to your preferences.
            </p>
          ) : (
            <p className="text-gray-600 max-w-2xl mx-auto">
              First, select the type of product you want to customize. Each category offers different components and options.
            </p>
          )}
        </div>

        {!selectedCategory ? (
          <>
            {isLoading ? (
              <div className="flex justify-center items-center py-20">
                <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
                <span className="ml-3 text-lg">Loading categories...</span>
              </div>
            ) : error ? (
              <Alert variant="destructive" className="mb-6">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : categories.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-gray-500">No categories found. Please check back later.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {categories.map((category) => (
                  <Card 
                    key={category.id} 
                    className="hover:shadow-lg transition-shadow duration-200 cursor-pointer"
                    onClick={() => selectCategory(category.name)}
                  >
                    <div className="overflow-hidden h-40">
                      <img 
                        src={category.image}
                        alt={category.name} 
                        className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                      />
                    </div>
                    <CardContent className="p-6">
                      <h3 className="text-xl font-semibold mb-2">{category.name}</h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {category.description || "No description available"}
                      </p>
                      <Button 
                        className="w-full bg-teal-600 hover:bg-teal-700"
                        onClick={(e) => {
                          e.stopPropagation()
                          selectCategory(category.name)
                        }}
                      >
                        Customize
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </>
        ) : (
          <BikeCustomizer
            initialConfiguration={initialConfig}
            productName={productName}
            productImage={productImage}
            productId={productId || "custom-bike"}
            category={selectedCategory.toLowerCase()}
          />
        )}
      </main>

      <Footer />
    </div>
  )
}