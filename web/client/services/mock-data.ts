// Mock data for homepage sections
// These can be replaced with real API data later

export type HeroSlide = {
  id: string
  title: string
  subtitle: string
  description: string
  image: string
  cta: {
    primary: {
      text: string
      link: string
    }
    secondary: {
      text: string
      link: string
    }
  }
}

export type Testimonial = {
  id: string
  name: string
  role: string
  content: string
  avatar: string
  rating: number
}

export type SocialPost = {
  id: string
  image: string
  username: string
  likes: number
  platform: string
}

export type CustomizationStep = {
  id: string
  title: string
  description: string
  icon: string
}

export const getMockHeroSlides = (): HeroSlide[] => {
  return [
    {
      id: "slide2",
      title: "Ride Your Custom Dream",
      subtitle: "Personalized Bikes",
      description: "Build a bike that's uniquely yours with our advanced customization tools.",
      image: "/placeholder.svg?height=600&width=600&text=Custom+Bike",
      cta: {
        primary: {
          text: "Start Building",
          link: "/customize",
        },
        secondary: {
          text: "View Gallery",
          link: "/gallery",
        },
      },
    },
    {
      id: "slide3",
      title: "Performance Meets Style",
      subtitle: "Premium Components",
      description: "Choose from top-tier components to create the perfect ride for any terrain.",
      image: "/placeholder.svg?height=600&width=600&text=Premium+Parts",
      cta: {
        primary: {
          text: "Explore Options",
          link: "/customize",
        },
        secondary: {
          text: "See Reviews",
          link: "#testimonials",
        },
      },
    },
  ]
}

export const getTestimonials = (): Testimonial[] => {
  return [
    {
      id: "1",
      name: "Sarah Johnson",
      role: "Mountain Bike Enthusiast",
      content:
        "The custom bike I built exceeded all my expectations! The configurator made it so easy to choose exactly what I wanted, and the quality is outstanding.",
      avatar: "/placeholder.svg?height=60&width=60&text=SJ",
      rating: 5,
    },
    {
      id: "2",
      name: "Michael Chen",
      role: "Road Cyclist",
      content:
        "I've been cycling for 15 years, and this is hands down the best bike I've ever owned. The customization options let me build my dream racing bike.",
      avatar: "/placeholder.svg?height=60&width=60&text=MC",
      rating: 5,
    },
    {
      id: "3",
      name: "Jessica Williams",
      role: "Urban Commuter",
      content:
        "Perfect for my daily commute! I was able to customize it exactly to my needs. The quality and attention to detail are exceptional.",
      avatar: "/placeholder.svg?height=60&width=60&text=JW",
      rating: 5,
    },
    {
      id: "4",
      name: "David Thompson",
      role: "Weekend Rider",
      content:
        "The whole process was seamless from start to finish. My custom hybrid bike arrived perfectly assembled and ready to ride. Highly recommend!",
      avatar: "/placeholder.svg?height=60&width=60&text=DT",
      rating: 4,
    },
  ]
}

export const getSocialPosts = (): SocialPost[] => {
  return [
    {
      id: "1",
      image: "/placeholder.svg?height=300&width=300&text=Mountain+Trail",
      username: "@trail_blazer",
      likes: 245,
      platform: "instagram",
    },
    {
      id: "2",
      image: "/placeholder.svg?height=300&width=300&text=Road+Race",
      username: "@speed_demon",
      likes: 189,
      platform: "instagram",
    },
    {
      id: "3",
      image: "/placeholder.svg?height=300&width=300&text=City+Ride",
      username: "@urban_cyclist",
      likes: 302,
      platform: "instagram",
    },
    {
      id: "4",
      image: "/placeholder.svg?height=300&width=300&text=Sunset+Ride",
      username: "@bike_life",
      likes: 276,
      platform: "instagram",
    },
    {
      id: "5",
      image: "/placeholder.svg?height=300&width=300&text=Custom+Build",
      username: "@custom_rides",
      likes: 198,
      platform: "instagram",
    },
    {
      id: "6",
      image: "/placeholder.svg?height=300&width=300&text=Weekend+Adventure",
      username: "@adventure_seeker",
      likes: 221,
      platform: "instagram",
    },
  ]
}

export const getCustomizationSteps = (): CustomizationStep[] => {
  return [
    {
      id: "step1",
      title: "Choose Your Base",
      description: "Select a bike category and starting configuration that matches your riding style.",
      icon: "MousePointerClick",
    },
    {
      id: "step2",
      title: "Customize Everything",
      description: "Pick your frame, wheels, components, and colors to create your perfect ride.",
      icon: "Palette",
    },
    {
      id: "step3",
      title: "We Build & Deliver",
      description: "We'll expertly assemble your custom bike and deliver it ready to ride.",
      icon: "Gift",
    },
  ]
}
