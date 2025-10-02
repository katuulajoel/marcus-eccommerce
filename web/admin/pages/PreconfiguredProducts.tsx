"use client"

import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { ArrowUpDown, Copy, Eye, MoreHorizontal, Plus, Search, Trash, Edit } from "lucide-react"
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
import { useToast } from "@shared/hooks/use-toast"
import { preconfiguredProductService, type PreconfiguredProduct } from "@admin/services/preconfigured-product-service"
import { categoryService, type Category } from "@admin/services/category-service"
import { partService, type Part } from "@admin/services/part-service"
import { partOptionService, type PartOption } from "@admin/services/part-option-service"
import { priceRuleService, type PriceAdjustmentRule } from "@admin/services/price-rule-service"
import { incompatibilityService, type IncompatibilityRule } from "@admin/services/incompatibility-service"
import { Textarea } from "@shared/components/ui/textarea"

export default function PreconfiguredProductsPage() {
  // State for data
  const [products, setProducts] = useState<PreconfiguredProduct[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [parts, setParts] = useState<Part[]>([])
  const [partOptions, setPartOptions] = useState<PartOption[]>([])
  const [priceRules, setPriceRules] = useState<PriceAdjustmentRule[]>([])
  const [incompatibilityRules, setIncompatibilityRules] = useState<IncompatibilityRule[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // State for dialogs
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<PreconfiguredProduct | null>(null)

  // State for search and filters
  const [searchQuery, setSearchQuery] = useState("")

  // State for configurator
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [selectedOptions, setSelectedOptions] = useState<Record<number, number>>({}) // partId -> optionId
  const [totalPrice, setTotalPrice] = useState(0)
  const [configName, setConfigName] = useState("")
  const [configDescription, setConfigDescription] = useState("")

  const { toast } = useToast()

  // Load initial data
  useEffect(() => {
    loadProducts()
    loadCategories()
    loadPartOptions()
    loadPriceRules()
    loadIncompatibilityRules()
  }, [])

  const loadProducts = async () => {
    try {
      setIsLoading(true)
      const data = await preconfiguredProductService.getAll()
      setProducts(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load preconfigured products",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const data = await categoryService.getAll()
      setCategories(data)
    } catch (error) {
      console.error("Failed to load categories:", error)
    }
  }

  const loadPartOptions = async () => {
    try {
      const data = await partOptionService.getAll()
      setPartOptions(data)
    } catch (error) {
      console.error("Failed to load part options:", error)
    }
  }

  const loadPriceRules = async () => {
    try {
      const data = await priceRuleService.getAll()
      setPriceRules(data)
    } catch (error) {
      console.error("Failed to load price rules:", error)
    }
  }

  const loadIncompatibilityRules = async () => {
    try {
      const data = await incompatibilityService.getAll()
      setIncompatibilityRules(data)
    } catch (error) {
      console.error("Failed to load incompatibility rules:", error)
    }
  }

  // Filter and search
  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.category_details?.name.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  // Get parts for selected category, sorted by step
  const categoryParts = parts
    .filter((part) => part.category === selectedCategoryId)
    .sort((a, b) => a.step - b.step)

  const currentPart = categoryParts[currentStep]

  // Get options for current part
  const currentPartOptions = currentPart
    ? partOptions.filter((option) => option.part === currentPart.id)
    : []

  // Calculate adjusted prices based on currently selected options
  const getAdjustedPrice = (optionId: number): number => {
    let adjustment = 0

    // Check all selected options to see if any trigger price adjustments for this option
    Object.values(selectedOptions).forEach((selectedOptionId) => {
      // Find rules where condition_option is selected and affected_option is this option
      const rule = priceRules.find(
        (r) => r.condition_option === selectedOptionId && r.affected_option === optionId
      )

      if (rule) {
        adjustment += parseFloat(rule.adjusted_price.toString())
      }
    })

    return adjustment
  }

  // Get total price for an option (base + adjustment)
  const getOptionTotalPrice = (option: PartOption): number => {
    const basePrice = parseFloat(option.default_price)
    const adjustment = getAdjustedPrice(option.id)
    return basePrice + adjustment
  }

  // Check if option is incompatible with current configuration
  const isOptionIncompatible = (optionId: number): { incompatible: boolean; message: string } => {
    // Check all selected options against this option
    for (const selectedOptionId of Object.values(selectedOptions)) {
      // Check both directions of incompatibility
      const rule = incompatibilityRules.find(
        (r) =>
          (r.part_option === optionId && r.incompatible_with_option === selectedOptionId) ||
          (r.part_option === selectedOptionId && r.incompatible_with_option === optionId)
      )

      if (rule) {
        return { incompatible: true, message: rule.message }
      }
    }

    return { incompatible: false, message: "" }
  }

  // Calculate total price whenever selection changes
  useEffect(() => {
    let total = 0

    Object.entries(selectedOptions).forEach(([partId, optionId]) => {
      const option = partOptions.find((o) => o.id === optionId)
      if (option) {
        total += getOptionTotalPrice(option)
      }
    })

    setTotalPrice(total)
  }, [selectedOptions, priceRules, partOptions])

  // Handle category selection
  const handleCategorySelect = async (categoryId: string) => {
    const catId = parseInt(categoryId)
    setSelectedCategoryId(catId)
    setCurrentStep(0)
    setSelectedOptions({})
    setTotalPrice(0)

    // Load parts for this category
    try {
      const categoryParts = await partService.getAll(catId)
      setParts(categoryParts)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load parts for category",
        variant: "destructive",
      })
    }
  }

  // Handle option selection
  const handleOptionSelect = (partId: number, optionId: number) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [partId]: optionId,
    }))
  }

  // Navigate steps
  const nextStep = () => {
    if (currentStep < categoryParts.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const isCurrentStepComplete = () => {
    return currentPart && selectedOptions[currentPart.id] !== undefined
  }

  const isConfigurationComplete = () => {
    return categoryParts.every((part) => selectedOptions[part.id] !== undefined)
  }

  // CRUD operations
  const handleCreateNew = () => {
    setSelectedCategoryId(null)
    setCurrentStep(0)
    setSelectedOptions({})
    setTotalPrice(0)
    setConfigName("")
    setConfigDescription("")
    setParts([])
    setIsAddDialogOpen(true)
  }

  const handleSaveConfiguration = async () => {
    if (!configName.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter a configuration name",
        variant: "destructive",
      })
      return
    }

    if (!isConfigurationComplete()) {
      toast({
        title: "Validation Error",
        description: "Please complete all configuration steps",
        variant: "destructive",
      })
      return
    }

    try {
      const partOptionIds = Object.values(selectedOptions)

      await preconfiguredProductService.createWithParts(
        configName,
        selectedCategoryId!,
        totalPrice,
        partOptionIds,
        undefined,
        configDescription.trim() || undefined
      )

      toast({
        title: "Success",
        description: "Preconfigured product created successfully",
      })

      setIsAddDialogOpen(false)
      loadProducts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create preconfigured product",
        variant: "destructive",
      })
    }
  }

  const handleView = (product: PreconfiguredProduct) => {
    setSelectedProduct(product)
    setIsViewDialogOpen(true)
  }

  const handleEdit = (product: PreconfiguredProduct) => {
    setSelectedProduct(product)
    setIsEditDialogOpen(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this preconfigured product?")) {
      return
    }

    try {
      await preconfiguredProductService.delete(id)
      toast({
        title: "Success",
        description: "Preconfigured product deleted successfully",
      })
      loadProducts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete preconfigured product",
        variant: "destructive",
      })
    }
  }

  const handleDuplicate = async (product: PreconfiguredProduct) => {
    try {
      const partOptionIds = product.parts?.map((p) => p.part_option) || []

      await preconfiguredProductService.createWithParts(
        `${product.name} (Copy)`,
        product.category,
        parseFloat(product.base_price),
        partOptionIds,
        product.image_url,
        product.description
      )

      toast({
        title: "Success",
        description: "Preconfigured product duplicated successfully",
      })

      loadProducts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to duplicate preconfigured product",
        variant: "destructive",
      })
    }
  }

  // Get summary of selected options
  const getOptionsSummary = (product: PreconfiguredProduct): string => {
    if (!product.parts || product.parts.length === 0) {
      return "No options selected"
    }

    return product.parts
      .map((p) => p.part_option_details?.name)
      .filter(Boolean)
      .join(", ")
  }

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
                    Category
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead>Selected Options</TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Base Price
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : filteredProducts.length === 0 ? (
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
                      <Link to={`/dashboard/categories`} className="text-primary hover:underline">
                        {product.category_details?.name || `Category ${product.category}`}
                      </Link>
                    </TableCell>
                    <TableCell className="max-w-[300px] truncate" title={getOptionsSummary(product)}>
                      {getOptionsSummary(product)}
                    </TableCell>
                    <TableCell>${parseFloat(product.base_price).toFixed(2)}</TableCell>
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
                          <DropdownMenuItem onClick={() => handleEdit(product)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDuplicate(product)}>
                            <Copy className="mr-2 h-4 w-4" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDelete(product.id)}
                          >
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
        <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Preconfigured Product</DialogTitle>
            <DialogDescription>Configure a product with predefined options</DialogDescription>
          </DialogHeader>
          <div className="grid gap-6 py-4">
            {!selectedCategoryId ? (
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="category">Select Category</Label>
                  <Select onValueChange={handleCategorySelect}>
                    <SelectTrigger id="category">
                      <SelectValue placeholder="Select a category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id.toString()}>
                          {category.name}
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
                    Step {currentStep + 1} of {categoryParts.length}: Select {currentPart?.name}
                  </h3>
                  <div className="text-lg font-bold">Total: ${totalPrice.toFixed(2)}</div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {currentPartOptions.map((option) => {
                    const incompatibility = isOptionIncompatible(option.id)
                    const isSelected = selectedOptions[currentPart?.id] === option.id
                    const optionPrice = getOptionTotalPrice(option)
                    const priceAdjustment = getAdjustedPrice(option.id)

                    return (
                      <Card
                        key={option.id}
                        className={`cursor-pointer transition-all ${
                          incompatibility.incompatible
                            ? "opacity-50 cursor-not-allowed"
                            : isSelected
                            ? "ring-2 ring-primary"
                            : "hover:bg-muted/50"
                        }`}
                        onClick={() => {
                          if (!incompatibility.incompatible) {
                            handleOptionSelect(currentPart?.id, option.id)
                          }
                        }}
                        title={incompatibility.incompatible ? incompatibility.message : ""}
                      >
                        <CardContent className="p-4">
                          <div className="flex flex-col gap-2">
                            <img
                              src={option.image_url || "/placeholder.svg"}
                              alt={option.name}
                              className="mx-auto rounded-md object-cover w-full h-32"
                            />
                            <div className="text-center font-medium">{option.name}</div>
                            <div className="text-center">
                              <div className="text-muted-foreground">
                                ${parseFloat(option.default_price).toFixed(2)}
                                {priceAdjustment !== 0 && (
                                  <span className="text-xs text-primary ml-1">
                                    {priceAdjustment > 0 ? "+" : ""}${priceAdjustment.toFixed(2)}
                                  </span>
                                )}
                              </div>
                              {priceAdjustment !== 0 && (
                                <div className="text-sm font-semibold">${optionPrice.toFixed(2)}</div>
                              )}
                            </div>
                            {incompatibility.incompatible && (
                              <div className="text-xs text-destructive text-center">
                                Incompatible
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>

                {currentStep === categoryParts.length - 1 && isConfigurationComplete() && (
                  <div className="grid gap-4 pt-4 border-t">
                    <div className="grid gap-2">
                      <Label htmlFor="config-name">Configuration Name *</Label>
                      <Input
                        id="config-name"
                        placeholder={`${categories.find((c) => c.id === selectedCategoryId)?.name} - Custom`}
                        value={configName}
                        onChange={(e) => setConfigName(e.target.value)}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="config-description">Description (Optional)</Label>
                      <Textarea
                        id="config-description"
                        placeholder="Enter a description for this configuration"
                        value={configDescription}
                        onChange={(e) => setConfigDescription(e.target.value)}
                        rows={3}
                      />
                    </div>
                  </div>
                )}

                <div className="flex justify-between">
                  <Button variant="outline" onClick={prevStep} disabled={currentStep === 0}>
                    Previous
                  </Button>
                  {currentStep < categoryParts.length - 1 ? (
                    <Button onClick={nextStep} disabled={!isCurrentStepComplete()}>
                      Next
                    </Button>
                  ) : (
                    <Button
                      onClick={handleSaveConfiguration}
                      disabled={!isConfigurationComplete() || !configName.trim()}
                    >
                      Save Configuration
                    </Button>
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
                <Label>Category</Label>
                <div className="rounded-md border p-2">
                  {selectedProduct.category_details?.name || `Category ${selectedProduct.category}`}
                </div>
              </div>
              <div className="grid gap-2">
                <Label>Selected Options</Label>
                <div className="rounded-md border p-2 max-h-[200px] overflow-y-auto">
                  {selectedProduct.parts?.map((part) => (
                    <div key={part.id} className="py-1">
                      • {part.part_option_details?.name || `Option ${part.part_option}`}
                    </div>
                  ))}
                </div>
              </div>
              {selectedProduct.description && (
                <div className="grid gap-2">
                  <Label>Description</Label>
                  <div className="rounded-md border p-2">{selectedProduct.description}</div>
                </div>
              )}
              <div className="grid gap-2">
                <Label>Base Price</Label>
                <div className="rounded-md border p-2 font-bold">
                  ${parseFloat(selectedProduct.base_price).toFixed(2)}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button onClick={() => selectedProduct && handleDuplicate(selectedProduct)}>
              <Copy className="mr-2 h-4 w-4" />
              Duplicate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog - Similar to View but with editable fields */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[650px]">
          <DialogHeader>
            <DialogTitle>Edit Preconfigured Product</DialogTitle>
            <DialogDescription>Update product name and description</DialogDescription>
          </DialogHeader>
          {selectedProduct && (
            <div className="grid gap-6 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-name">Name</Label>
                <Input
                  id="edit-name"
                  defaultValue={selectedProduct.name}
                  onBlur={async (e) => {
                    try {
                      await preconfiguredProductService.update(selectedProduct.id, {
                        name: e.target.value,
                      })
                      toast({ title: "Success", description: "Name updated" })
                      loadProducts()
                    } catch (error) {
                      toast({ title: "Error", description: "Failed to update name", variant: "destructive" })
                    }
                  }}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  defaultValue={selectedProduct.description || ""}
                  rows={4}
                  onBlur={async (e) => {
                    try {
                      await preconfiguredProductService.update(selectedProduct.id, {
                        description: e.target.value,
                      })
                      toast({ title: "Success", description: "Description updated" })
                      loadProducts()
                    } catch (error) {
                      toast({
                        title: "Error",
                        description: "Failed to update description",
                        variant: "destructive",
                      })
                    }
                  }}
                />
              </div>
              <div className="grid gap-2">
                <Label>Category</Label>
                <div className="rounded-md border p-2 bg-muted">
                  {selectedProduct.category_details?.name || `Category ${selectedProduct.category}`}
                </div>
              </div>
              <div className="grid gap-2">
                <Label>Base Price</Label>
                <div className="rounded-md border p-2 bg-muted font-bold">
                  ${parseFloat(selectedProduct.base_price).toFixed(2)}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
