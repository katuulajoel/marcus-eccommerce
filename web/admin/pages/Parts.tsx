"use client"

import { useState, useEffect } from "react"
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
import { useToast } from "@shared/components/ui/use-toast"
import { partService, type Part } from "../services/part-service"
import { categoryService, type Category } from "../services/category-service"

export default function PartsPage() {
  const [parts, setParts] = useState<Part[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedPart, setSelectedPart] = useState<Part | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()

  // Form state for add
  const [addForm, setAddForm] = useState({
    name: "",
    category: "",
    step: 1,
  })

  // Form state for edit
  const [editForm, setEditForm] = useState({
    name: "",
    category: "",
    step: 1,
  })

  useEffect(() => {
    loadParts()
    loadCategories()
  }, [])

  const loadParts = async () => {
    try {
      setIsLoading(true)
      const data = await partService.getAll()
      setParts(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load parts",
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
      toast({
        title: "Error",
        description: "Failed to load categories",
        variant: "destructive",
      })
    }
  }

  const filteredParts = parts.filter(
    (part) =>
      part.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (part.category_name && part.category_name.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleEdit = (part: Part) => {
    setSelectedPart(part)
    setEditForm({
      name: part.name,
      category: part.category.toString(),
      step: part.step,
    })
    setIsEditDialogOpen(true)
  }

  const handleAdd = async () => {
    try {
      await partService.create({
        name: addForm.name,
        category: parseInt(addForm.category),
        step: addForm.step,
      })
      toast({
        title: "Success",
        description: "Part created successfully",
      })
      setIsAddDialogOpen(false)
      setAddForm({ name: "", category: "", step: 1 })
      loadParts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create part",
        variant: "destructive",
      })
    }
  }

  const handleUpdate = async () => {
    if (!selectedPart) return

    try {
      await partService.update(selectedPart.id, {
        name: editForm.name,
        category: parseInt(editForm.category),
        step: editForm.step,
      })
      toast({
        title: "Success",
        description: "Part updated successfully",
      })
      setIsEditDialogOpen(false)
      setSelectedPart(null)
      loadParts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update part",
        variant: "destructive",
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this part?")) return

    try {
      await partService.delete(id)
      toast({
        title: "Success",
        description: "Part deleted successfully",
      })
      loadParts()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete part",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Parts</h1>
        <p className="text-muted-foreground">Manage bike parts for your categories</p>
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
              <DialogDescription>Create a new part for a category in the bike configurator</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Part Name</Label>
                <Input
                  id="name"
                  placeholder="Frame"
                  value={addForm.name}
                  onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="category">Category</Label>
                <Select value={addForm.category} onValueChange={(value) => setAddForm({ ...addForm, category: value })}>
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
              <div className="grid gap-2">
                <Label htmlFor="step">Step Number</Label>
                <Input
                  id="step"
                  type="number"
                  min="1"
                  placeholder="1"
                  value={addForm.step}
                  onChange={(e) => setAddForm({ ...addForm, step: parseInt(e.target.value) || 1 })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAdd} disabled={!addForm.name || !addForm.category}>
                Save Part
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-24 items-center justify-center">
              <p className="text-muted-foreground">Loading...</p>
            </div>
          ) : (
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
                      Category
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
                        <Link to={`/dashboard/categories`} className="text-primary hover:underline">
                          {part.category_name || `Category #${part.category}`}
                        </Link>
                      </TableCell>
                      <TableCell>{part.step}</TableCell>
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
                            <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(part.id)}>
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
          )}
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
                <Input
                  id="edit-name"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-category">Category</Label>
                <Select value={editForm.category} onValueChange={(value) => setEditForm({ ...editForm, category: value })}>
                  <SelectTrigger id="edit-category">
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
              <div className="grid gap-2">
                <Label htmlFor="edit-step">Step Number</Label>
                <Input
                  id="edit-step"
                  type="number"
                  min="1"
                  value={editForm.step}
                  onChange={(e) => setEditForm({ ...editForm, step: parseInt(e.target.value) || 1 })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={!editForm.name || !editForm.category}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
