import { Link } from "react-router-dom"
import { ArrowRight, ChevronRight } from "lucide-react"
import ProductCarousel from "@client/components/product-carousel"
import { Button } from "@shared/components/ui/button"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import { useQuery } from "@tanstack/react-query"
import { fetchBestSellingProduct, fetchTopProducts } from "@client/services/api"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"

export default function Home() {
  // Fetch the best-selling product for the hero section
  const { 
    data: bestSeller, 
    isLoading: isLoadingBestSeller 
  } = useQuery({
    queryKey: ["bestSellingProduct"],
    queryFn: fetchBestSellingProduct,
  })

  const { formattedPrice, isConverting } = useConvertedPrice({ amount: parseInt(bestSeller?.base_price) || parseInt('0') })

  // Fetch top products for category sections
  const {
    data: topProducts,
    isLoading: isLoadingTopProducts
  } = useQuery({
    queryKey: ["topProducts"],
    queryFn: fetchTopProducts,
  })

  // Helper function to get features from parts
  const getFeatures = (parts) => {
    if (!parts) return [];
    return parts.map(part => part.part_option_details?.name).filter(Boolean);
  };

  // Group products by category using category_details.name from API
  const productsByCategory = topProducts ?
    topProducts.reduce((acc, product) => {
        const categoryName = product.category_details.name;

        if (!acc[categoryName]) {
            acc[categoryName] = [];
        }
        // Format product to match the expected shape for ProductCarousel
        acc[categoryName].push({
            id: product.id,
            name: product.name,
            tagline: product.description || '',
            description: product.description || '',
            price: parseFloat(product.base_price),
            image: product.image_url,
            parts: product.parts,
            category: categoryName,
            category_id: product.category_details.id,
            features: getFeatures(product.parts),
            configuration: {
              frameType: '',
              frameFinish: '',
              wheels: '',
              rimColor: '',
              chain: ''
            }
        });

        return acc;
    }, {}) : {};
  
  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <main>
        {/* Hero Section */}
        {isLoadingBestSeller ? (
          <section className="relative bg-gray-50 overflow-hidden">
            <div className="container mx-auto px-4 py-20 md:py-32 text-center">
              <p>Loading best seller...</p>
            </div>
          </section>
        ) : bestSeller && (
          <section className="relative bg-gray-50 overflow-hidden">
            <div className="container mx-auto px-4 py-20 md:py-32">
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div className="order-2 md:order-1">
                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4">{bestSeller.name}</h1>
                  <p className="text-xl md:text-2xl text-gray-500 mb-4">Best selling product</p>
                  <p className="text-gray-600 mb-8 max-w-md">
                    {bestSeller.description || "A custom-built bike with premium components designed for optimal performance and comfort."}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button asChild size="lg" className="bg-teal-600 hover:bg-teal-700">
                      <Link to={`/customize?product=${bestSeller.id}&category=${bestSeller.category_details.name.toLowerCase()}`}>
                        Customize This Bike
                      </Link>
                    </Button>
                  </div>
                  <div className="mt-8">
                    <p className="text-2xl font-bold mb-2">
                    {isConverting ? (
                        <span className="text-gray-400">Converting...</span>
                      ) : (
                        `From ${formattedPrice}`
                      )}
                    </p>
                    <ul className="space-y-2">
                      {getFeatures(bestSeller.parts).slice(0, 4).map((feature, index) => (
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
                <div className="order-1 md:order-2 relative">
                  <div className="relative h-[200px] sm:h-[300px] md:h-[500px] w-full bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
                    <img
                      src={bestSeller.image_url || "/placeholder.svg"}
                      alt={`${bestSeller.name} - Featured product image`}
                      className="object-contain w-full h-full p-4"
                      onError={(e) => {
                        e.currentTarget.src = "/placeholder.svg"
                        e.currentTarget.classList.add('opacity-50')
                      }}
                      loading="lazy"
                    />
                    {!bestSeller.image_url && (
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <p className="text-gray-400 text-sm">Product image coming soon</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
        
        {/* Dynamic Category Sections */}
        {isLoadingTopProducts ? (
          <section className="py-16 md:py-24">
            <div className="container mx-auto px-4 text-center">
              <p>Loading categories...</p>
            </div>
          </section>
        ) : (
          Object.entries(productsByCategory).map(([category, products], index) => (
            <section 
              key={category} 
              className={`py-16 md:py-24 ${index % 2 === 1 ? 'bg-gray-50' : ''}`}
            >
              <div className="container mx-auto px-4">
                <div className="flex justify-between items-end mb-8">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">{category}</h2>
                    <p className="text-gray-600 max-w-2xl">
                      {category === "Mountain" && "Designed for off-road cycling with features like rugged tires and durable frames."}
                      {category === "Road" && "Optimized for riding on paved roads with speed and efficiency."}
                      {category === "Hybrid" && "Versatile bikes that combine features of both road and mountain bikes."}
                    </p>
                  </div>
                  <Link
                    to={`/category/${products[0]?.category_id}`}
                    className="hidden md:flex items-center text-teal-600 hover:text-teal-700 font-medium"
                  >
                    View all <ChevronRight className="h-4 w-4 ml-1" />
                  </Link>
                </div>

                <ProductCarousel products={products} />

                <div className="mt-6 md:hidden">
                  <Link to={`/category/${products[0]?.category_id}`} className="flex items-center text-teal-600 hover:text-teal-700 font-medium">
                    View all {category.toLowerCase()} bikes <ChevronRight className="h-4 w-4 ml-1" />
                  </Link>
                </div>
              </div>
            </section>
          ))
        )}

        {/* Custom Build CTA Section */}
        <section className="py-16 md:py-24 bg-gray-900 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Build Your Dream Bike</h2>
            <p className="text-gray-300 max-w-2xl mx-auto mb-8">
              Create a custom bike that's perfectly tailored to your style, needs, and preferences. Our bike
              configurator makes it easy to build the bike of your dreams.
            </p>
            <Button asChild size="lg" className="bg-teal-600 hover:bg-teal-700">
              <Link to="/customize">
                Start Customizing <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}