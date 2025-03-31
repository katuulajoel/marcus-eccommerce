"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@client/components/ui/button"
import { cn } from "@client/lib/utils"
import ProductDetailsModal from "@client/components/product-details-modal"
import ProductCard from "@client/components/product-card"

interface Product {
  id: string
  name: string
  tagline: string
  description: string
  price: number
  image: string
  category: string
  features: string[]
  specifications?: Array<{
    name: string
    value: string
  }>
  configuration: {
    frameType: string
    frameFinish: string
    wheels: string
    rimColor: string
    chain: string
  }
}

interface ProductCarouselProps {
  products: Product[]
  category?: string
}

export default function ProductCarousel({ products, category }: ProductCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [visibleCount, setVisibleCount] = useState(3)
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [startX, setStartX] = useState(0)
  const [scrollLeft, setScrollLeft] = useState(0)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Update visible count based on screen size
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 640) {
        setVisibleCount(1)
      } else if (window.innerWidth < 1024) {
        setVisibleCount(2)
      } else {
        setVisibleCount(3)
      }
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const handlePrev = () => {
    setCurrentIndex((prevIndex) => Math.max(prevIndex - 1, 0))
  }

  const handleNext = () => {
    setCurrentIndex((prevIndex) => Math.min(prevIndex + 1, products.length - visibleCount))
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!containerRef.current) return
    setIsDragging(true)
    setStartX(e.pageX - containerRef.current.offsetLeft)
    setScrollLeft(containerRef.current.scrollLeft)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return
    e.preventDefault()
    const x = e.pageX - containerRef.current.offsetLeft
    const walk = (x - startX) * 2
    containerRef.current.scrollLeft = scrollLeft - walk
  }

  const openProductDetails = (product: Product) => {
    setSelectedProduct(product)
    setIsModalOpen(true)
  }

  const closeProductDetails = () => {
    setIsModalOpen(false)
  }

  return (
    <div className="relative">
      <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-1/2 z-10">
        <Button
          variant="outline"
          size="icon"
          className={cn(
            "rounded-full bg-white shadow-md hover:bg-gray-100",
            currentIndex === 0 ? "opacity-50 cursor-not-allowed" : "",
          )}
          onClick={handlePrev}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-6 w-6" />
          <span className="sr-only">Previous</span>
        </Button>
      </div>

      <div
        ref={containerRef}
        className="overflow-hidden"
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onMouseMove={handleMouseMove}
      >
        <div
          className="flex transition-transform duration-300 ease-out"
          style={{
            transform: `translateX(-${currentIndex * (100 / visibleCount)}%)`,
            width: `${(products.length / visibleCount) * 100}%`,
          }}
        >
          {products.map((product) => (
            <div key={product.id} className="px-2" style={{ width: `${(100 / products.length) * visibleCount}%` }}>
              <ProductCard product={product} onViewDetails={() => openProductDetails(product)} />
            </div>
          ))}
        </div>
      </div>

      <div className="absolute top-1/2 right-0 transform -translate-y-1/2 translate-x-1/2 z-10">
        <Button
          variant="outline"
          size="icon"
          className={cn(
            "rounded-full bg-white shadow-md hover:bg-gray-100",
            currentIndex >= products.length - visibleCount ? "opacity-50 cursor-not-allowed" : "",
          )}
          onClick={handleNext}
          disabled={currentIndex >= products.length - visibleCount}
        >
          <ChevronRight className="h-6 w-6" />
          <span className="sr-only">Next</span>
        </Button>
      </div>

      <div className="flex justify-center mt-6 gap-1">
        {Array.from({ length: Math.ceil(products.length / visibleCount) }).map((_, index) => (
          <button
            key={index}
            className={`h-2 w-2 rounded-full transition-all ${
              index === Math.floor(currentIndex / visibleCount) ? "bg-teal-600 w-4" : "bg-gray-300"
            }`}
            onClick={() => setCurrentIndex(index * visibleCount)}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>

      {selectedProduct && (
        <ProductDetailsModal product={selectedProduct} isOpen={isModalOpen} onClose={closeProductDetails} />
      )}
    </div>
  )
}

