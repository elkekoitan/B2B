import React, { useState } from 'react'
import { useApiClient } from '../services/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export function TwoFactorPage() {
  const api = useApiClient()
  const [secret, setSecret] = useState('')
  const [otpauth, setOtpauth] = useState('')
  const [code, setCode] = useState('')
  const [msg, setMsg] = useState('')

  const setup = async () => {
    setMsg('')
    const res = await api.setup2FA()
    if ((res as any)?.success && (res as any)?.data) {
      setSecret((res as any).data.secret)
      setOtpauth((res as any).data.otpauth_url)
    }
  }

  const enable = async () => {
    setMsg('')
    try {
      const res = await api.enable2FA(code)
      setMsg(res.success ? '2FA etkin' : (res.message || 'Hata'))
    } catch (e: any) {
      setMsg(e.message || 'Hata')
    }
  }

  const disable = async () => {
    setMsg('')
    try {
      const res = await api.disable2FA()
      setMsg(res.success ? '2FA kapatıldı' : (res.message || 'Hata'))
    } catch (e: any) {
      setMsg(e.message || 'Hata')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle>İki Aşamalı Doğrulama (2FA)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button onClick={setup}>Kurulum Bilgisi Al</Button>
              <Button variant="outline" onClick={disable}>Devre Dışı Bırak</Button>
            </div>
            {secret && (
              <div className="text-sm text-gray-700">
                <div>Secret: <code>{secret}</code></div>
                <div>OTPAuth URL: <code className="break-all">{otpauth}</code></div>
              </div>
            )}
            <div className="flex gap-2 items-center">
              <Input placeholder="Doğrulama Kodu" value={code} onChange={(e) => setCode(e.target.value)} />
              <Button onClick={enable}>Etkinleştir</Button>
            </div>
            {msg && <div className="text-sm text-gray-700">{msg}</div>}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

