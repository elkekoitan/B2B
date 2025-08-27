import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Label } from '../ui/Label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/Table'
import { Badge } from '../ui/Badge'
import { useRoles } from '../../hooks/useRoles'
import { toast } from 'sonner'

interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  created_at: string
  updated_at: string
}

export function RoleManagement() {
  const { roles, loading, error, createRole, updateRole, deleteRole } = useRoles()
  const [newRole, setNewRole] = useState({ name: '', description: '', permissions: '' })
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [editForm, setEditForm] = useState({ name: '', description: '', permissions: '' })

  const handleCreateRole = async () => {
    try {
      const permissions = newRole.permissions.split(',').map(p => p.trim()).filter(p => p)
      await createRole({
        name: newRole.name,
        description: newRole.description,
        permissions: permissions
      })
      setNewRole({ name: '', description: '', permissions: '' })
    } catch (error) {
      console.error('Failed to create role:', error)
    }
  }

  const handleUpdateRole = async () => {
    if (!editingRole) return

    try {
      const permissions = editForm.permissions.split(',').map(p => p.trim()).filter(p => p)
      await updateRole(editingRole.id, {
        name: editForm.name,
        description: editForm.description,
        permissions: permissions
      })
      setEditingRole(null)
    } catch (error) {
      console.error('Failed to update role:', error)
    }
  }

  const handleDeleteRole = async (roleId: string) => {
    try {
      await deleteRole(roleId)
    } catch (error) {
      console.error('Failed to delete role:', error)
    }
  }

  const startEditing = (role: Role) => {
    setEditingRole(role)
    setEditForm({
      name: role.name,
      description: role.description,
      permissions: role.permissions?.join(', ') || ''
    })
  }

  if (loading) {
    return <div className="p-4">Loading roles...</div>
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rol Yönetimi</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Create Role Form */}
          <div className="border-b pb-6">
            <h3 className="text-lg font-medium mb-4">Yeni Rol Oluştur</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="role-name">Rol Adı</Label>
                <Input
                  id="role-name"
                  placeholder="Rol adı"
                  value={newRole.name}
                  onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="role-description">Açıklama</Label>
                <Input
                  id="role-description"
                  placeholder="Rol açıklaması"
                  value={newRole.description}
                  onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
                />
              </div>
            </div>
            <div className="mt-4">
              <Label htmlFor="role-permissions">İzinler</Label>
              <Input
                id="role-permissions"
                placeholder="İzinler (virgülle ayırın: rfq:create,rfq:read)"
                value={newRole.permissions}
                onChange={(e) => setNewRole({ ...newRole, permissions: e.target.value })}
              />
              <p className="text-sm text-gray-500 mt-1">
                Örnek izinler: rfq:create, rfq:read, supplier:manage
              </p>
            </div>
            <Button className="mt-4" onClick={handleCreateRole}>
              Rol Oluştur
            </Button>
          </div>

          {/* Roles List */}
          <div>
            <h3 className="text-lg font-medium mb-4">Mevcut Roller</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Rol Adı</TableHead>
                  <TableHead>Açıklama</TableHead>
                  <TableHead>İzinler</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {roles.map((role) => (
                  <TableRow key={role.id}>
                    {editingRole?.id === role.id ? (
                      <>
                        <TableCell>
                          <Input
                            value={editForm.name}
                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            value={editForm.description}
                            onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            value={editForm.permissions}
                            onChange={(e) => setEditForm({ ...editForm, permissions: e.target.value })}
                          />
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button size="sm" onClick={handleUpdateRole}>
                            Kaydet
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setEditingRole(null)}
                          >
                            İptal
                          </Button>
                        </TableCell>
                      </>
                    ) : (
                      <>
                        <TableCell className="font-medium">{role.name}</TableCell>
                        <TableCell>{role.description}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {role.permissions?.slice(0, 3).map((permission, idx) => (
                              <Badge key={idx} variant="secondary">
                                {permission}
                              </Badge>
                            ))}
                            {role.permissions && role.permissions.length > 3 && (
                              <Badge variant="outline">
                                +{role.permissions.length - 3}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => startEditing(role)}
                          >
                            Düzenle
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteRole(role.id)}
                          >
                            Sil
                          </Button>
                        </TableCell>
                      </>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}