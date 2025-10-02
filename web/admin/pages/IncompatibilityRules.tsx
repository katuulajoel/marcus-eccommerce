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
import { Textarea } from "@shared/components/ui/textarea"
import { useToast } from "@shared/hooks/use-toast"
import { incompatibilityService, type IncompatibilityRule } from "../services/incompatibility-service"
import { partOptionService, type PartOption } from "../services/part-option-service"

export default function IncompatibilityRulesPage() {
  const [incompatibilityRules, setIncompatibilityRules] = useState<IncompatibilityRule[]>([])
  const [partOptions, setPartOptions] = useState<PartOption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedRule, setSelectedRule] = useState<IncompatibilityRule | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const { toast } = useToast()

  const [addForm, setAddForm] = useState({
    part_option: "",
    incompatible_with_option: "",
    message: "",
  })

  const [editForm, setEditForm] = useState({
    part_option: "",
    incompatible_with_option: "",
    message: "",
  })

  useEffect(() => {
    loadIncompatibilityRules()
    loadPartOptions()
  }, [])

  const loadIncompatibilityRules = async () => {
    try {
      setIsLoading(true)
      const data = await incompatibilityService.getAll()
      setIncompatibilityRules(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load incompatibility rules",
        variant: "destructive",
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
        variant: "destructive",
      })
    }
  }

  const filteredRules = incompatibilityRules.filter(
    (rule) =>
      (rule.option_a_name && rule.option_a_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (rule.option_b_name && rule.option_b_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      rule.message.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleEdit = (rule: IncompatibilityRule) => {
    setSelectedRule(rule)
    setEditForm({
      part_option: rule.part_option.toString(),
      incompatible_with_option: rule.incompatible_with_option.toString(),
      message: rule.message,
    })
    setIsEditDialogOpen(true)
  }

  const handleAdd = async () => {
    try {
      await incompatibilityService.create({
        part_option: parseInt(addForm.part_option),
        incompatible_with_option: parseInt(addForm.incompatible_with_option),
        message: addForm.message,
      })
      toast({
        title: "Success",
        description: "Incompatibility rule created successfully",
      })
      setIsAddDialogOpen(false)
      setAddForm({ part_option: "", incompatible_with_option: "", message: "" })
      loadIncompatibilityRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create incompatibility rule",
        variant: "destructive",
      })
    }
  }

  const handleUpdate = async () => {
    if (!selectedRule) return

    try {
      await incompatibilityService.update(selectedRule.id, {
        part_option: parseInt(editForm.part_option),
        incompatible_with_option: parseInt(editForm.incompatible_with_option),
        message: editForm.message,
      })
      toast({
        title: "Success",
        description: "Incompatibility rule updated successfully",
      })
      setIsEditDialogOpen(false)
      setSelectedRule(null)
      loadIncompatibilityRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update incompatibility rule",
        variant: "destructive",
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this incompatibility rule?")) return

    try {
      await incompatibilityService.delete(id)
      toast({
        title: "Success",
        description: "Incompatibility rule deleted successfully",
      })
      loadIncompatibilityRules()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete incompatibility rule",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Incompatibility Rules</h1>
        <p className="text-muted-foreground">
          Define which part options are incompatible with each other in the configurator
        </p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search incompatibility rules..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Incompatibility Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[550px]">
            <DialogHeader>
              <DialogTitle>Add New Incompatibility Rule</DialogTitle>
              <DialogDescription>
                Define two part options that cannot be selected together
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="option-a">Part Option A</Label>
                <Select
                  value={addForm.part_option}
                  onValueChange={(value) => setAddForm({ ...addForm, part_option: value })}
                >
                  <SelectTrigger id="option-a">
                    <SelectValue placeholder="Select first option" />
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
                <Label htmlFor="option-b">Part Option B (Incompatible with)</Label>
                <Select
                  value={addForm.incompatible_with_option}
                  onValueChange={(value) => setAddForm({ ...addForm, incompatible_with_option: value })}
                >
                  <SelectTrigger id="option-b">
                    <SelectValue placeholder="Select incompatible option" />
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
                <Label htmlFor="message">Incompatibility Message</Label>
                <Textarea
                  id="message"
                  placeholder="These options cannot be selected together..."
                  value={addForm.message}
                  onChange={(e) => setAddForm({ ...addForm, message: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAdd} disabled={!addForm.part_option || !addForm.incompatible_with_option || !addForm.message}>
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
                  <TableHead className="w-[200px]">Part Option A</TableHead>
                  <TableHead className="w-[200px]">Incompatible With</TableHead>
                  <TableHead className="w-[300px]">Message</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRules.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="h-24 text-center">
                      No incompatibility rules found.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredRules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">
                        {rule.option_a_name || `Option #${rule.part_option}`}
                      </TableCell>
                      <TableCell>{rule.option_b_name || `Option #${rule.incompatible_with_option}`}</TableCell>
                      <TableCell className="max-w-[300px] truncate">{rule.message}</TableCell>
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
            <DialogTitle>Edit Incompatibility Rule</DialogTitle>
            <DialogDescription>Update the incompatibility rule details</DialogDescription>
          </DialogHeader>
          {selectedRule && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-option-a">Part Option A</Label>
                <Select
                  value={editForm.part_option}
                  onValueChange={(value) => setEditForm({ ...editForm, part_option: value })}
                >
                  <SelectTrigger id="edit-option-a">
                    <SelectValue placeholder="Select first option" />
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
                <Label htmlFor="edit-option-b">Part Option B (Incompatible with)</Label>
                <Select
                  value={editForm.incompatible_with_option}
                  onValueChange={(value) => setEditForm({ ...editForm, incompatible_with_option: value })}
                >
                  <SelectTrigger id="edit-option-b">
                    <SelectValue placeholder="Select incompatible option" />
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
                <Label htmlFor="edit-message">Incompatibility Message</Label>
                <Textarea
                  id="edit-message"
                  value={editForm.message}
                  onChange={(e) => setEditForm({ ...editForm, message: e.target.value })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={!editForm.part_option || !editForm.incompatible_with_option || !editForm.message}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
