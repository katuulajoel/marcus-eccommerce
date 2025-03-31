"use client"

import { useState } from "react"
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

// Sample data
const customers = [
  {
    id: "1",
    name: "John Smith",
    email: "john.smith@example.com",
    ordersCount: 3,
    totalSpent: 2499.97,
    joinedDate: new Date("2023-01-15"),
    address: "123 Main St, Anytown, CA 12345",
    phone: "(555) 123-4567",
    orders: [
      { id: "ORD-001", date: new Date("2023-05-15"), total: 899.99, status: "Completed" },
      { id: "ORD-006", date: new Date("2023-07-10"), total: 799.99, status: "Shipped" },
      { id: "ORD-012", date: new Date("2023-09-22"), total: 799.99, status: "Completed" },
    ],
  },
  {
    id: "2",
    name: "Jane Doe",
    email: "jane.doe@example.com",
    ordersCount: 1,
    totalSpent: 599.99,
    joinedDate: new Date("2023-02-20"),
    address: "456 Oak Ave, Somewhere, NY 67890",
    phone: "(555) 234-5678",
    orders: [{ id: "ORD-002", date: new Date("2023-05-20"), total: 599.99, status: "Pending" }],
  },
  {
    id: "3",
    name: "Robert Johnson",
    email: "robert.johnson@example.com",
    ordersCount: 2,
    totalSpent: 2149.98,
    joinedDate: new Date("2023-03-10"),
    address: "789 Pine Rd, Elsewhere, TX 54321",
    phone: "(555) 345-6789",
    orders: [
      { id: "ORD-003", date: new Date("2023-05-25"), total: 1299.99, status: "Shipped" },
      { id: "ORD-009", date: new Date("2023-08-15"), total: 849.99, status: "Completed" },
    ],
  },
  {
    id: "4",
    name: "Emily Wilson",
    email: "emily.wilson@example.com",
    ordersCount: 1,
    totalSpent: 749.99,
    joinedDate: new Date("2023-04-05"),
    address: "321 Elm St, Nowhere, WA 13579",
    phone: "(555) 456-7890",
    orders: [{ id: "ORD-004", date: new Date("2023-06-01"), total: 749.99, status: "Cancelled" }],
  },
  {
    id: "5",
    name: "Michael Brown",
    email: "michael.brown@example.com",
    ordersCount: 2,
    totalSpent: 1699.98,
    joinedDate: new Date("2023-05-12"),
    address: "654 Maple Dr, Somewhere, FL 97531",
    phone: "(555) 567-8901",
    orders: [
      { id: "ORD-005", date: new Date("2023-06-05"), total: 849.99, status: "Pending" },
      { id: "ORD-011", date: new Date("2023-09-10"), total: 849.99, status: "Completed" },
    ],
  },
]

export default function CustomersPage() {
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState<(typeof customers)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 5

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage)
  const paginatedCustomers = filteredCustomers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  const handleView = (customer: (typeof customers)[0]) => {
    setSelectedCustomer(customer)
    setIsViewDialogOpen(true)
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
              {paginatedCustomers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No customers found.
                  </TableCell>
                </TableRow>
              ) : (
                paginatedCustomers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell className="font-medium">{customer.name}</TableCell>
                    <TableCell>{customer.email}</TableCell>
                    <TableCell>{customer.ordersCount}</TableCell>
                    <TableCell>{format(customer.joinedDate, "MMM d, yyyy")}</TableCell>
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
                      <div className="rounded-md border p-2">{selectedCustomer.name}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Email</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.email}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Phone</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.phone}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Joined Date</Label>
                      <div className="rounded-md border p-2">{format(selectedCustomer.joinedDate, "MMMM d, yyyy")}</div>
                    </div>
                    <div className="col-span-2 grid gap-2">
                      <Label>Address</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.address}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Total Orders</Label>
                      <div className="rounded-md border p-2">{selectedCustomer.ordersCount}</div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Total Spent</Label>
                      <div className="rounded-md border p-2 font-bold">${selectedCustomer.totalSpent.toFixed(2)}</div>
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
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedCustomer.orders.map((order) => (
                        <TableRow key={order.id}>
                          <TableCell>
                            <Link to={`/dashboard/orders`} className="text-primary hover:underline">
                              {order.id}
                            </Link>
                          </TableCell>
                          <TableCell>{format(order.date, "MMM d, yyyy")}</TableCell>
                          <TableCell>${order.total.toFixed(2)}</TableCell>
                          <TableCell>{order.status}</TableCell>
                        </TableRow>
                      ))}
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

