"use client"

import { useState, useEffect } from "react"
import { Edit, MoreHorizontal, Plus, Search, Trash } from "lucide-react"
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
import { useToast } from "@shared/hooks/use-toast"
import { priceRuleService, type PriceAdjustmentRule } from "../services/price-rule-service"
import { partOptionService, type PartOption } from "../services/part-option-service"

export default function PriceRulesPage() {
  const [priceRules, setPriceRules] = useState<PriceAdjustmentRule[]>([])
  const [partOptions, setPartOptions] = useState<PartOption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedRule, setSelectedRule] = useState<PriceAdjustmentRule | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()

  const [addForm, setAddForm] = useState({
    condition_option: "",
    affected_option: "",
    adjusted_price: 0,
  })

  const [editForm, setEditForm] = useState({
    condition_option: "",
    affected_option: "",
    adjusted_price: 0,
  })

  useEffect(() => {
    loadPriceRules()
    loadPartOptions()
  }, [])

  const loadPriceRules = async () => {
    try {
      setIsLoading(true)
      const data = await priceRuleService.getAll()
      setPriceRules(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load price adjustment rules",
        className: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadPartOptions = async () => {
    try {
      const data = await partOptionService.getAll()
      setPartOptions(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load part options",
        className: "destructive",
      })
    }
  }

  const filteredRules = priceRules.filter(
    (rule) =>
      (rule.condition_option_name && rule.condition_option_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (rule.affected_option_name && rule.affected_option_name.toLowerCase().includes(searchQuery.toLowerCase())),
  )

  const handleEdit = (rule: PriceAdjustmentRule) => {
    setSelectedRule(rule)
    setEditForm({
      condition_option: rule.condition_option.toString(),
      affected_option: rule.affected_option.toString(),
      adjusted_price: rule.adjusted_price,
    })
    setIsEditDialogOpen(true)
  }

  const handleAdd = async () => {
    try {
      await priceRuleService.create({
        condition_option: parseInt(addForm.condition_option),
        affected_option: parseInt(addForm.affected_option),
        adjusted_price: addForm.adjusted_price,
      })
      toast({
        title: "Success",
        description: "Price adjustment rule created successfully",
      })
      setIsAddDialogOpen(false)
      setAddForm({ condition_option: "", affected_option: "", adjusted_price: 0 })
      loadPriceRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create price adjustment rule",
        className: "destructive",
      })
    }
  }

  const handleUpdate = async () => {
    if (!selectedRule) return

    try {
      await priceRuleService.update(selectedRule.id, {
        condition_option: parseInt(editForm.condition_option),
        affected_option: parseInt(editForm.affected_option),
        adjusted_price: editForm.adjusted_price,
      })
      toast({
        title: "Success",
        description: "Price adjustment rule updated successfully",
      })
      setIsEditDialogOpen(false)
      setSelectedRule(null)
      loadPriceRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update price adjustment rule",
        className: "destructive",
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this price adjustment rule?")) return

    try {
      await priceRuleService.delete(id)
      toast({
        title: "Success",
        description: "Price adjustment rule deleted successfully",
      })
      loadPriceRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete price adjustment rule",
        className: "destructive",
      })
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Price Adjustment Rules</h1>
        <p className="text-muted-foreground">
          Manage dynamic pricing rules that adjust prices based on selected options
        </p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search price rules..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Price Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add New Price Adjustment Rule</DialogTitle>
              <DialogDescription>
                Create a rule that adjusts the price of one option based on another option being selected
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="condition">Condition Option (When selected)</Label>
                <Select
                  value={addForm.condition_option}
                  onValueChange={(value) => setAddForm({ ...addForm, condition_option: value })}
                >
                  <SelectTrigger id="condition">
                    <SelectValue placeholder="Select condition option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id.toString()}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="affected">Affected Option (Price will change)</Label>
                <Select
                  value={addForm.affected_option}
                  onValueChange={(value) => setAddForm({ ...addForm, affected_option: value })}
                >
                  <SelectTrigger id="affected">
                    <SelectValue placeholder="Select affected option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id.toString()}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="price">Adjusted Price ($)</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  placeholder="199.99"
                  value={addForm.adjusted_price}
                  onChange={(e) => setAddForm({ ...addForm, adjusted_price: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAdd} disabled={!addForm.condition_option || !addForm.affected_option}>
                Save Rule
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
                  <TableHead className="w-[250px]">Condition Option</TableHead>
                  <TableHead className="w-[250px]">Affected Option</TableHead>
                  <TableHead className="w-[150px]">Adjusted Price</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRules.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="h-24 text-center">
                      No price adjustment rules found.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredRules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">
                        {rule.condition_option_name || `Option #${rule.condition_option}`}
                      </TableCell>
                      <TableCell>{rule.affected_option_name || `Option #${rule.affected_option}`}</TableCell>
                      <TableCell>${Number(rule.adjusted_price).toFixed(2)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleEdit(rule)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive" onClick={() => handleDelete(rule.id)}>
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

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Edit Price Adjustment Rule</DialogTitle>
            <DialogDescription>Update the price adjustment rule details</DialogDescription>
          </DialogHeader>
          {selectedRule && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-condition">Condition Option (When selected)</Label>
                <Select
                  value={editForm.condition_option}
                  onValueChange={(value) => setEditForm({ ...editForm, condition_option: value })}
                >
                  <SelectTrigger id="edit-condition">
                    <SelectValue placeholder="Select condition option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id.toString()}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-affected">Affected Option (Price will change)</Label>
                <Select
                  value={editForm.affected_option}
                  onValueChange={(value) => setEditForm({ ...editForm, affected_option: value })}
                >
                  <SelectTrigger id="edit-affected">
                    <SelectValue placeholder="Select affected option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id.toString()}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-price">Adjusted Price ($)</Label>
                <Input
                  id="edit-price"
                  type="number"
                  step="0.01"
                  value={editForm.adjusted_price}
                  onChange={(e) => setEditForm({ ...editForm, adjusted_price: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={!editForm.condition_option || !editForm.affected_option}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
