"use client"

import { useState, useEffect } from "react"
import { format } from "date-fns"
import { Link } from "react-router-dom"
import { ArrowUpDown, Eye, MoreHorizontal, Search } from "lucide-react"
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
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@shared/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/components/ui/tabs"
import { customerService, type Customer, type CustomerOrder } from "@admin/services/customer-service"
import { orderService, type Order } from "@admin/services/order-service"

interface CustomerWithStats extends Customer {
  ordersCount: number;
  totalSpent: number;
}

export default function CustomersPage() {
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerWithStats | null>(null)
  const [selectedCustomerOrders, setSelectedCustomerOrders] = useState<Order[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [customers, setCustomers] = useState<CustomerWithStats[]>([])
  const [loading, setLoading] = useState(true)
  const itemsPerPage = 5

  useEffect(() => {
    loadCustomers()
  }, [])

  const loadCustomers = async () => {
    try {
      setLoading(true)
      const [customersData, ordersData] = await Promise.all([
        customerService.getAll(),
        orderService.getAll()
      ])

      // Calculate stats for each customer
      const customersWithStats: CustomerWithStats[] = customersData.map(customer => {
        const customerOrders = ordersData.filter(order => order.customer === customer.id)
        const totalSpent = Number(customerOrders.reduce((sum, order) => sum + Number(order.total_price || 0), 0).toFixed(2))

        return {
          ...customer,
          ordersCount: customerOrders.length,
          totalSpent
        }
      })

      setCustomers(customersWithStats)
    } catch (error) {
      console.error('Failed to load customers:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      customer.email?.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage)
  const paginatedCustomers = filteredCustomers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  const handleView = async (customer: CustomerWithStats) => {
    try {
      // Fetch customer's orders
      const allOrders = await orderService.getAll()
      const customerOrders = allOrders.filter(order => order.customer === customer.id)
      setSelectedCustomerOrders(customerOrders)
      setSelectedCustomer(customer)
      setIsViewDialogOpen(true)
    } catch (error) {
      console.error('Failed to load customer orders:', error)
      setSelectedCustomer(customer)
      setSelectedCustomerOrders([])
      setIsViewDialogOpen(true)
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
        <p className="text-muted-foreground">Manage customer accounts and view order history</p>
      </div>

      <div className="flex w-full items-center gap-2 md:w-1/3">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search customers..."
          className="w-full"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[250px]">
                  <div className="flex items-center gap-1">
                    Name
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[250px]">Email</TableHead>
                <TableHead className="w-[120px]">
                  <div className="flex items-center gap-1">
                    Orders
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[150px]">
                  <div className="flex items-center gap-1">
                    Joined Date
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <ArrowUpDown className="h-3 w-3" />
                    </Button>
                  </div>
                </TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    Loading customers...
                  </TableCell>
                </TableRow>
              ) : paginatedCustomers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No customers found.
                  </TableCell>
                </TableRow>
              ) : (
                paginatedCustomers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell className="font-medium">{customer.name || 'N/A'}</TableCell>
                    <TableCell>{customer.email || 'N/A'}</TableCell>
                    <TableCell>{customer.ordersCount}</TableCell>
                    <TableCell>{format(new Date(customer.created_at), "MMM d, yyyy")}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleView(customer)}>
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

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-end space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <div className="text-sm">
            Page {currentPage} of {totalPages}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </Button>
        </div>
      )}

      {/* View Customer Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="sm:max-w-[650px]">
          <DialogHeader>
            <DialogTitle>Customer Details</DialogTitle>
            <DialogDescription>View customer information and order history</DialogDescription>
          </DialogHeader>
          {selectedCustomer && (
            <div className="grid gap-6 py-4">
              <Tabs defaultValue="details">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="details">Customer Details</TabsTrigger>
                  <TabsTrigger value="orders">Order History</TabsTrigger>
                </TabsList>
                <TabsContent value="details" className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Name</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.name || 'N/A'}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Email</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.email || 'N/A'}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Phone</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.phone || 'N/A'}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Joined Date</Label>
                      <div className="rounded-md border p-2">{format(new Date(selectedCustomer.created_at), "MMMM d, yyyy")}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Total Orders</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.ordersCount}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Total Spent</Label>
                      <div className="rounded-md border p-2 font-bold">${Number(selectedCustomer.totalSpent).toFixed(2)}</div>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="orders" className="grid gap-4 py-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Order ID</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Total</TableHead>
                        <TableHead>Paid</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedCustomerOrders.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                            No orders found
                          </TableCell>
                        </TableRow>
                      ) : (
                        selectedCustomerOrders.map((order) => (
                          <TableRow key={order.id}>
                            <TableCell>
                              Order ORD-{order.id.toString().padStart(3, "0")}
                            </TableCell>
                            <TableCell>{format(new Date(order.created_at), "MMM d, yyyy")}</TableCell>
                            <TableCell className="font-medium">${Number(order.total_price).toFixed(2)}</TableCell>
                            <TableCell className="text-green-600">${Number(order.amount_paid).toFixed(2)}</TableCell>
                            <TableCell>
                              <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                                order.fulfillment_status === 'in_production' ? 'bg-yellow-100 text-yellow-700' :
                                order.fulfillment_status === 'ready_for_pickup' ? 'bg-yellow-100 text-yellow-700' :
                                order.fulfillment_status === 'in_delivery' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {order.fulfillment_status.charAt(0).toUpperCase() + order.fulfillment_status.slice(1)}
                              </span>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
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

