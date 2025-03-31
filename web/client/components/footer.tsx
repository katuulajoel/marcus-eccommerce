import { Link } from "react-router-dom"

export default function Footer() {
  return (
    <footer className="bg-gray-100 py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
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
                className="text-teal-600"
              >
                <circle cx="5.5" cy="17.5" r="3.5" />
                <circle cx="18.5" cy="17.5" r="3.5" />
                <path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 11.5V14l-3-3 4-3 2 3h2" />
              </svg>
              <h3 className="font-bold">Marcus' Custom Cycles</h3>
            </div>
            <p className="text-gray-600">Crafting premium custom bicycles for every type of rider since 2010.</p>
          </div>
          <div>
            <h3 className="font-bold mb-4">Shop</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/category/mountain" className="text-gray-600 hover:text-teal-600">
                  Mountain Bikes
                </Link>
              </li>
              <li>
                <Link to="/category/road" className="text-gray-600 hover:text-teal-600">
                  Road Bikes
                </Link>
              </li>
              <li>
                <Link to="/category/hybrid" className="text-gray-600 hover:text-teal-600">
                  Hybrid Bikes
                </Link>
              </li>
              <li>
                <Link to="/customize" className="text-gray-600 hover:text-teal-600">
                  Custom Bikes
                </Link>
              </li>
              <li>
                <Link to="/accessories" className="text-gray-600 hover:text-teal-600">
                  Accessories
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold mb-4">Company</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/about" className="text-gray-600 hover:text-teal-600">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-gray-600 hover:text-teal-600">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/careers" className="text-gray-600 hover:text-teal-600">
                  Careers
                </Link>
              </li>
              <li>
                <Link to="/blog" className="text-gray-600 hover:text-teal-600">
                  Blog
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/faq" className="text-gray-600 hover:text-teal-600">
                  FAQ
                </Link>
              </li>
              <li>
                <Link to="/shipping" className="text-gray-600 hover:text-teal-600">
                  Shipping & Returns
                </Link>
              </li>
              <li>
                <Link to="/warranty" className="text-gray-600 hover:text-teal-600">
                  Warranty
                </Link>
              </li>
              <li>
                <Link to="/care" className="text-gray-600 hover:text-teal-600">
                  Bike Care
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-200 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-600 mb-4 md:mb-0">© 2024 Marcus' Custom Cycles. All rights reserved.</p>
          <div className="flex gap-4">
            <Link to="/terms" className="text-gray-600 hover:text-teal-600">
              Terms
            </Link>
            <Link to="/privacy" className="text-gray-600 hover:text-teal-600">
              Privacy
            </Link>
            <Link to="/cookies" className="text-gray-600 hover:text-teal-600">
              Cookies
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

