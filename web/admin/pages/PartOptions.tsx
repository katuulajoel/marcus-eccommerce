"use client"

import { useState } from "react"
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
const partOptions = [
  {
    id: "1",
    name: "Aluminum Frame",
    partId: "1",
    partName: "Frame",
    basePrice: 299.99,
    image: "/placeholder.svg",
  },
  {
    id: "2",
    name: "Carbon Fiber Frame",
    partId: "1",
    partName: "Frame",
    basePrice: 599.99,
    image: "/placeholder.svg",
  },
  {
    id: "3",
    name: "Standard Wheels",
    partId: "2",
    partName: "Wheels",
    basePrice: 149.99,
    image: "/placeholder.svg",
  },
  {
    id: "4",
    name: "Performance Wheels",
    partId: "2",
    partName: "Wheels",
    basePrice: 249.99,
    image: "/placeholder.svg",
  },
  {
    id: "5",
    name: "Flat Handlebars",
    partId: "3",
    partName: "Handlebars",
    basePrice: 79.99,
    image: "/placeholder.svg",
  },
]

const parts = [
  { id: "1", name: "Frame" },
  { id: "2", name: "Wheels" },
  { id: "3", name: "Handlebars" },
  { id: "4", name: "Saddle" },
  { id: "5", name: "Brakes" },
]

export default function PartOptionsPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedOption, setSelectedOption] = useState<(typeof partOptions)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredOptions = partOptions.filter(
    (option) =>
      option.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      option.partName.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleEdit = (option: (typeof partOptions)[0]) => {
    setSelectedOption(option)
    setIsEditDialogOpen(true)
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Part Options</h1>
        <p className="text-muted-foreground">Manage options for each part in the bike configurator</p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search options..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Option
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add New Option</DialogTitle>
              <DialogDescription>Create a new option for a part in the bike configurator</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Option Name</Label>
                <Input id="name" placeholder="Aluminum Frame" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="part">Part</Label>
                <Select>
                  <SelectTrigger id="part">
                    <SelectValue placeholder="Select a part" />
                  </SelectTrigger>
                  <SelectContent>
                    {parts.map((part) => (
                      <SelectItem key={part.id} value={part.id}>
                        {part.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="price">Base Price ($)</Label>
                <Input id="price" type="number" min="0" step="0.01" placeholder="299.99" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="image">Option Image</Label>
                <Input id="image" type="file" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsAddDialogOpen(false)}>Save Option</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[80px]">Image</TableHead>
                <TableHead className="w-[250px]">
                  <div className="flex items-center gap-1">
                    Option Name
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[200px]">
                  <div className="flex items-center gap-1">
                    Part
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
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
              {filteredOptions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No options found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredOptions.map((option) => (
                  <TableRow key={option.id}>
                    <TableCell>
                      <img
                        src={option.image || "/placeholder.svg"}
                        alt={option.name}
                        width={40}
                        height={40}
                        className="rounded-md object-cover"
                      />
                    </TableCell>
                    <TableCell className="font-medium">{option.name}</TableCell>
                    <TableCell>
                      <span className="text-primary">{option.partName}</span>
                    </TableCell>
                    <TableCell>${option.basePrice.toFixed(2)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEdit(option)}>
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

      {/* Edit Option Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Edit Option</DialogTitle>
            <DialogDescription>Update the option details</DialogDescription>
          </DialogHeader>
          {selectedOption && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-name">Option Name</Label>
                <Input id="edit-name" defaultValue={selectedOption.name} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-part">Part</Label>
                <Select defaultValue={selectedOption.partId}>
                  <SelectTrigger id="edit-part">
                    <SelectValue placeholder="Select a part" />
                  </SelectTrigger>
                  <SelectContent>
                    {parts.map((part) => (
                      <SelectItem key={part.id} value={part.id}>
                        {part.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-price">Base Price ($)</Label>
                <Input id="edit-price" type="number" min="0" step="0.01" defaultValue={selectedOption.basePrice} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-image">Option Image</Label>
                <div className="mb-2">
                  <img
                    src={selectedOption.image || "/placeholder.svg"}
                    alt={selectedOption.name}
                    width={100}
                    height={100}
                    className="rounded-md object-cover"
                  />
                </div>
                <Input id="edit-image" type="file" />
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

