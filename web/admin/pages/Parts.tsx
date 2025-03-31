"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { ArrowUpDown, Edit, MoreHorizontal, Plus, Search, Trash } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Card, CardContent } from "@shared/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@shared/components/ui/dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@shared/components/ui/dropdown-menu"
import { Input } from "@shared/components/ui/input"
import { Label } from "@shared/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@shared/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@shared/components/ui/table"

// Sample data
const parts = [
  {
    id: "1",
    name: "Frame",
    productId: "1",
    productName: "Mountain Explorer Pro",
    stepNumber: 1,
  },
  {
    id: "2",
    name: "Wheels",
    productId: "1",
    productName: "Mountain Explorer Pro",
    stepNumber: 2,
  },
  {
    id: "3",
    name: "Handlebars",
    productId: "1",
    productName: "Mountain Explorer Pro",
    stepNumber: 3,
  },
  {
    id: "4",
    name: "Frame",
    productId: "2",
    productName: "City Cruiser Deluxe",
    stepNumber: 1,
  },
  {
    id: "5",
    name: "Wheels",
    productId: "2",
    productName: "City Cruiser Deluxe",
    stepNumber: 2,
  },
]

const products = [
  { id: "1", name: "Mountain Explorer Pro" },
  { id: "2", name: "City Cruiser Deluxe" },
  { id: "3", name: "Road Racer Elite" },
  { id: "4", name: "Adventure Trail Master" },
  { id: "5", name: "Urban Commuter Plus" },
]

export default function PartsPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedPart, setSelectedPart] = useState<(typeof parts)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredParts = parts.filter(
    (part) =>
      part.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      part.productName.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleEdit = (part: (typeof parts)[0]) => {
    setSelectedPart(part)
    setIsEditDialogOpen(true)
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Parts</h1>
        <p className="text-muted-foreground">Manage bike parts for your products</p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search parts..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Part
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add New Part</DialogTitle>
              <DialogDescription>Create a new part for a product in the bike configurator</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Part Name</Label>
                <Input id="name" placeholder="Frame" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="product">Product</Label>
                <Select>
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
              <div className="grid gap-2">
                <Label htmlFor="step">Step Number</Label>
                <Input id="step" type="number" min="1" placeholder="1" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsAddDialogOpen(false)}>Save Part</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[250px]">
                  <div className="flex items-center gap-1">
                    Part Name
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[250px]">
                  <div className="flex items-center gap-1">
                    Product
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Step Number
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredParts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="h-24 text-center">
                    No parts found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredParts.map((part) => (
                  <TableRow key={part.id}>
                    <TableCell className="font-medium">{part.name}</TableCell>
                    <TableCell>
                      <Link to={`/dashboard/products`} className="text-primary hover:underline">
                        {part.productName}
                      </Link>
                    </TableCell>
                    <TableCell>{part.stepNumber}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEdit(part)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
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

      {/* Edit Part Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Edit Part</DialogTitle>
            <DialogDescription>Update the part details</DialogDescription>
          </DialogHeader>
          {selectedPart && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-name">Part Name</Label>
                <Input id="edit-name" defaultValue={selectedPart.name} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-product">Product</Label>
                <Select defaultValue={selectedPart.productId}>
                  <SelectTrigger id="edit-product">
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
              <div className="grid gap-2">
                <Label htmlFor="edit-step">Step Number</Label>
                <Input id="edit-step" type="number" min="1" defaultValue={selectedPart.stepNumber} />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsEditDialogOpen(false)}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

