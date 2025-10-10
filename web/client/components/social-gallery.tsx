import { Instagram, Facebook, Twitter } from "lucide-react"
import type { SocialPost } from "@client/services/mock-data"

interface SocialGalleryProps {
  posts: SocialPost[]
}

export default function SocialGallery({ posts }: SocialGalleryProps) {
  const getSocialIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "instagram":
        return <Instagram className="h-4 w-4 mr-1" />
      case "facebook":
        return <Facebook className="h-4 w-4 mr-1" />
      case "twitter":
        return <Twitter className="h-4 w-4 mr-1" />
      default:
        return <Instagram className="h-4 w-4 mr-1" />
    }
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {posts.map((post) => (
        <div key={post.id} className="relative group overflow-hidden rounded-lg shadow-md">
          <div className="relative h-48 sm:h-64 bg-gray-100">
            <img
              src={post.image || "/placeholder.svg"}
              alt="Social media post"
              className="object-cover w-full h-full transition-transform duration-300 group-hover:scale-110"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
              <div className="flex items-center justify-between text-white">
                <span className="text-sm font-medium">{post.username}</span>
                <div className="flex items-center">
                  {getSocialIcon(post.platform)}
                  <span className="text-xs">{post.likes}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
