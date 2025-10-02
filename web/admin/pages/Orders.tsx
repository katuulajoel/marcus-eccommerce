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
    amountPaid: 899.99,
    minimumRequiredAmount: 629.99,
    paymentStatus: "completed",
    isFulfillable: true,
    status: "Completed",
    createdAt: new Date("2023-05-15"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame", price: 300, minimumPayment: 210 },
      { partName: "Wheels", optionName: "Performance Wheels", price: 400, minimumPayment: 320 },
      { partName: "Handlebars", optionName: "Flat Handlebars", price: 199.99, minimumPayment: 99.99 },
    ],
    shippingAddress: "123 Main St, Anytown, CA 12345",
    paymentMethod: "Credit Card",
    payments: [
      { id: 1, amount: 899.99, method: "Credit Card", date: new Date("2023-05-15"), paidBy: "customer" },
    ],
  },
  {
    id: "ORD-002",
    customerId: "2",
    customerName: "Jane Doe",
    customerEmail: "jane.doe@example.com",
    totalPrice: 599.99,
    amountPaid: 419.99,
    minimumRequiredAmount: 419.99,
    paymentStatus: "partial",
    isFulfillable: true,
    status: "Pending",
    createdAt: new Date("2023-05-20"),
    selectedOptions: [
      { partName: "Frame", optionName: "Aluminum Frame", price: 200, minimumPayment: 140 },
      { partName: "Wheels", optionName: "Standard Wheels", price: 250, minimumPayment: 175 },
      { partName: "Handlebars", optionName: "Comfort Handlebars", price: 149.99, minimumPayment: 104.99 },
    ],
    shippingAddress: "456 Oak Ave, Somewhere, NY 67890",
    paymentMethod: "PayPal",
    payments: [
      { id: 2, amount: 419.99, method: "PayPal", date: new Date("2023-05-20"), paidBy: "customer" },
    ],
  },
  {
    id: "ORD-003",
    customerId: "3",
    customerName: "Robert Johnson",
    customerEmail: "robert.johnson@example.com",
    totalPrice: 1299.99,
    amountPaid: 1299.99,
    minimumRequiredAmount: 909.99,
    paymentStatus: "completed",
    isFulfillable: true,
    status: "Shipped",
    createdAt: new Date("2023-05-25"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame", price: 300, minimumPayment: 210 },
      { partName: "Wheels", optionName: "Aero Wheels", price: 700, minimumPayment: 490 },
      { partName: "Handlebars", optionName: "Drop Handlebars", price: 299.99, minimumPayment: 209.99 },
    ],
    shippingAddress: "789 Pine Rd, Elsewhere, TX 54321",
    paymentMethod: "Credit Card",
    payments: [
      { id: 3, amount: 1299.99, method: "Credit Card", date: new Date("2023-05-25"), paidBy: "customer" },
    ],
  },
  {
    id: "ORD-004",
    customerId: "4",
    customerName: "Emily Wilson",
    customerEmail: "emily.wilson@example.com",
    totalPrice: 749.99,
    amountPaid: 0,
    minimumRequiredAmount: 524.99,
    paymentStatus: "pending",
    isFulfillable: false,
    status: "Cancelled",
    createdAt: new Date("2023-06-01"),
    selectedOptions: [
      { partName: "Frame", optionName: "Aluminum Frame", price: 200, minimumPayment: 140 },
      { partName: "Wheels", optionName: "Performance Wheels", price: 400, minimumPayment: 280 },
      { partName: "Handlebars", optionName: "Flat Handlebars", price: 149.99, minimumPayment: 104.99 },
    ],
    shippingAddress: "321 Elm St, Nowhere, WA 13579",
    paymentMethod: "PayPal",
    payments: [],
  },
  {
    id: "ORD-005",
    customerId: "5",
    customerName: "Michael Brown",
    customerEmail: "michael.brown@example.com",
    totalPrice: 849.99,
    amountPaid: 200,
    minimumRequiredAmount: 594.99,
    paymentStatus: "pending",
    isFulfillable: false,
    status: "Pending",
    createdAt: new Date("2023-06-05"),
    selectedOptions: [
      { partName: "Frame", optionName: "Carbon Fiber Frame", price: 300, minimumPayment: 210 },
      { partName: "Wheels", optionName: "Standard Wheels", price: 350, minimumPayment: 245 },
      { partName: "Handlebars", optionName: "Comfort Handlebars", price: 199.99, minimumPayment: 139.99 },
    ],
    shippingAddress: "654 Maple Dr, Somewhere, FL 97531",
    paymentMethod: "Credit Card",
    payments: [
      { id: 4, amount: 200, method: "Credit Card", date: new Date("2023-06-05"), paidBy: "customer" },
    ],
  },
]

export default function OrdersPage() {
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [isRecordPaymentDialogOpen, setIsRecordPaymentDialogOpen] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<(typeof orders)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [paymentAmount, setPaymentAmount] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("Credit Card")
  const [paidBy, setPaidBy] = useState("customer")

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

  const getPaymentStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "success"
      case "partial":
        return "info"
      case "pending":
        return "warning"
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
                <TableHead className="w-[120px]">
                  <div className="flex items-center gap-1">
                    Total Price
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[120px]">Amount Paid</TableHead>
                <TableHead className="w-[130px]">Payment Status</TableHead>
                <TableHead className="w-[120px]">Order Status</TableHead>
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
                  <TableCell colSpan={8} className="h-24 text-center">
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
                      <div className="flex flex-col">
                        <span>${order.amountPaid.toFixed(2)}</span>
                        <span className="text-sm text-muted-foreground">
                          of ${order.minimumRequiredAmount.toFixed(2)} min
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        <Badge variant={getPaymentStatusBadgeVariant(order.paymentStatus) as any}>
                          {order.paymentStatus.charAt(0).toUpperCase() + order.paymentStatus.slice(1)}
                        </Badge>
                        {order.isFulfillable && (
                          <span className="text-xs text-green-600">✓ Fulfillable</span>
                        )}
                      </div>
                    </TableCell>
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
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="details">Order Details</TabsTrigger>
                  <TabsTrigger value="payment">Payment Info</TabsTrigger>
                  <TabsTrigger value="configuration">Configuration</TabsTrigger>
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
                <TabsContent value="payment" className="grid gap-4 py-4">
                  <div className="grid gap-4">
                    {/* Payment Summary */}
                    <div className="rounded-lg border p-4 bg-muted/50">
                      <h3 className="font-semibold mb-3">Payment Summary</h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-muted-foreground">Total Price</Label>
                          <div className="text-lg font-bold">${selectedOrder.totalPrice.toFixed(2)}</div>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Amount Paid</Label>
                          <div className="text-lg font-bold text-green-600">${selectedOrder.amountPaid.toFixed(2)}</div>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Minimum Required</Label>
                          <div className="text-lg font-semibold">${selectedOrder.minimumRequiredAmount.toFixed(2)}</div>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Balance Due</Label>
                          <div className="text-lg font-semibold text-orange-600">
                            ${(selectedOrder.totalPrice - selectedOrder.amountPaid).toFixed(2)}
                          </div>
                        </div>
                        <div className="col-span-2">
                          <Label className="text-muted-foreground">Payment Status</Label>
                          <div className="mt-1 flex items-center gap-2">
                            <Badge variant={getPaymentStatusBadgeVariant(selectedOrder.paymentStatus) as any}>
                              {selectedOrder.paymentStatus.charAt(0).toUpperCase() + selectedOrder.paymentStatus.slice(1)}
                            </Badge>
                            {selectedOrder.isFulfillable && (
                              <span className="text-sm text-green-600">✓ Can be fulfilled</span>
                            )}
                            {!selectedOrder.isFulfillable && (
                              <span className="text-sm text-orange-600">⚠ Cannot be fulfilled yet</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Payment History */}
                    <div>
                      <div className="flex justify-between items-center mb-3">
                        <Label>Payment History</Label>
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => setIsRecordPaymentDialogOpen(true)}
                          disabled={selectedOrder.paymentStatus === "completed"}
                        >
                          Record Payment
                        </Button>
                      </div>
                      {selectedOrder.payments.length > 0 ? (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Date</TableHead>
                              <TableHead>Amount</TableHead>
                              <TableHead>Method</TableHead>
                              <TableHead>Paid By</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {selectedOrder.payments.map((payment) => (
                              <TableRow key={payment.id}>
                                <TableCell>{format(payment.date, "MMM d, yyyy")}</TableCell>
                                <TableCell className="font-semibold">${payment.amount.toFixed(2)}</TableCell>
                                <TableCell>{payment.method}</TableCell>
                                <TableCell className="capitalize">{payment.paidBy.replace('_', ' ')}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground border rounded-md">
                          No payments recorded yet
                        </div>
                      )}
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

      {/* Record Payment Dialog */}
      <Dialog open={isRecordPaymentDialogOpen} onOpenChange={setIsRecordPaymentDialogOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Record Payment</DialogTitle>
            <DialogDescription>
              Record a new payment for Order {selectedOrder?.id}
            </DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="grid gap-4 py-4">
              <div className="rounded-lg border p-3 bg-muted/50">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Total Price:</span>
                  <span className="font-semibold">${selectedOrder.totalPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Already Paid:</span>
                  <span className="font-semibold text-green-600">${selectedOrder.amountPaid.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Remaining Balance:</span>
                  <span className="font-semibold text-orange-600">
                    ${(selectedOrder.totalPrice - selectedOrder.amountPaid).toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="amount">Payment Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="0.00"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  min="0"
                  max={selectedOrder.totalPrice - selectedOrder.amountPaid}
                  step="0.01"
                />
                <p className="text-xs text-muted-foreground">
                  Maximum: ${(selectedOrder.totalPrice - selectedOrder.amountPaid).toFixed(2)}
                </p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="paymentMethod">Payment Method *</Label>
                <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                  <SelectTrigger id="paymentMethod">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Credit Card">Credit Card</SelectItem>
                    <SelectItem value="PayPal">PayPal</SelectItem>
                    <SelectItem value="Cash">Cash</SelectItem>
                    <SelectItem value="Bank Transfer">Bank Transfer</SelectItem>
                    <SelectItem value="Mobile Money">Mobile Money</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="paidBy">Paid By *</Label>
                <Select value={paidBy} onValueChange={setPaidBy}>
                  <SelectTrigger id="paidBy">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="delivery_person">Delivery Person</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsRecordPaymentDialogOpen(false)
              setPaymentAmount("")
              setPaymentMethod("Credit Card")
              setPaidBy("customer")
            }}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                // TODO: Implement payment recording logic
                console.log("Recording payment:", {
                  orderId: selectedOrder?.id,
                  amount: paymentAmount,
                  method: paymentMethod,
                  paidBy: paidBy,
                })
                setIsRecordPaymentDialogOpen(false)
                setPaymentAmount("")
                setPaymentMethod("Credit Card")
                setPaidBy("customer")
              }}
              disabled={!paymentAmount || parseFloat(paymentAmount) <= 0}
            >
              Record Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

