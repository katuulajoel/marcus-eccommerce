import { Link } from "react-router-dom"
import { ArrowRight, ChevronRight } from "lucide-react"
import ProductCarousel from "@client/components/product-carousel"
import { Button } from "@shared/components/ui/button"
import SiteHeader from "@client/components/site-header"
import { featuredBike, mountainBikes, roadBikes, hybridBikes } from "@client/data/bikes"
import Footer from "@client/components/footer"
import { useQuery } from "@tanstack/react-query"
import { fetchAllProducts } from "@client/services/api"

export default function Home() {
  // Use react-query's useQuery with object-based syntax
  const { data: products, error, isLoading } = useQuery({
    queryKey: ["products"], // Use queryKey as an object property
    queryFn: fetchAllProducts, // Use queryFn as an object property
  })

  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <main>
        {/* Hero Section */}
        <section className="relative bg-gray-50 overflow-hidden">
          <div className="container mx-auto px-4 py-20 md:py-32">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div className="order-2 md:order-1">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4">{featuredBike.name}</h1>
                <p className="text-xl md:text-2xl text-gray-500 mb-4">{featuredBike.tagline}</p>
                <p className="text-gray-600 mb-8 max-w-md">{featuredBike.description}</p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button asChild size="lg" className="bg-teal-600 hover:bg-teal-700">
                    <Link to={`/customize?config=${featuredBike.id}`}>Customize This Bike</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg">
                    <Link to={`/product/${featuredBike.id}`}>View Details</Link>
                  </Button>
                </div>
                <div className="mt-8">
                  <p className="text-2xl font-bold mb-2">From ${featuredBike.price}</p>
                  <ul className="space-y-2">
                    {featuredBike.features.map((feature, index) => (
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
                <div className="relative h-[300px] md:h-[500px] w-full">
                  <img
                    src={featuredBike.image || "/placeholder.svg"}
                    alt={featuredBike.name}
                    className="object-contain w-full h-full"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Mountain Bikes Section */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">Mountain Bikes</h2>
                <p className="text-gray-600 max-w-2xl">
                  Designed for off-road cycling with features like rugged tires and durable frames.
                </p>
              </div>
              <Link
                to="/category/mountain"
                className="hidden md:flex items-center text-teal-600 hover:text-teal-700 font-medium"
              >
                View all <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <ProductCarousel products={mountainBikes} />

            <div className="mt-6 md:hidden">
              <Link to="/category/mountain" className="flex items-center text-teal-600 hover:text-teal-700 font-medium">
                View all mountain bikes <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        </section>

        {/* Road Bikes Section */}
        <section className="py-16 md:py-24 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">Road Bikes</h2>
                <p className="text-gray-600 max-w-2xl">
                  Optimized for riding on paved roads with speed and efficiency.
                </p>
              </div>
              <Link
                to="/category/road"
                className="hidden md:flex items-center text-teal-600 hover:text-teal-700 font-medium"
              >
                View all <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <ProductCarousel products={roadBikes} />

            <div className="mt-6 md:hidden">
              <Link to="/category/road" className="flex items-center text-teal-600 hover:text-teal-700 font-medium">
                View all road bikes <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        </section>

        {/* Hybrid Bikes Section */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">Hybrid Bikes</h2>
                <p className="text-gray-600 max-w-2xl">
                  Versatile bikes that combine features of both road and mountain bikes.
                </p>
              </div>
              <Link
                to="/category/hybrid"
                className="hidden md:flex items-center text-teal-600 hover:text-teal-700 font-medium"
              >
                View all <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <ProductCarousel products={hybridBikes} />

            <div className="mt-6 md:hidden">
              <Link to="/category/hybrid" className="flex items-center text-teal-600 hover:text-teal-700 font-medium">
                View all hybrid bikes <ChevronRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        </section>

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