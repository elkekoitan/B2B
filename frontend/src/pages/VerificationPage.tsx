import React, { useState } from 'react'
import { useApiClient } from '../services/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { toast } from 'sonner'
import { Button } from '../components/ui/Button'

export function VerificationPage() {
  const api = useApiClient()
  const [files, setFiles] = useState<{ file_name: string; file_path: string; file_type: string; file_size?: number }[]>([])
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    try {
      const up = await api.uploadFile(f)
      if (up?.success && up?.data) {
        setFiles((prev) => [
          ...prev,
          { file_name: up.data.file_name, file_path: up.data.file_path, file_type: 'verification', file_size: f.size },
        ])
      }
    } catch (er: any) {
      setMsg(er.message || 'Yükleme hatası')
      toast.error(er.message || 'Yükleme hatası')
    }
  }

  const submit = async () => {
    if (files.length === 0) return setMsg('Önce dosya yükleyin')
    setLoading(true)
    try {
      const res = await api.requestVerification({ documents: files, notes: 'Company verification request' })
      if (res.success) {
        setMsg('Doğrulama talebi gönderildi')
        toast.success('Doğrulama talebi gönderildi')
      } else {
        setMsg(res.message || 'Hata')
        toast.error(res.message || 'Hata')
      }
    } catch (e: any) {
      setMsg(e.message || 'Hata')
      toast.error(e.message || 'Hata')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle>Şirket Doğrulaması</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <input type="file" onChange={onFile} />
            <ul className="text-sm text-gray-700 list-disc ml-4">
              {files.map((f) => (
                <li key={f.file_path}>{f.file_name}</li>
              ))}
            </ul>
            {msg && <div className="text-sm text-gray-700">{msg}</div>}
            <Button onClick={submit} disabled={loading}>{loading ? 'Gönderiliyor...' : 'Doğrulamayı Gönder'}</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
