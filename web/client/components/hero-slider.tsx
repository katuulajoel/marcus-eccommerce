import { useState, useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import { Sparkles } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import type { HeroSlide } from "@client/services/mock-data"

interface HeroSliderProps {
  slides: HeroSlide[]
}

export default function HeroSlider({ slides }: HeroSliderProps) {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [isLocked, setIsLocked] = useState(true)
  const [isInHeroSection, setIsInHeroSection] = useState(true)
  const containerRef = useRef<HTMLDivElement>(null)
  const slideRefs = useRef<(HTMLDivElement | null)[]>([])
  const scrollTimeout = useRef<NodeJS.Timeout | null>(null)
  const lastScrollY = useRef(0)
  const scrollDirection = useRef<"up" | "down">("down")

  // Initialize slide refs
  useEffect(() => {
    slideRefs.current = slideRefs.current.slice(0, slides.length)
  }, [slides.length])

  // Handle wheel events to control slide navigation
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleWheel = (e: WheelEvent) => {
      // Determine scroll direction
      scrollDirection.current = e.deltaY > 0 ? "down" : "up"

      // If we're at the last slide and scrolling down, allow normal page scrolling (don't lock)
      if (currentSlide === slides.length - 1 && scrollDirection.current === "down") {
        setIsLocked(false)
        return
      }

      // If we're at the first slide and scrolling up, allow normal page scrolling
      if (currentSlide === 0 && scrollDirection.current === "up") {
        return
      }

      // Otherwise, prevent default scrolling and handle slide navigation
      if (isLocked) {
        e.preventDefault()

        // Debounce scroll events
        if (scrollTimeout.current) clearTimeout(scrollTimeout.current)

        scrollTimeout.current = setTimeout(() => {
          if (scrollDirection.current === "down" && currentSlide < slides.length - 1) {
            setCurrentSlide((prev) => prev + 1)
          } else if (scrollDirection.current === "up" && currentSlide > 0) {
            setCurrentSlide((prev) => prev - 1)
          }
        }, 50)
      }
    }

    // Handle scroll events for detecting when to re-lock scrolling
    const handleScroll = () => {
      const scrollY = window.scrollY
      const containerTop = container.offsetTop

      // Determine scroll direction
      scrollDirection.current = scrollY > lastScrollY.current ? "down" : "up"
      lastScrollY.current = scrollY

      // Check if we're still viewing the hero section
      // Hide indicators once we've scrolled more than 80% of the viewport
      const heroSectionHeight = window.innerHeight * 0.15
      const inHeroSection = scrollY < heroSectionHeight
      setIsInHeroSection(inHeroSection)

      // If scrolling up and we're back at the hero section, re-lock and show last slide
      if (scrollDirection.current === "up" && scrollY <= containerTop + 100) {
        if (!isLocked) {
          setIsLocked(true)
          setCurrentSlide(slides.length - 1)
        }
      }

      // If scrolling down and we're past the hero, ensure we're unlocked
      if (scrollDirection.current === "down" && scrollY > containerTop + window.innerHeight) {
        setIsLocked(false)
      }
    }

    // Add event listeners
    container.addEventListener("wheel", handleWheel, { passive: false })
    window.addEventListener("scroll", handleScroll)

    return () => {
      container.removeEventListener("wheel", handleWheel)
      window.removeEventListener("scroll", handleScroll)
      if (scrollTimeout.current) clearTimeout(scrollTimeout.current)
    }
  }, [currentSlide, isLocked, slides.length])

  // Function to manually navigate to a specific slide
  const goToSlide = (index: number) => {
    setCurrentSlide(index)
    if (index < slides.length - 1) {
      setIsLocked(true)
    }
  }

  return (
    <div
      ref={containerRef}
      className="relative h-[calc(100vh-5.5rem)] bg-gradient-to-b from-pink-50 to-white"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute top-20 left-10 w-40 h-40 rounded-full bg-pink-400 blur-3xl" />
        <div className="absolute bottom-10 right-10 w-60 h-60 rounded-full bg-purple-400 blur-3xl" />
        <div className="absolute top-40 right-20 w-40 h-40 rounded-full bg-yellow-300 blur-3xl" />
      </div>

      {/* Slides container */}
      <div className="relative w-full h-full">
        {slides.map((slide, index) => (
          <div
            key={slide.id}
            ref={(el) => (slideRefs.current[index] = el)}
            className={`absolute inset-0 transition-opacity duration-700 ${
              index === currentSlide ? "opacity-100 z-10" : "opacity-0 z-0"
            }`}
          >
            <div className="container mx-auto px-4 py-8 md:py-8 lg:py-8 h-full flex items-center">
              <div className="grid md:grid-cols-2 gap-6 md:gap-12 items-center w-full">
                <div
                  className={`transition-all duration-700 transform ${
                    index === currentSlide ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
                  }`}
                >
                  <div className="inline-block bg-pink-100 text-pink-800 px-3 py-1 rounded-full text-xs md:text-sm font-medium mb-3 md:mb-6">
                    {slide.subtitle}
                  </div>
                  <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-3 md:mb-4 text-gray-900 leading-tight">
                    {slide.title.split(" ").map((word, idx, array) =>
                      idx === array.length - 1 ? (
                        <span key={idx} className="text-pink-600">
                          {word}{" "}
                        </span>
                      ) : (
                        <span key={idx}>{word} </span>
                      ),
                    )}
                  </h1>
                  <p className="text-base md:text-xl text-gray-600 mb-6 md:mb-8 max-w-md">{slide.description}</p>
                  <div className="flex flex-col sm:flex-row gap-3 md:gap-4">
                    <Button asChild size="lg" className="bg-pink-600 hover:bg-pink-700 text-sm md:text-base">
                      <Link to={slide.cta.primary.link}>
                        {slide.cta.primary.text} <Sparkles className="ml-2 h-4 w-4 md:h-5 md:w-5" />
                      </Link>
                    </Button>
                    <Button
                      asChild
                      variant="outline"
                      size="lg"
                      className="border-pink-200 text-pink-700 hover:bg-pink-50 text-sm md:text-base"
                    >
                      <Link to={slide.cta.secondary.link}>{slide.cta.secondary.text}</Link>
                    </Button>
                  </div>
                  <div className="mt-6 md:mt-8 flex items-center">
                    <div className="flex -space-x-2">
                      {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="w-7 h-7 md:w-8 md:h-8 rounded-full border-2 border-white overflow-hidden bg-gray-200">
                          <img
                            src={`/placeholder.svg?height=32&width=32&text=${i}`}
                            alt="Customer"
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ))}
                    </div>
                    <div className="ml-3 md:ml-4">
                      <div className="flex items-center">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <svg key={i} className="w-3 h-3 md:w-4 md:h-4 text-yellow-400 fill-current" viewBox="0 0 24 24">
                            <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" />
                          </svg>
                        ))}
                      </div>
                      <p className="text-xs md:text-sm text-gray-600">Over 2,000 happy customers</p>
                    </div>
                  </div>
                </div>
                <div
                  className={`relative transition-all duration-700 transform ${
                    index === currentSlide ? "translate-x-0 opacity-100 rotate-0" : "translate-x-10 opacity-0 rotate-3"
                  } hidden md:block`}
                >
                  <div className="rounded-2xl overflow-hidden shadow-xl">
                    <img
                      src={slide.image || "/placeholder.svg"}
                      alt={slide.title}
                      className="w-full h-auto object-cover transform transition-transform duration-500"
                    />
                  </div>

                  <div className="absolute -bottom-6 -right-6 bg-white rounded-lg shadow-xl p-3 md:p-4 max-w-[180px] md:max-w-[200px]">
                    <div className="flex items-center gap-2 text-pink-600 font-medium text-sm md:text-base">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="md:w-5 md:h-5"
                      >
                        <path d="M20 12v10H4V12" />
                        <path d="M2 7h20" />
                        <path d="M12 22V7" />
                        <path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7Z" />
                        <path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7Z" />
                      </svg>
                      <span className="text-sm">Free assembly</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Slide indicators - Only visible in hero section */}
      {isInHeroSection && (
        <div className="fixed bottom-20 md:bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2 z-30 transition-opacity duration-300">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-2.5 h-2.5 md:w-3 md:h-3 rounded-full transition-all ${
                index === currentSlide ? "bg-pink-600 w-5 md:w-6" : "bg-gray-300"
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Scroll indicator for the last slide */}
      {currentSlide === slides.length - 1 && isLocked && isInHeroSection && (
        <div className="fixed bottom-28 md:bottom-16 left-1/2 transform -translate-x-1/2 text-center animate-bounce z-30">
          <p className="text-xs md:text-sm text-gray-500 mb-1 md:mb-2">Scroll to continue</p>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto text-gray-400 md:w-6 md:h-6"
          >
            <path d="M12 5v14M5 12l7 7 7-7" />
          </svg>
        </div>
      )}
    </div>
  )
}
