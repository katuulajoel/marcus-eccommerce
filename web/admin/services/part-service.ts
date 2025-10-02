/**
 * Part service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface Part {
  id: number;
  name: string;
  category: number;
  category_name?: string;
  step_number: number;
  created_at: string;
  updated_at: string;
}

export interface PartCreateInput {
  name: string;
  category: number;
  step_number: number;
}

export interface PartUpdateInput {
  name?: string;
  category?: number;
  step_number?: number;
}

/**
 * Part service for admin operations
 */
export const partService = {
  /**
   * Get all parts (optionally filtered by category)
   */
  getAll: async (categoryId?: number): Promise<Part[]> => {
    const params = categoryId ? { category_id: categoryId } : {};
    const response = await adminApiClient.get<Part[]>('/api/parts/', { params });
    return response.data;
  },

  /**
   * Get single part by ID
   */
  getById: async (id: number): Promise<Part> => {
    const response = await adminApiClient.get<Part>(`/api/parts/${id}/`);
    return response.data;
  },

  /**
   * Create new part
   */
  create: async (data: PartCreateInput): Promise<Part> => {
    const response = await adminApiClient.post<Part>('/api/parts/', data);
    return response.data;
  },

  /**
   * Update existing part
   */
  update: async (id: number, data: PartUpdateInput): Promise<Part> => {
    const response = await adminApiClient.patch<Part>(`/api/parts/${id}/`, data);
    return response.data;
  },

  /**
   * Delete part
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/parts/${id}/`);
  },
};
