import { Link } from "react-router-dom"
import { ArrowRight, ChevronRight } from "lucide-react"
import ProductCarousel from "@client/components/product-carousel"
import { Button } from "@shared/components/ui/button"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"
import HeroSlider from "@client/components/hero-slider"
import AnimatedCategoryCard from "@client/components/animated-category-card"
import HowItWorks from "@client/components/how-it-works"
import TestimonialCarousel from "@client/components/testimonial-carousel"
import SocialGallery from "@client/components/social-gallery"
import { useQuery } from "@tanstack/react-query"
import { fetchBestSellingProduct, fetchTopProducts, fetchCategories } from "@client/services/api"
import {
  getMockHeroSlides,
  getTestimonials,
  getSocialPosts,
  getCustomizationSteps,
  type HeroSlide,
} from "@client/services/mock-data"

export default function Home() {
  // Fetch the best-selling product for the hero section
  const {
    data: bestSeller,
    isLoading: isLoadingBestSeller
  } = useQuery({
    queryKey: ["bestSellingProduct"],
    queryFn: fetchBestSellingProduct,
  })

  // Fetch top products for category sections
  const {
    data: topProducts,
    isLoading: isLoadingTopProducts
  } = useQuery({
    queryKey: ["topProducts"],
    queryFn: fetchTopProducts,
  })

  // Fetch categories for the animated cards section
  const {
    data: categories,
    isLoading: isLoadingCategories
  } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
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

  // Create hero slides from best-selling product + mock slides
  const heroSlides: HeroSlide[] = bestSeller ? [
    {
      id: "bestseller",
      title: bestSeller.name,
      subtitle: "Best Selling Product",
      description: bestSeller.description || "A custom-built bike with premium components designed for optimal performance and comfort.",
      image: bestSeller.image_url || "/placeholder.svg",
      cta: {
        primary: {
          text: "Customize This Bike",
          link: `/customize?product=${bestSeller.id}&category=${bestSeller.category_details.name.toLowerCase()}`,
        },
        secondary: {
          text: "View Details",
          link: `/category/${bestSeller.category_details.id}`,
        },
      },
    },
    ...getMockHeroSlides(),
  ] : getMockHeroSlides();

  // Assign color schemes to categories
  const categoriesWithColors = categories?.map((category: any, index: number) => {
    const colorSchemes = ['purple', 'teal', 'pink', 'blue', 'orange', 'green'];
    return {
      ...category,
      colorScheme: colorSchemes[index % colorSchemes.length],
    };
  }) || [];

  // Get mock data for new sections
  const testimonials = getTestimonials();
  const socialPosts = getSocialPosts();
  const customizationSteps = getCustomizationSteps();

  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      <main>
        {/* Hero Slider Section */}
        {isLoadingBestSeller ? (
          <section className="relative bg-gradient-to-b from-pink-50 to-white overflow-hidden">
            <div className="container mx-auto px-4 py-20 md:py-32 text-center">
              <p>Loading...</p>
            </div>
          </section>
        ) : (
          <HeroSlider slides={heroSlides} />
        )}

        {/* Animated Category Cards Section */}
        {!isLoadingCategories && categoriesWithColors.length > 0 && (
          <section className="py-16 md:py-24 bg-gray-50">
            <div className="container mx-auto px-4">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold mb-4">Shop by Category</h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Explore our collection of custom bikes designed for every riding style and terrain.
                </p>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {categoriesWithColors.map((category: any, index: number) => (
                  <AnimatedCategoryCard key={category.id} category={category} index={index} />
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Top Products by Category Sections (KEPT FROM ORIGINAL) */}
        {isLoadingTopProducts ? (
          <section className="py-16 md:py-24">
            <div className="container mx-auto px-4 text-center">
              <p>Loading products...</p>
            </div>
          </section>
        ) : (
          Object.entries(productsByCategory).map(([category, products]: [string, any], index: number) => (
            <section
              key={category}
              className={`py-16 md:py-24 ${
                index % 2 === 0
                  ? 'bg-gradient-to-b from-white to-pink-50/30'
                  : 'bg-gradient-to-b from-pink-50/30 to-purple-50/20'
              }`}
            >
              <div className="container mx-auto px-4">
                <div className="flex justify-between items-end mb-12">
                  <div>
                    <div className="inline-block bg-pink-100 text-pink-800 px-3 py-1 rounded-full text-sm font-medium mb-4">
                      Collection
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                      {category} Bikes
                    </h2>
                    <p className="text-gray-600 max-w-2xl">
                      {category === "Mountain" && "Designed for off-road cycling with features like rugged tires and durable frames."}
                      {category === "Road" && "Optimized for riding on paved roads with speed and efficiency."}
                      {category === "Hybrid" && "Versatile bikes that combine features of both road and mountain bikes."}
                    </p>
                  </div>
                  <Link
                    to={`/category/${products[0]?.category_id}`}
                    className="hidden md:flex items-center gap-1 text-pink-600 hover:text-pink-700 font-medium transition-all hover:gap-2"
                  >
                    View all <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>

                <ProductCarousel products={products} />

                <div className="mt-8 md:hidden text-center">
                  <Link
                    to={`/category/${products[0]?.category_id}`}
                    className="inline-flex items-center gap-1 text-pink-600 hover:text-pink-700 font-medium transition-all hover:gap-2"
                  >
                    View all {category.toLowerCase()} bikes <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </section>
          ))
        )}

        {/* How It Works Section */}
        <section className="py-16 md:py-24 bg-gradient-to-b from-white to-pink-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Building your custom bike is easy. Just follow these three simple steps.
              </p>
            </div>
            <HowItWorks steps={customizationSteps} />
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-16 md:py-24 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">What Our Customers Say</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Don't just take our word for it. Here's what our satisfied customers have to say.
              </p>
            </div>
            <TestimonialCarousel testimonials={testimonials} />
          </div>
        </section>

        {/* Social Gallery Section */}
        <section className="py-16 md:py-24 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Share Your Ride</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Join our community and share your custom bike adventures with #MarcusBikes
              </p>
            </div>
            <SocialGallery posts={socialPosts} />
          </div>
        </section>

        {/* Custom Build CTA Section (KEPT FROM ORIGINAL) */}
        <section className="py-16 md:py-24 bg-gradient-to-r from-pink-600 to-purple-600 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Build Your Dream Bike</h2>
            <p className="text-pink-100 max-w-2xl mx-auto mb-8">
              Create a custom bike that's perfectly tailored to your style, needs, and preferences. Our bike
              configurator makes it easy to build the bike of your dreams.
            </p>
            <Button asChild size="lg" className="bg-white text-pink-600 hover:bg-gray-100">
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
