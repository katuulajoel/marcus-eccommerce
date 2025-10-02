/**
 * Order service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface ShippingAddress {
  id: number;
  recipient_name: string;
  phone_number: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state_province?: string;
  postal_code?: string;
  country: string;
}

export interface Payment {
  id: number;
  amount: number;
  payment_method: string;
  payment_date: string;
  paid_by: 'customer' | 'delivery_person';
  transaction_reference?: string;
}

export interface OrderItem {
  id: number;
  part_name: string;
  option_name: string;
  final_price: number;
  minimum_payment_required: number;
}

export interface OrderProduct {
  id: number;
  preconfigured_product?: number;
  custom_name?: string;
  base_product_name: string;
  items: OrderItem[];
}

export interface Order {
  id: number;
  customer: number;
  customer_name?: string;
  customer_email?: string;
  shipping_address?: ShippingAddress;
  total_price: number;
  minimum_required_amount: number;
  amount_paid: number;
  payment_status: 'pending' | 'partial' | 'completed';
  is_fulfillable: boolean;
  created_at: string;
  products: OrderProduct[];
  payments: Payment[];
  balance_due: number;
}

export interface RecordPaymentInput {
  amount: number;
  payment_method: string;
  paid_by: 'customer' | 'delivery_person';
  transaction_reference?: string;
}

/**
 * Order service for admin operations
 */
export const orderService = {
  /**
   * Get all orders
   */
  getAll: async (): Promise<Order[]> => {
    const response = await adminApiClient.get<Order[]>('/api/orders/');
    return response.data;
  },

  /**
   * Get single order by ID
   */
  getById: async (id: number): Promise<Order> => {
    const response = await adminApiClient.get<Order>(`/api/orders/${id}/`);
    return response.data;
  },

  /**
   * Record a payment for an order
   */
  recordPayment: async (orderId: number, data: RecordPaymentInput): Promise<{ message: string; payment: Payment; order: Order }> => {
    const response = await adminApiClient.post(`/api/orders/${orderId}/record_payment/`, data);
    return response.data;
  },

  /**
   * Update order status (if needed)
   */
  updateStatus: async (id: number, status: string): Promise<Order> => {
    const response = await adminApiClient.patch<Order>(`/api/orders/${id}/`, { status });
    return response.data;
  },
};
