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
  image?: File;
  is_active?: boolean;
}

export interface CategoryUpdateInput {
  name?: string;
  description?: string;
  image?: File | null;
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
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('description', data.description);
    if (data.image) {
      formData.append('image', data.image);
    }
    if (data.is_active !== undefined) {
      formData.append('is_active', String(data.is_active));
    }

    const response = await adminApiClient.post<Category>('/api/categories/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Update existing category
   */
  update: async (id: number, data: CategoryUpdateInput): Promise<Category> => {
    const formData = new FormData();
    if (data.name !== undefined) {
      formData.append('name', data.name);
    }
    if (data.description !== undefined) {
      formData.append('description', data.description);
    }
    if (data.image !== undefined) {
      if (data.image === null) {
        // Clear the image
        formData.append('image', '');
      } else {
        formData.append('image', data.image);
      }
    }
    if (data.is_active !== undefined) {
      formData.append('is_active', String(data.is_active));
    }

    const response = await adminApiClient.patch<Category>(`/api/categories/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Delete category
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/categories/${id}/`);
  },
};
