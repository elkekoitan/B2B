import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table'
import { Badge } from '../components/ui/Badge'
import { RoleManagement } from '../components/admin/RoleManagement'
import { toast } from 'sonner'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  company_name: string
}

export function AdminPage() {
  const { hasPermission } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [newRole, setNewRole] = useState({ name: '', description: '', permissions: '' })
  const [selectedUser, setSelectedUser] = useState<{ userId: string; roleId: string } | null>(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      // This would be replaced with actual API call to fetch users
      // For now, we'll mock the data
      const mockUsers: User[] = [
        {
          id: '1',
          email: 'admin@example.com',
          full_name: 'Admin User',
          role: 'admin',
          company_name: 'Agentik'
        },
        {
          id: '2',
          email: 'buyer@example.com',
          full_name: 'Buyer User',
          role: 'buyer',
          company_name: 'Construction Co'
        },
        {
          id: '3',
          email: 'supplier@example.com',
          full_name: 'Supplier User',
          role: 'supplier',
          company_name: 'Chemical Supplier'
        }
      ]
      setUsers(mockUsers)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch users:', error)
      toast.error('Kullanıcılar yüklenirken hata oluştu')
      setLoading(false)
    }
  }

  if (!hasPermission('user', 'manage')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardContent className="text-center py-8">
            <div className="text-red-500 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Erişim Reddedildi</h3>
            <p className="text-gray-500">Bu sayfaya erişim izniniz bulunmamaktadır.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Yönetim Paneli</h1>
          <p className="mt-2 text-gray-600">Sistem yönetimi ve kullanıcı rolleri</p>
        </div>

        <div className="grid grid-cols-1 gap-8">
          {/* Role Management */}
          <RoleManagement />

          {/* Users Management */}
          <Card>
            <CardHeader>
              <CardTitle>Kullanıcılar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Kullanıcı Listesi</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kullanıcı</TableHead>
                      <TableHead>E-posta</TableHead>
                      <TableHead>Rol</TableHead>
                      <TableHead>Şirket</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell className="font-medium">{user.full_name}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          <Badge variant={
                            user.role === 'admin' ? 'destructive' :
                            user.role === 'buyer' ? 'default' :
                            user.role === 'supplier' ? 'secondary' : 'outline'
                          }>
                            {user.role}
                          </Badge>
                        </TableCell>
                        <TableCell>{user.company_name}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}