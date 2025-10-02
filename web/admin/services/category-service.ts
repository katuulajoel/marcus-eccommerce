/**
 * Category service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface Category {
  id: number;
  name: string;
  description: string;
  image_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreateInput {
  name: string;
  description: string;
  image_url?: string;
  is_active?: boolean;
}

export interface CategoryUpdateInput {
  name?: string;
  description?: string;
  image_url?: string;
  is_active?: boolean;
}

/**
 * Category service for admin operations
 */
export const categoryService = {
  /**
   * Get all categories
   */
  getAll: async (): Promise<Category[]> => {
    const response = await adminApiClient.get<Category[]>('/api/categories/');
    return response.data;
  },

  /**
   * Get single category by ID
   */
  getById: async (id: number): Promise<Category> => {
    const response = await adminApiClient.get<Category>(`/api/categories/${id}/`);
    return response.data;
  },

  /**
   * Create new category
   */
  create: async (data: CategoryCreateInput): Promise<Category> => {
    const response = await adminApiClient.post<Category>('/api/categories/', data);
    return response.data;
  },

  /**
   * Update existing category
   */
  update: async (id: number, data: CategoryUpdateInput): Promise<Category> => {
    const response = await adminApiClient.patch<Category>(`/api/categories/${id}/`, data);
    return response.data;
  },

  /**
   * Delete category
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/categories/${id}/`);
  },
};
