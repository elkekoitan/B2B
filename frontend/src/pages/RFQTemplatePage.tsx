import React, { useEffect, useState } from 'react'
import { useApiClient } from '../services/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Textarea } from '../components/ui/Textarea'
import { toast } from 'sonner'

interface TemplateField {
  name: string
  label: string
  type: string
  required?: boolean
}

export function RFQTemplatePage() {
  const api = useApiClient()
  const [templates, setTemplates] = useState<{ category: string; title: string }[]>([])
  const [category, setCategory] = useState('')
  const [fields, setFields] = useState<TemplateField[]>([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

  // Basic RFQ inputs
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [quantity, setQuantity] = useState<number | ''>('')
  const [unit, setUnit] = useState('kg')
  const [currency, setCurrency] = useState('USD')

  // Template extra fields state
  const [extra, setExtra] = useState<Record<string, any>>({})

  useEffect(() => {
    (async () => {
      try {
        const res = await api.listRFQTemplates()
        if (res.success && res.data) setTemplates(res.data)
      } catch (e: any) {
        console.error(e)
      }
    })()
  }, [])

  const loadTemplate = async (cat: string) => {
    setCategory(cat)
    setExtra({})
    try {
      const res = await api.getRFQTemplate(cat)
      if (res && (res as any).category) {
        setFields((res as any).fields || [])
      }
    } catch (e: any) {
      console.error(e)
    }
  }

  const submit = async () => {
    if (!category) return setMsg('Kategori seçin')
    if (!title || !description) return setMsg('Başlık ve açıklama zorunlu')
    // validate required fields
    const missing = fields.filter((f) => f.required && !String(extra[f.name] ?? '').trim())
    if (missing.length > 0) {
      setMsg(`Eksik alanlar: ${missing.map((m) => m.label).join(', ')}`)
      toast.error('Zorunlu alanlar eksik')
      return
    }
    setLoading(true)
    setMsg('')
    try {
      const payload = {
        title,
        description,
        category,
        quantity: quantity === '' ? undefined : Number(quantity),
        unit,
        currency,
        extra_fields: extra,
      }
      const res = await api.createRFQWithTemplate(payload)
      if (res.success) {
        setMsg('RFQ oluşturuldu')
        toast.success('RFQ oluşturuldu')
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
      <div className="max-w-5xl mx-auto px-4 grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Şablon Seç</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {templates.map((t) => (
                <Button key={t.category} variant={category === t.category ? 'default' : 'outline'} onClick={() => loadTemplate(t.category)}>
                  {t.title} ({t.category})
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>RFQ Bilgileri</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input placeholder="Başlık" value={title} onChange={(e) => setTitle(e.target.value)} />
            <Textarea rows={4} placeholder="Açıklama" value={description} onChange={(e) => setDescription(e.target.value)} />
            <div className="grid grid-cols-3 gap-2">
              <Input placeholder="Miktar" type="number" value={quantity} onChange={(e) => setQuantity(e.target.value === '' ? '' : Number(e.target.value))} />
              <Input placeholder="Birim" value={unit} onChange={(e) => setUnit(e.target.value)} />
              <Input placeholder="Para Birimi" value={currency} onChange={(e) => setCurrency(e.target.value.toUpperCase())} />
            </div>
            <hr />
            <div className="space-y-2">
              {fields.map((f) => (
                <div key={f.name}>
                  <label className="text-sm text-gray-600">{f.label} {f.required ? '*' : ''}</label>
                  <Input
                    placeholder={f.label}
                    value={extra[f.name] ?? ''}
                    onChange={(e) => setExtra((prev) => ({ ...prev, [f.name]: e.target.value }))}
                  />
                </div>
              ))}
            </div>
            {msg && <div className="text-sm text-gray-700">{msg}</div>}
            <Button onClick={submit} disabled={loading}>{loading ? 'Gönderiliyor...' : 'RFQ Oluştur'}</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
