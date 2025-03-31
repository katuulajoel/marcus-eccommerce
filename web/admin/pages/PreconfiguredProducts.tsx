"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { ArrowUpDown, Copy, Eye, MoreHorizontal, Plus, Search, Trash } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@shared/components/ui/dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@shared/components/ui/dropdown-menu"
import { Input } from "@shared/components/ui/input"
import { Label } from "@shared/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@shared/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@shared/components/ui/table"

// Sample data
const preconfiguredProducts = [
  {
    id: "1",
    name: "Mountain Explorer Pro - Trail Edition",
    productId: "1",
    productName: "Mountain Explorer Pro",
    optionsSummary: "Carbon Fiber Frame, Performance Wheels, Flat Handlebars",
    totalPrice: 899.99,
  },
  {
    id: "2",
    name: "City Cruiser Deluxe - Commuter",
    productId: "2",
    productName: "City Cruiser Deluxe",
    optionsSummary: "Aluminum Frame, Standard Wheels, Comfort Handlebars",
    totalPrice: 599.99,
  },
  {
    id: "3",
    name: "Road Racer Elite - Competition",
    productId: "3",
    productName: "Road Racer Elite",
    optionsSummary: "Carbon Fiber Frame, Aero Wheels, Drop Handlebars",
    totalPrice: 1299.99,
  },
]

const products = [
  { id: "1", name: "Mountain Explorer Pro" },
  { id: "2", name: "City Cruiser Deluxe" },
  { id: "3", name: "Road Racer Elite" },
]

const parts = [
  { id: "1", name: "Frame", productId: "1", stepNumber: 1 },
  { id: "2", name: "Wheels", productId: "1", stepNumber: 2 },
  { id: "3", name: "Handlebars", productId: "1", stepNumber: 3 },
]

const partOptions = [
  { id: "1", name: "Aluminum Frame", partId: "1", basePrice: 299.99 },
  { id: "2", name: "Carbon Fiber Frame", partId: "1", basePrice: 599.99 },
  { id: "3", name: "Standard Wheels", partId: "2", basePrice: 149.99 },
  { id: "4", name: "Performance Wheels", partId: "2", basePrice: 249.99 },
  { id: "5", name: "Flat Handlebars", partId: "3", basePrice: 79.99 },
]

export default function PreconfiguredProductsPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<(typeof preconfiguredProducts)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedProductId, setSelectedProductId] = useState("")
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>({})
  const [totalPrice, setTotalPrice] = useState(0)

  const filteredProducts = preconfiguredProducts.filter(
    (product) =>
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.optionsSummary.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleView = (product: (typeof preconfiguredProducts)[0]) => {
    setSelectedProduct(product)
    setIsViewDialogOpen(true)
  }

  const handleCreateNew = () => {
    setSelectedProductId("")
    setCurrentStep(1)
    setSelectedOptions({})
    setTotalPrice(0)
    setIsAddDialogOpen(true)
  }

  const handleProductSelect = (productId: string) => {
    setSelectedProductId(productId)
    setCurrentStep(1)
    setSelectedOptions({})
    setTotalPrice(0)
  }

  const handleOptionSelect = (partId: string, optionId: string) => {
    const newSelectedOptions = { ...selectedOptions, [partId]: optionId }
    setSelectedOptions(newSelectedOptions)

    // Calculate new total price
    let newTotal = 0
    Object.entries(newSelectedOptions).forEach(([_, optId]) => {
      const option = partOptions.find((o) => o.id === optId)
      if (option) {
        newTotal += option.basePrice
      }
    })
    setTotalPrice(newTotal)
  }

  const nextStep = () => {
    setCurrentStep(currentStep + 1)
  }

  const prevStep = () => {
    setCurrentStep(currentStep - 1)
  }

  const filteredParts = parts
    .filter((part) => part.productId === selectedProductId)
    .sort((a, b) => a.stepNumber - b.stepNumber)

  const currentPart = filteredParts.find((part) => part.stepNumber === currentStep)

  const filteredOptions = currentPart ? partOptions.filter((option) => option.partId === currentPart.id) : []

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Preconfigured Products</h1>
        <p className="text-muted-foreground">Manage preconfigured product combinations</p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search preconfigured products..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={handleCreateNew}>
          <Plus className="mr-2 h-4 w-4" />
          Create Preconfigured Product
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">
                  <div className="flex items-center gap-1">
                    Name
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[200px]">
                  <div className="flex items-center gap-1">
                    Linked Product
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead>Selected Options</TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Total Price
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProducts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No preconfigured products found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredProducts.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell className="font-medium">{product.name}</TableCell>
                    <TableCell>
                      <Link to={`/dashboard/products`} className="text-primary hover:underline">
                        {product.productName}
                      </Link>
                    </TableCell>
                    <TableCell>{product.optionsSummary}</TableCell>
                    <TableCell>${product.totalPrice.toFixed(2)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleView(product)}>
                            <Eye className="mr-2 h-4 w-4" />
                            View
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Copy className="mr-2 h-4 w-4" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-destructive">
                            <Trash className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create Preconfigured Product Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="sm:max-w-[650px]">
          <DialogHeader>
            <DialogTitle>Create Preconfigured Product</DialogTitle>
            <DialogDescription>Configure a product with predefined options</DialogDescription>
          </DialogHeader>
          <div className="grid gap-6 py-4">
            {!selectedProductId ? (
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="product">Select Product</Label>
                  <Select onValueChange={handleProductSelect}>
                    <SelectTrigger id="product">
                      <SelectValue placeholder="Select a product" />
                    </SelectTrigger>
                    <SelectContent>
                      {products.map((product) => (
                        <SelectItem key={product.id} value={product.id}>
                          {product.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ) : (
              <div className="grid gap-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">
                    Step {currentStep}: Select {currentPart?.name}
                  </h3>
                  <div className="text-lg font-bold">Total: ${totalPrice.toFixed(2)}</div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {filteredOptions.map((option) => (
                    <Card
                      key={option.id}
                      className={`cursor-pointer transition-all ${
                        selectedOptions[currentPart?.id || ""] === option.id
                          ? "ring-2 ring-primary"
                          : "hover:bg-muted/50"
                      }`}
                      onClick={() => handleOptionSelect(currentPart?.id || "", option.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex flex-col gap-2">
                          <img
                            src="/placeholder.svg"
                            alt={option.name}
                            width={100}
                            height={100}
                            className="mx-auto rounded-md object-cover"
                          />
                          <div className="text-center font-medium">{option.name}</div>
                          <div className="text-center text-muted-foreground">${option.basePrice.toFixed(2)}</div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {currentStep === filteredParts.length && (
                  <div className="grid gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="config-name">Configuration Name</Label>
                      <Input
                        id="config-name"
                        placeholder={`${products.find((p) => p.id === selectedProductId)?.name} - Custom`}
                      />
                    </div>
                  </div>
                )}

                <div className="flex justify-between">
                  <Button variant="outline" onClick={prevStep} disabled={currentStep === 1}>
                    Previous
                  </Button>
                  {currentStep < filteredParts.length ? (
                    <Button onClick={nextStep} disabled={!selectedOptions[currentPart?.id || ""]}>
                      Next
                    </Button>
                  ) : (
                    <Button onClick={() => setIsAddDialogOpen(false)}>Save Configuration</Button>
                  )}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* View Preconfigured Product Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="sm:max-w-[650px]">
          <DialogHeader>
            <DialogTitle>{selectedProduct?.name}</DialogTitle>
            <DialogDescription>Preconfigured product details</DialogDescription>
          </DialogHeader>
          {selectedProduct && (
            <div className="grid gap-6 py-4">
              <div className="grid gap-2">
                <Label>Product</Label>
                <div className="rounded-md border p-2">{selectedProduct.productName}</div>
              </div>
              <div className="grid gap-2">
                <Label>Selected Options</Label>
                <div className="rounded-md border p-2">{selectedProduct.optionsSummary}</div>
              </div>
              <div className="grid gap-2">
                <Label>Total Price</Label>
                <div className="rounded-md border p-2 font-bold">${selectedProduct.totalPrice.toFixed(2)}</div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button>
              <Copy className="mr-2 h-4 w-4" />
              Duplicate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

