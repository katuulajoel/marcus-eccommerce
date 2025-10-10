import { useState, useRef, useEffect } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { cn } from "@shared/lib/utils"
import type { Testimonial } from "@client/services/mock-data"

interface TestimonialCarouselProps {
  testimonials: Testimonial[]
}

export default function TestimonialCarousel({ testimonials }: TestimonialCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [visibleCount, setVisibleCount] = useState(3)
  const containerRef = useRef<HTMLDivElement>(null)

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
    setCurrentIndex((prevIndex) => Math.min(prevIndex + 1, testimonials.length - visibleCount))
  }

  return (
    <div className="relative" id="testimonials">
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

      <div ref={containerRef} className="overflow-hidden">
        <div
          className="flex transition-transform duration-300 ease-out"
          style={{
            transform: `translateX(-${currentIndex * (100 / visibleCount)}%)`,
            width: `${(testimonials.length / visibleCount) * 100}%`,
          }}
        >
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="px-4"
              style={{ width: `${(100 / testimonials.length) * visibleCount}%` }}
            >
              <div className="bg-white rounded-2xl shadow-lg p-6 h-full">
                <div className="flex items-center mb-4">
                  <div className="relative h-12 w-12 rounded-full overflow-hidden mr-4 bg-gray-200">
                    <img
                      src={testimonial.avatar || "/placeholder.svg"}
                      alt={testimonial.name}
                      className="object-cover w-full h-full"
                    />
                  </div>
                  <div>
                    <h4 className="font-bold">{testimonial.name}</h4>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
                  </div>
                </div>
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`h-4 w-4 ${i < testimonial.rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`}
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-600">{testimonial.content}</p>
              </div>
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
            currentIndex >= testimonials.length - visibleCount ? "opacity-50 cursor-not-allowed" : "",
          )}
          onClick={handleNext}
          disabled={currentIndex >= testimonials.length - visibleCount}
        >
          <ChevronRight className="h-6 w-6" />
          <span className="sr-only">Next</span>
        </Button>
      </div>

      <div className="flex justify-center mt-6 gap-1">
        {Array.from({ length: Math.ceil(testimonials.length / visibleCount) }).map((_, index) => (
          <button
            key={index}
            className={`h-2 w-2 rounded-full transition-all ${
              index === Math.floor(currentIndex / visibleCount) ? "bg-pink-600 w-4" : "bg-gray-300"
            }`}
            onClick={() => setCurrentIndex(index * visibleCount)}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
