/**
 * Incompatibility Rule service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface IncompatibilityRule {
  id: number;
  option_a: number;
  option_a_name?: string;
  option_b: number;
  option_b_name?: string;
  incompatibility_message?: string;
  created_at: string;
  updated_at: string;
}

export interface IncompatibilityRuleCreateInput {
  option_a: number;
  option_b: number;
  incompatibility_message?: string;
}

export interface IncompatibilityRuleUpdateInput {
  option_a?: number;
  option_b?: number;
  incompatibility_message?: string;
}

/**
 * Incompatibility Rule service for admin operations
 */
export const incompatibilityService = {
  /**
   * Get all incompatibility rules
   */
  getAll: async (): Promise<IncompatibilityRule[]> => {
    const response = await adminApiClient.get<IncompatibilityRule[]>('/api/configurator/incompatibilities/');
    return response.data;
  },

  /**
   * Get single incompatibility rule by ID
   */
  getById: async (id: number): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.get<IncompatibilityRule>(`/api/configurator/incompatibilities/${id}/`);
    return response.data;
  },

  /**
   * Create new incompatibility rule
   */
  create: async (data: IncompatibilityRuleCreateInput): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.post<IncompatibilityRule>('/api/configurator/incompatibilities/', data);
    return response.data;
  },

  /**
   * Update existing incompatibility rule
   */
  update: async (id: number, data: IncompatibilityRuleUpdateInput): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.patch<IncompatibilityRule>(`/api/configurator/incompatibilities/${id}/`, data);
    return response.data;
  },

  /**
   * Delete incompatibility rule
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/configurator/incompatibilities/${id}/`);
  },
};
