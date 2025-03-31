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
const priceRules = [
  {
    id: "1",
    conditionOptionId: "2",
    conditionOptionName: "Carbon Fiber Frame",
    affectedOptionId: "4",
    affectedOptionName: "Performance Wheels",
    adjustment: -50.0,
  },
  {
    id: "2",
    conditionOptionId: "1",
    conditionOptionName: "Aluminum Frame",
    affectedOptionId: "3",
    affectedOptionName: "Standard Wheels",
    adjustment: -20.0,
  },
  {
    id: "3",
    conditionOptionId: "4",
    conditionOptionName: "Performance Wheels",
    affectedOptionId: "5",
    affectedOptionName: "Flat Handlebars",
    adjustment: 15.0,
  },
]

const partOptions = [
  { id: "1", name: "Aluminum Frame" },
  { id: "2", name: "Carbon Fiber Frame" },
  { id: "3", name: "Standard Wheels" },
  { id: "4", name: "Performance Wheels" },
  { id: "5", name: "Flat Handlebars" },
]

export default function PriceRulesPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedRule, setSelectedRule] = useState<(typeof priceRules)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredRules = priceRules.filter(
    (rule) =>
      rule.conditionOptionName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rule.affectedOptionName.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleEdit = (rule: (typeof priceRules)[0]) => {
    setSelectedRule(rule)
    setIsEditDialogOpen(true)
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Price Adjustment Rules</h1>
        <p className="text-muted-foreground">Manage price adjustments between different part options</p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search rules..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add Price Adjustment Rule</DialogTitle>
              <DialogDescription>Create a new price adjustment rule between part options</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="condition-option">Condition Option</Label>
                <Select>
                  <SelectTrigger id="condition-option">
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="affected-option">Affected Option</Label>
                <Select>
                  <SelectTrigger id="affected-option">
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="adjustment">Price Adjustment ($)</Label>
                <Input id="adjustment" type="number" step="0.01" placeholder="-50.00 or 25.00" />
                <p className="text-sm text-muted-foreground">
                  Use negative values for discounts, positive for additional costs
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsAddDialogOpen(false)}>Save Rule</Button>
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
                    Condition Option
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[250px]">
                  <div className="flex items-center gap-1">
                    Affected Option
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Adjustment
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="h-24 text-center">
                    No rules found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredRules.map((rule) => (
                  <TableRow key={rule.id}>
                    <TableCell className="font-medium">{rule.conditionOptionName}</TableCell>
                    <TableCell>{rule.affectedOptionName}</TableCell>
                    <TableCell className={rule.adjustment < 0 ? "text-green-600" : "text-red-600"}>
                      {rule.adjustment < 0 ? "-" : "+"}${Math.abs(rule.adjustment).toFixed(2)}
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
                          <DropdownMenuItem onClick={() => handleEdit(rule)}>
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

      {/* Edit Rule Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Edit Price Adjustment Rule</DialogTitle>
            <DialogDescription>Update the price adjustment rule</DialogDescription>
          </DialogHeader>
          {selectedRule && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-condition-option">Condition Option</Label>
                <Select defaultValue={selectedRule.conditionOptionId}>
                  <SelectTrigger id="edit-condition-option">
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-affected-option">Affected Option</Label>
                <Select defaultValue={selectedRule.affectedOptionId}>
                  <SelectTrigger id="edit-affected-option">
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {partOptions.map((option) => (
                      <SelectItem key={option.id} value={option.id}>
                        {option.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-adjustment">Price Adjustment ($)</Label>
                <Input id="edit-adjustment" type="number" step="0.01" defaultValue={selectedRule.adjustment} />
                <p className="text-sm text-muted-foreground">
                  Use negative values for discounts, positive for additional costs
                </p>
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

