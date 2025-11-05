"use client"

import { useState, useEffect } from "react"
import { ArrowUpDown, Edit, MoreHorizontal, Plus, Search, Trash, Image as ImageIcon } from "lucide-react"
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
import { Textarea } from "@shared/components/ui/textarea"
import { useToast } from "@shared/components/ui/use-toast"
import { useCurrency } from "@shared/contexts/currency-context"
import { partOptionService, type PartOption } from "../services/part-option-service"
import { partService, type Part } from "../services/part-service"
import { ImageUpload } from "@admin/components/ImageUpload"

export default function PartOptionsPage() {
  const [partOptions, setPartOptions] = useState<PartOption[]>([])
  const [parts, setParts] = useState<Part[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedOption, setSelectedOption] = useState<PartOption | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()
  const { formatAmount, convertAmount, selectedCurrency } = useCurrency()
  const [convertedPrices, setConvertedPrices] = useState<Record<number, number>>({})

  // Form state for add
  const [addForm, setAddForm] = useState({
    name: "",
    part: "",
    default_price: 0,
    minimum_payment_percentage: 0,
    image: null as File | null,
    description: "",
  })

  // Form state for edit
  const [editForm, setEditForm] = useState({
    name: "",
    part: "",
    default_price: 0,
    minimum_payment_percentage: 0,
    image: null as File | null,
    description: "",
  })

  useEffect(() => {
    loadPartOptions()
    loadParts()
  }, [])

  useEffect(() => {
    // Convert prices when currency changes
    const convertPrices = async () => {
      const converted: Record<number, number> = {}
      for (const option of partOptions) {
        const convertedPrice = await convertAmount(Number(option.default_price))
        converted[option.id] = convertedPrice
      }
      setConvertedPrices(converted)
    }
    if (partOptions.length > 0) {
      convertPrices()
    }
  }, [partOptions, selectedCurrency])

  const loadPartOptions = async () => {
    try {
      setIsLoading(true)
      const data = await partOptionService.getAll()
      setPartOptions(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load part options",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadParts = async () => {
    try {
      const data = await partService.getAll()
      setParts(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load parts",
        variant: "destructive",
      })
    }
  }

  const filteredOptions = partOptions.filter(
    (option) =>
      option.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (option.part_name && option.part_name.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleEdit = (option: PartOption) => {
    setSelectedOption(option)
    setEditForm({
      name: option.name,
      part: option.part.toString(),
      default_price: option.default_price,
      minimum_payment_percentage: option.minimum_payment_percentage || 0,
      image: null,
      description: option.description || "",
    })
    setIsEditDialogOpen(true)
  }

  const handleAdd = async () => {
    try {
      await partOptionService.create({
        name: addForm.name,
        part: parseInt(addForm.part),
        default_price: addForm.default_price,
        minimum_payment_percentage: addForm.minimum_payment_percentage,
        image: addForm.image || undefined,
        description: addForm.description || undefined,
      })
      toast({
        title: "Success",
        description: "Part option created successfully",
      })
      setIsAddDialogOpen(false)
      setAddForm({ name: "", part: "", default_price: 0, minimum_payment_percentage: 0, image: null, description: "" })
      loadPartOptions()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create part option",
        variant: "destructive",
      })
    }
  }

  const handleUpdate = async () => {
    if (!selectedOption) return

    try {
      await partOptionService.update(selectedOption.id, {
        name: editForm.name,
        part: parseInt(editForm.part),
        default_price: editForm.default_price,
        minimum_payment_percentage: editForm.minimum_payment_percentage,
        image: editForm.image || undefined,
        description: editForm.description || undefined,
      })
      toast({
        title: "Success",
        description: "Part option updated successfully",
      })
      setIsEditDialogOpen(false)
      setSelectedOption(null)
      loadPartOptions()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update part option",
        variant: "destructive",
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this part option?")) return

    try {
      await partOptionService.delete(id)
      toast({
        title: "Success",
        description: "Part option deleted successfully",
      })
      loadPartOptions()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete part option",
        variant: "destructive",
      })
    }
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
            placeholder="Search part options..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Part Option
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add New Part Option</DialogTitle>
              <DialogDescription>Create a new option for a specific part</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Option Name</Label>
                <Input
                  id="name"
                  placeholder="Aluminum Frame"
                  value={addForm.name}
                  onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="part">Part</Label>
                <Select value={addForm.part} onValueChange={(value) => setAddForm({ ...addForm, part: value })}>
                  <SelectTrigger id="part">
                    <SelectValue placeholder="Select a part" />
                  </SelectTrigger>
                  <SelectContent>
                    {parts.map((part) => (
                      <SelectItem key={part.id} value={part.id.toString()}>
                        {part.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="price">Default Price ($)</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="299.99"
                  value={addForm.default_price}
                  onChange={(e) => setAddForm({ ...addForm, default_price: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="minimum_payment_percentage">Minimum Payment Percentage (%)</Label>
                <Input
                  id="minimum_payment_percentage"
                  type="number"
                  step="1"
                  min="0"
                  max="100"
                  placeholder="70"
                  value={addForm.minimum_payment_percentage * 100}
                  onChange={(e) => setAddForm({ ...addForm, minimum_payment_percentage: (parseFloat(e.target.value) || 0) / 100 })}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum upfront payment required (0-100%). Example: 70 = 70% required upfront, 0 = no upfront payment required
                </p>
              </div>
              <ImageUpload
                label="Part Option Image"
                onImageChange={(file) => setAddForm({ ...addForm, image: file })}
              />
              <div className="grid gap-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="High-quality aluminum frame..."
                  value={addForm.description}
                  onChange={(e) => setAddForm({ ...addForm, description: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAdd} disabled={!addForm.name || !addForm.part}>
                Save Part Option
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
                  <TableHead className="w-[80px]">Image</TableHead>
                  <TableHead className="w-[220px]">Option Name</TableHead>
                  <TableHead className="w-[180px]">Part</TableHead>
                  <TableHead className="w-[130px]">Default Price</TableHead>
                  <TableHead className="w-[150px]">Min Payment %</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOptions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center">
                      No part options found.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredOptions.map((option) => (
                    <TableRow key={option.id}>
                      <TableCell>
                        {option.image_url ? (
                          <img
                            src={option.image_url}
                            alt={option.name}
                            className="w-12 h-12 object-cover rounded"
                          />
                        ) : (
                          <div className="w-12 h-12 bg-muted rounded flex items-center justify-center">
                            <ImageIcon className="h-6 w-6 text-muted-foreground" />
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="font-medium">{option.name}</TableCell>
                      <TableCell>{option.part_name || `Part #${option.part}`}</TableCell>
                      <TableCell>
                        {convertedPrices[option.id]
                          ? formatAmount(convertedPrices[option.id])
                          : formatAmount(Number(option.default_price))
                        }
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium">{((option.minimum_payment_percentage || 0) * 100).toFixed(0)}%</span>
                          <span className="text-xs text-muted-foreground">
                            {convertedPrices[option.id]
                              ? formatAmount(convertedPrices[option.id] * (option.minimum_payment_percentage || 0))
                              : formatAmount(Number(option.default_price) * (option.minimum_payment_percentage || 0))
                            } min
                          </span>
                        </div>
                      </TableCell>
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
                            <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(option.id)}>
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

      {/* Edit Part Option Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Edit Part Option</DialogTitle>
            <DialogDescription>Update the part option details</DialogDescription>
          </DialogHeader>
          {selectedOption && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-name">Option Name</Label>
                <Input
                  id="edit-name"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-part">Part</Label>
                <Select value={editForm.part} onValueChange={(value) => setEditForm({ ...editForm, part: value })}>
                  <SelectTrigger id="edit-part">
                    <SelectValue placeholder="Select a part" />
                  </SelectTrigger>
                  <SelectContent>
                    {parts.map((part) => (
                      <SelectItem key={part.id} value={part.id.toString()}>
                        {part.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-price">Default Price ($)</Label>
                <Input
                  id="edit-price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={editForm.default_price}
                  onChange={(e) => setEditForm({ ...editForm, default_price: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-minimum_payment_percentage">Minimum Payment Percentage (%)</Label>
                <Input
                  id="edit-minimum_payment_percentage"
                  type="number"
                  step="1"
                  min="0"
                  max="100"
                  value={editForm.minimum_payment_percentage * 100}
                  onChange={(e) => setEditForm({ ...editForm, minimum_payment_percentage: (parseFloat(e.target.value) || 0) / 100 })}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum upfront payment required (0-100%). Example: 70 = 70% required upfront, 0 = no upfront payment required
                </p>
              </div>
              <ImageUpload
                label="Part Option Image"
                currentImageUrl={selectedOption?.image_url}
                onImageChange={(file) => setEditForm({ ...editForm, image: file })}
                onImageClear={() => setEditForm({ ...editForm, image: null })}
              />
              <div className="grid gap-2">
                <Label htmlFor="edit-description">Description (optional)</Label>
                <Textarea
                  id="edit-description"
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={!editForm.name || !editForm.part}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
