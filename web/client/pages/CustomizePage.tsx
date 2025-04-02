"use client"

import { useEffect, useState } from "react"
import { useSearchParams, Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Loader2 } from "lucide-react"
import BikeCustomizer from "@client/components/bike-customizer"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import { Alert, AlertDescription } from "@shared/components/ui/alert"
import { fetchCategories, fetchProductById } from "@client/services/api"
import { useQuery } from "@tanstack/react-query"

// Default image for categories without images
const DEFAULT_CATEGORY_IMAGE = "/placeholder.svg?height=200&width=300"

export default function CustomizePage() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
  
    const productId = searchParams.get("product")
    const categoryParam = searchParams.get("category")

    const { 
        data: preConfiguredProduct, 
        isLoading: isLoadingPreConfiguredProduct,
        error: productError
    } = useQuery({
        queryKey: ["productById", productId],
        queryFn: () => productId ? fetchProductById(productId) : null,
        enabled: !!productId,
    })
  
    const { 
        data: categories = [], 
        isLoading: isLoadingCategories, 
        error: categoriesError 
    } = useQuery({
        queryKey: ["categories"],
        queryFn: async () => {
            const categoriesData = await fetchCategories()
            return categoriesData.map(category => ({
                ...category,
                image: category.image_url || DEFAULT_CATEGORY_IMAGE
            }))
        },
    })

    const [selectedCategory, setSelectedCategory] = useState(categoryParam || null)

    useEffect(() => {
        if (categoryParam) {
            setSelectedCategory(categoryParam)
        }
    }, [categoryParam])

    const selectCategory = (categoryName) => {
        setSelectedCategory(categoryName)
        navigate(`/customize?category=${categoryName.toLowerCase()}`)
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

                <div className="text-center mb-12">
                    <h1 className="text-3xl md:text-4xl font-bold mb-4">
                        {selectedCategory
                            ? `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Products`
                            : productId
                            ? "Customize Your Product"
                            : "Build Your Dream Product"}
                    </h1>
                    {productId && preConfiguredProduct ? (
                        <p className="text-gray-600 max-w-2xl mx-auto">
                            You're customizing the <span className="font-semibold">{preConfiguredProduct.name}</span>. Feel free to modify any options to create your perfect product.
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

                {categoryParam ? (
                    <BikeCustomizer
                        productId={productId || null}
                        category={categoryParam.toLowerCase()}
                    />
                ) : (
                    <>
                        {isLoadingCategories ? (
                            <div className="flex justify-center items-center py-20">
                                <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
                                <span className="ml-3 text-lg">Loading categories...</span>
                            </div>
                        ) : categoriesError ? (
                            <Alert variant="destructive" className="mb-6">
                                <AlertDescription>{categoriesError.message}</AlertDescription>
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
                )}
            </main>

            <Footer />
        </div>
    )
}