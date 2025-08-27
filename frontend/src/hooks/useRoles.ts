import { useState, useEffect } from 'react'
import { roleApi } from './roleApi'
import { toast } from 'sonner'

interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  created_at: string
  updated_at: string
}

export const useRoles = () => {
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchRoles = async () => {
    try {
      setLoading(true)
      const response = await roleApi.listRoles()
      if (response.success) {
        setRoles(response.data?.roles || [])
      } else {
        setError(response.message || 'Failed to fetch roles')
        toast.error(response.message || 'Roller yüklenirken hata oluştu')
      }
    } catch (err) {
      setError('Failed to fetch roles')
      toast.error('Roller yüklenirken hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const createRole = async (roleData: { name: string; description?: string; permissions?: string[] }) => {
    try {
      const response = await roleApi.createRole(roleData)
      if (response.success) {
        toast.success('Rol başarıyla oluşturuldu')
        fetchRoles()
        return response
      } else {
        toast.error(response.message || 'Rol oluşturulurken hata oluştu')
        return response
      }
    } catch (err) {
      toast.error('Rol oluşturulurken hata oluştu')
      throw err
    }
  }

  const updateRole = async (roleId: string, roleData: { name?: string; description?: string; permissions?: string[] }) => {
    try {
      const response = await roleApi.updateRole(roleId, roleData)
      if (response.success) {
        toast.success('Rol başarıyla güncellendi')
        fetchRoles()
        return response
      } else {
        toast.error(response.message || 'Rol güncellenirken hata oluştu')
        return response
      }
    } catch (err) {
      toast.error('Rol güncellenirken hata oluştu')
      throw err
    }
  }

  const deleteRole = async (roleId: string) => {
    try {
      const response = await roleApi.deleteRole(roleId)
      if (response.success) {
        toast.success('Rol başarıyla silindi')
        fetchRoles()
        return response
      } else {
        toast.error(response.message || 'Rol silinirken hata oluştu')
        return response
      }
    } catch (err) {
      toast.error('Rol silinirken hata oluştu')
      throw err
    }
  }

  const assignRoleToUser = async (userId: string, roleId: string) => {
    try {
      const response = await roleApi.assignRoleToUser(userId, roleId)
      if (response.success) {
        toast.success('Rol başarıyla atandı')
        return response
      } else {
        toast.error(response.message || 'Rol atanırken hata oluştu')
        return response
      }
    } catch (err) {
      toast.error('Rol atanırken hata oluştu')
      throw err
    }
  }

  const removeRoleFromUser = async (userId: string, roleId: string) => {
    try {
      const response = await roleApi.removeRoleFromUser(userId, roleId)
      if (response.success) {
        toast.success('Rol başarıyla kaldırıldı')
        return response
      } else {
        toast.error(response.message || 'Rol kaldırılırken hata oluştu')
        return response
      }
    } catch (err) {
      toast.error('Rol kaldırılırken hata oluştu')
      throw err
    }
  }

  useEffect(() => {
    fetchRoles()
  }, [])

  return {
    roles,
    loading,
    error,
    fetchRoles,
    createRole,
    updateRole,
    deleteRole,
    assignRoleToUser,
    removeRoleFromUser
  }
}