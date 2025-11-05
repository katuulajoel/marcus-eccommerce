import { Link } from "react-router-dom"
import { User, LogOut, Package } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@shared/components/ui/dropdown-menu"
import CartIcon from "@client/components/cart-icon"
import { CurrencySelector } from "@shared/components/currency-selector"
import { useAuth } from "@client/context/auth-context"

export default function SiteHeader() {
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    window.location.href = "/"
  }

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm shadow-sm">
      <div className="container mx-auto py-6 px-4">
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
            className="text-pink-600"
          >
            <circle cx="5.5" cy="17.5" r="3.5" />
            <circle cx="18.5" cy="17.5" r="3.5" />
            <path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 11.5V14l-3-3 4-3 2 3h2" />
          </svg>
          <h1 className="text-xl font-bold">
            <Link to="/">Marcus' Custom Cycles</Link>
          </h1>
        </div>
        <nav className="hidden md:block">
          <ul className="flex gap-6 items-center">
            <li className="font-medium text-gray-700 hover:text-pink-600 transition-colors">
              <Link to="/">Home</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-pink-600 transition-colors">
              <Link to="/category/mountain">Shop</Link>
            </li>
            <li className="font-medium text-gray-700 hover:text-pink-600 transition-colors">
              <Link to="/customize">Customize</Link>
            </li>
            <li>
              <CurrencySelector variant="compact" />
            </li>
            <li>
              <CartIcon />
            </li>
            <li>
              {isAuthenticated ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <User className="h-5 w-5" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <div className="px-2 py-1.5 text-sm font-medium">
                      {user?.customer?.name || user?.username}
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link to="/orders" className="cursor-pointer">
                        <Package className="mr-2 h-4 w-4" />
                        My Orders
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                      <LogOut className="mr-2 h-4 w-4" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button asChild variant="outline" size="sm">
                  <Link to="/login">Login</Link>
                </Button>
              )}
            </li>
          </ul>
        </nav>
        <div className="flex items-center gap-4 md:hidden">
          <CartIcon />
          {isAuthenticated ? (
            <Button variant="ghost" size="icon" asChild>
              <Link to="/orders">
                <User className="h-5 w-5" />
              </Link>
            </Button>
          ) : (
            <Button variant="ghost" size="sm" asChild>
              <Link to="/login">Login</Link>
            </Button>
          )}
        </div>
      </div>
      </div>
    </header>
  )
}

