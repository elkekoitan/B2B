// Role management API service
import { apiClient } from './api'

export const roleApi = {
  // List all roles
  async listRoles() {
    return apiClient.request('/roles')
  },

  // Create a new role
  async createRole(roleData: { name: string; description?: string; permissions?: string[] }) {
    return apiClient.request('/roles', {
      method: 'POST',
      body: JSON.stringify(roleData)
    })
  },

  // Update an existing role
  async updateRole(roleId: string, roleData: { name?: string; description?: string; permissions?: string[] }) {
    return apiClient.request(`/roles/${roleId}`, {
      method: 'PUT',
      body: JSON.stringify(roleData)
    })
  },

  // Delete a role
  async deleteRole(roleId: string) {
    return apiClient.request(`/roles/${roleId}`, {
      method: 'DELETE'
    })
  },

  // Assign a role to a user
  async assignRoleToUser(userId: string, roleId: string) {
    return apiClient.request(`/users/${userId}/roles`, {
      method: 'POST',
      body: JSON.stringify({ role_id: roleId })
    })
  },

  // Remove a role from a user
  async removeRoleFromUser(userId: string, roleId: string) {
    return apiClient.request(`/users/${userId}/roles/${roleId}`, {
      method: 'DELETE'
    })
  },

  // Get roles assigned to a user
  async getUserRoles(userId: string) {
    return apiClient.request(`/users/${userId}/roles`)
  }
}