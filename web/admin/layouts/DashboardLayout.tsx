"use client"

import type React from "react"

import { useState } from "react"
import { Link, useLocation, Outlet } from "react-router-dom"
import { Bike, Box, DollarSign, Layers, PanelLeft, Puzzle, Settings, ShoppingCart, Users, X } from "lucide-react"
import { cn } from "@shared/lib/utils"
import { Button } from "@shared/components/ui/button"
import { ScrollArea } from "@shared/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@shared/components/ui/sheet"

interface NavItem {
  title: string
  href: string
  icon: React.ElementType
}

const navItems: NavItem[] = [
  {
    title: "Products",
    href: "/dashboard/products",
    icon: Bike,
  },
  {
    title: "Parts",
    href: "/dashboard/parts",
    icon: Puzzle,
  },
  {
    title: "Part Options",
    href: "/dashboard/part-options",
    icon: Layers,
  },
  {
    title: "Price Adjustment Rules",
    href: "/dashboard/price-rules",
    icon: DollarSign,
  },
  {
    title: "Incompatibility Rules",
    href: "/dashboard/incompatibility-rules",
    icon: X,
  },
  {
    title: "Preconfigured Products",
    href: "/dashboard/preconfigured",
    icon: Box,
  },
  {
    title: "Orders",
    href: "/dashboard/orders",
    icon: ShoppingCart,
  },
  {
    title: "Customers",
    href: "/dashboard/customers",
    icon: Users,
  },
]

export default function DashboardLayout() {
  const location = useLocation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6 md:px-8">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="md:hidden">
              <PanelLeft className="h-5 w-5" />
              <span className="sr-only">Toggle Menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="pr-0">
            <MobileNav pathname={location.pathname} />
          </SheetContent>
        </Sheet>
        <div className="flex items-center gap-2">
          <Bike className="h-6 w-6" />
          <span className="font-bold">Bike Configurator Admin</span>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
            <span className="sr-only">Settings</span>
          </Button>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className={cn("hidden border-r bg-muted/40 md:block", isSidebarOpen ? "md:w-64" : "md:w-16")}>
          <div className="flex h-full flex-col gap-2">
            <div className="flex-1 py-2">
              <nav className="grid items-start px-2 text-sm font-medium">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                      location.pathname === item.href && "bg-muted text-primary",
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    {isSidebarOpen && <span>{item.title}</span>}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="p-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              >
                <PanelLeft className="mr-2 h-4 w-4" />
                {isSidebarOpen && <span>Collapse</span>}
              </Button>
            </div>
          </div>
        </aside>
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function MobileNav({ pathname }: { pathname: string }) {
  return (
    <div className="flex flex-col gap-6 pb-6 text-sm">
      <div className="flex items-center gap-2 border-b pb-4">
        <Bike className="h-6 w-6" />
        <span className="font-bold">Bike Configurator Admin</span>
      </div>
      <ScrollArea className="flex-1">
        <nav className="grid items-start gap-2 px-1 text-sm font-medium">
          {navItems.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                pathname === item.href && "bg-muted text-primary",
              )}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.title}</span>
            </Link>
          ))}
        </nav>
      </ScrollArea>
    </div>
  )
}