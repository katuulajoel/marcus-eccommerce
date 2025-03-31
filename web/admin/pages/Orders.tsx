"use client"

import { useState } from "react"
import { format } from "date-fns"
import { ArrowUpDown, Eye, MoreHorizontal, Search } from "lucide-react"
import { Badge } from "@shared/components/ui/badge"
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/components/ui/tabs"

// Sample data
const orders = [
  {
    id: "ORD-001",
    customerId: "1",
    customerName: "John Smith",
    customerEmail: "john.smith@example.com",
    totalPrice: 899.99,
    status: "Completed",
    createdAt: new Date("2023-05-15"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame" },
      { partName: "Wheels", optionName: "Performance Wheels" },
      { partName: "Handlebars", optionName: "Flat Handlebars" },
    ],
    shippingAddress: "123 Main St, Anytown, CA 12345",
    paymentMethod: "Credit Card",
  },
  {
    id: "ORD-002",
    customerId: "2",
    customerName: "Jane Doe",
    customerEmail: "jane.doe@example.com",
    totalPrice: 599.99,
    status: "Pending",
    createdAt: new Date("2023-05-20"),
    selectedOptions: [
      { partName: "Frame", optionName: "Aluminum Frame" },
      { partName: "Wheels", optionName: "Standard Wheels" },
      { partName: "Handlebars", optionName: "Comfort Handlebars" },
    ],
    shippingAddress: "456 Oak Ave, Somewhere, NY 67890",
    paymentMethod: "PayPal",
  },
  {
    id: "ORD-003",
    customerId: "3",
    customerName: "Robert Johnson",
    customerEmail: "robert.johnson@example.com",
    totalPrice: 1299.99,
    status: "Shipped",
    createdAt: new Date("2023-05-25"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame" },
      { partName: "Wheels", optionName: "Aero Wheels" },
      { partName: "Handlebars", optionName: "Drop Handlebars" },
    ],
    shippingAddress: "789 Pine Rd, Elsewhere, TX 54321",
    paymentMethod: "Credit Card",
  },
  {
    id: "ORD-004",
    customerId: "4",
    customerName: "Emily Wilson",
    customerEmail: "emily.wilson@example.com",
    totalPrice: 749.99,
    status: "Cancelled",
    createdAt: new Date("2023-06-01"),
    selectedOptions: [
      { partName: "Frame", optionName: "Aluminum Frame" },
      { partName: "Wheels", optionName: "Performance Wheels" },
      { partName: "Handlebars", optionName: "Flat Handlebars" },
    ],
    shippingAddress: "321 Elm St, Nowhere, WA 13579",
    paymentMethod: "PayPal",
  },
  {
    id: "ORD-005",
    customerId: "5",
    customerName: "Michael Brown",
    customerEmail: "michael.brown@example.com",
    totalPrice: 849.99,
    status: "Pending",
    createdAt: new Date("2023-06-05"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame" },
      { partName: "Wheels", optionName: "Standard Wheels" },
      { partName: "Handlebars", optionName: "Comfort Handlebars" },
    ],
    shippingAddress: "654 Maple Dr, Somewhere, FL 97531",
    paymentMethod: "Credit Card",
  },
]

export default function OrdersPage() {
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<(typeof orders)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const filteredOrders = orders.filter((order) => {
    // Apply status filter
    if (statusFilter !== "all" && order.status.toLowerCase() !== statusFilter.toLowerCase()) {
      return false
    }

    // Apply search filter
    return (
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customerEmail.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  const handleView = (order: (typeof orders)[0]) => {
    setSelectedOrder(order)
    setIsViewDialogOpen(true)
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "success"
      case "pending":
        return "warning"
      case "shipped":
        return "info"
      case "cancelled":
        return "destructive"
      default:
        return "secondary"
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Orders</h1>
        <p className="text-muted-foreground">Manage customer orders for configured bikes</p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full items-center gap-2 md:w-1/3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search orders..."
            className="w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="shipped">Shipped</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[120px]">
                  <div className="flex items-center gap-1">
                    Order ID
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[200px]">
                  <div className="flex items-center gap-1">
                    Customer
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Total Price
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[120px]">Status</TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Created At
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredOrders.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    No orders found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell className="font-medium">{order.id}</TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span>{order.customerName}</span>
                        <span className="text-sm text-muted-foreground">{order.customerEmail}</span>
                      </div>
                    </TableCell>
                    <TableCell>${order.totalPrice.toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadgeVariant(order.status) as any}>{order.status}</Badge>
                    </TableCell>
                    <TableCell>{format(order.createdAt, "MMM d, yyyy")}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleView(order)}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
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

      {/* View Order Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="sm:max-w-[650px]">
          <DialogHeader>
            <DialogTitle>Order {selectedOrder?.id}</DialogTitle>
            <DialogDescription>Order details and configuration</DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="grid gap-6 py-4">
              <Tabs defaultValue="details">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="details">Order Details</TabsTrigger>
                  <TabsTrigger value="configuration">Bike Configuration</TabsTrigger>
                </TabsList>
                <TabsContent value="details" className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Customer</Label>
                      <div className="rounded-md border p-2">
                        <div>{selectedOrder.customerName}</div>
                        <div className="text-sm text-muted-foreground">{selectedOrder.customerEmail}</div>
                      </div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Status</Label>
                      <div className="rounded-md border p-2">
                        <Badge variant={getStatusBadgeVariant(selectedOrder.status) as any}>
                          {selectedOrder.status}
                        </Badge>
                      </div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Order Date</Label>
                      <div className="rounded-md border p-2">{format(selectedOrder.createdAt, "MMMM d, yyyy")}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Total Price</Label>
                      <div className="rounded-md border p-2 font-bold">${selectedOrder.totalPrice.toFixed(2)}</div>
                    </div>
                    <div className="col-span-2 grid gap-2">
                      <Label>Shipping Address</Label>
                      <div className="rounded-md border p-2">{selectedOrder.shippingAddress}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Payment Method</Label>
                      <div className="rounded-md border p-2">{selectedOrder.paymentMethod}</div>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="configuration" className="grid gap-4 py-4">
                  <div className="grid gap-4">
                    <Label>Selected Options</Label>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Part</TableHead>
                          <TableHead>Selected Option</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedOrder.selectedOptions.map((option, index) => (
                          <TableRow key={index}>
                            <TableCell>{option.partName}</TableCell>
                            <TableCell>{option.optionName}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

