import { useRef, useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"
import { cn } from "@shared/lib/utils"
import { getColorClasses } from "@shared/lib/color-utils"

interface Category {
  id: number
  name: string
  description?: string
  image_url?: string
  colorScheme: string
}

interface AnimatedCategoryCardProps {
  category: Category
  index: number
}

export default function AnimatedCategoryCard({ category, index }: AnimatedCategoryCardProps) {
  const [isVisible, setIsVisible] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)
  const colorClasses = getColorClasses(category.colorScheme)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Add a small delay based on the index for staggered animation
        setTimeout(() => {
          if (entry.isIntersecting) {
            setIsVisible(true)
            observer.unobserve(entry.target)
          }
        }, index * 150) // 150ms delay between each card
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -100px 0px",
      },
    )

    if (cardRef.current) {
      observer.observe(cardRef.current)
    }

    return () => {
      if (cardRef.current) {
        observer.unobserve(cardRef.current)
      }
    }
  }, [index])

  return (
    <div
      ref={cardRef}
      className={cn(
        "opacity-0 transform translate-y-10",
        isVisible && "opacity-100 translate-y-0 transition-all duration-700 ease-out",
      )}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      <Link to={`/category/${category.id}`}>
        <div
          className={cn(
            "rounded-2xl overflow-hidden shadow-md transition-all duration-300 hover:shadow-xl h-full flex flex-col group",
            colorClasses.base,
            colorClasses.hover,
            isVisible && "animate-card-appear",
          )}
        >
          <div className="p-6 flex-grow">
            <h3 className={cn("text-xl font-bold mb-2", colorClasses.text)}>{category.name}</h3>
            <p className="text-gray-600 text-sm mb-4">
              {category.description || `Explore our ${category.name.toLowerCase()} collection`}
            </p>
          </div>
          <div className="relative h-48 w-full overflow-hidden bg-gray-100">
            <img
              src={category.image_url || "/placeholder.svg"}
              alt={category.name}
              className={cn(
                "object-cover w-full h-full transition-transform duration-700",
                isVisible ? "scale-100" : "scale-110"
              )}
              onError={(e) => {
                e.currentTarget.src = "/placeholder.svg"
                e.currentTarget.classList.add('opacity-50')
              }}
            />
          </div>
          <div className="p-4 flex justify-between items-center">
            <span className={cn("font-medium", colorClasses.text)}>Explore</span>
            <ArrowRight
              className={cn(
                "h-4 w-4 transition-transform duration-300",
                colorClasses.text,
                "group-hover:translate-x-1",
              )}
            />
          </div>
        </div>
      </Link>
    </div>
  )
}
