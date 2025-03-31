import { Link } from "react-router-dom" // Replace next/link with react-router-dom
import { Button } from "@client/components/ui/button"
import CartIcon from "@client/components/cart-icon"

export default function SiteHeader() {
  return (
    <header className="container mx-auto py-6 px-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-teal-600"
          >
            <circle cx="5.5" cy="17.5" r="3.5" />
            <circle cx="18.5" cy="17.5" r="3.5" />
            <path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 11.5V14l-3-3 4-3 2 3h2" />
          </svg>
          <h1 className="text-xl font-bold">
            <Link href="/">Marcus' Custom Cycles</Link>
          </h1>
        </div>
        <nav className="hidden md:block">
          <ul className="flex gap-6 items-center">
            <li className="font-medium text-gray-700 hover:text-teal-600 transition-colors">
              <Link href="/">Home</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-teal-600 transition-colors">
              <Link href="/category/mountain">Shop</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-teal-600 transition-colors">
              <Link href="/customize">Customize</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-teal-600 transition-colors">
              <Link href="/about">About</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-teal-600 transition-colors">
              <Link href="/contact">Contact</Link>
            </li>
            <li>
              <CartIcon />
            </li>
          </ul>
        </nav>
        <div className="flex items-center gap-4 md:hidden">
          <CartIcon />
          <Button variant="ghost" size="icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="4" x2="20" y1="12" y2="12" />
              <line x1="4" x2="20" y1="6" y2="6" />
              <line x1="4" x2="20" y1="18" y2="18" />
            </svg>
          </Button>
        </div>
      </div>
    </header>
  )
}

