import { adminApiClient } from './api-client';

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  created_at: string;
  orders_count?: number;
  total_spent?: number;
}

export interface CustomerOrder {
  id: number;
  order_id: string;
  created_at: string;
  total_amount: number;
  status: string;
}

export interface CustomerDetails extends Customer {
  orders: CustomerOrder[];
}

export const customerService = {
  async getAll(): Promise<Customer[]> {
    const response = await adminApiClient.get<Customer[]>('/api/customers/');
    return response.data;
  },

  async getById(id: number): Promise<CustomerDetails> {
    const response = await adminApiClient.get<CustomerDetails>(`/api/customers/${id}/`);
    return response.data;
  },

  async getCustomerOrders(customerId: number): Promise<CustomerOrder[]> {
    const response = await adminApiClient.get<CustomerOrder[]>(`/api/orders/?customer=${customerId}`);
    return response.data;
  },
};
