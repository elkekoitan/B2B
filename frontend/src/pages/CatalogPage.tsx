import React, { useEffect, useState } from 'react'
import { useApiClient } from '../services/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { toast } from 'sonner'

export function CatalogPage() {
  const api = useApiClient()
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterCurrency, setFilterCurrency] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<{ product_name?: string; category?: string; price?: string; currency?: string }>({})

  const [form, setForm] = useState({ product_name: '', category: '', price: '', currency: 'USD' })

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.getMyCatalog({
        page,
        size,
        search: search.trim() || undefined,
        category: filterCategory.trim() || undefined,
        currency: filterCurrency.trim() || undefined,
      })
      if (res.success && (res.data as any)?.data !== undefined) {
        setItems((res.data as any).data || [])
        setTotal((res.data as any).total || 0)
      }
    } catch (e: any) {
      setMsg(e.message || 'Hata')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [page, size])

  const create = async () => {
    setMsg('')
    try {
      const payload = {
        product_name: form.product_name,
        category: form.category || null,
        price: form.price ? Number(form.price) : null,
        currency: form.currency || 'USD',
        supplier_id: items[0]?.supplier_id || undefined, // if state carries supplier, else backend will validate
      }
      const res = await api.createCatalogItem(payload)
      if (res.success) {
        setMsg('Eklendi')
        toast.success('Katalog ürünü eklendi')
      } else {
        setMsg(res.message || 'Hata')
        toast.error(res.message || 'Hata')
      }
      await load()
    } catch (e: any) {
      setMsg(e.message || 'Hata')
      toast.error(e.message || 'Hata')
    }
  }

  const remove = async (id: string) => {
    try {
      const r = await api.deleteCatalogItem(id)
      if (r.success) toast.success('Silindi')
      else toast.error(r.message || 'Hata')
      await load()
    } catch (e: any) {
      toast.error(e.message || 'Hata')
    }
  }

  const startEdit = (it: any) => {
    setEditingId(it.id)
    setEditForm({ product_name: it.product_name, category: it.category, price: String(it.price ?? ''), currency: it.currency })
  }

  const saveEdit = async () => {
    if (!editingId) return
    try {
      const updates: any = {}
      if (editForm.product_name !== undefined) updates.product_name = editForm.product_name
      if (editForm.category !== undefined) updates.category = editForm.category
      if (editForm.price !== undefined) updates.price = editForm.price ? Number(editForm.price) : null
      if (editForm.currency !== undefined) updates.currency = (editForm.currency || 'USD').toUpperCase()
      const r = await api.updateCatalogItem(editingId, updates)
      if (r.success) toast.success('Güncellendi')
      else toast.error(r.message || 'Hata')
      setEditingId(null)
      await load()
    } catch (e: any) {
      toast.error(e.message || 'Hata')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Katalog Ekle</CardTitle>
          </CardHeader>
          <CardContent className="grid md:grid-cols-4 gap-2">
            <Input placeholder="Ürün Adı" value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} />
            <Input placeholder="Kategori" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
            <Input placeholder="Fiyat" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
            <Input placeholder="Para Birimi" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })} />
            <div className="col-span-full"><Button onClick={create}>Ekle</Button></div>
            {msg && <div className="text-sm text-gray-700 col-span-full">{msg}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Katalog</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-5 gap-2 mb-3">
              <Input className="md:col-span-2" placeholder="Ara" value={search} onChange={(e) => setSearch(e.target.value)} />
              <Input placeholder="Kategori" value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} />
              <Input placeholder="Para Birimi (USD/EUR/TRY)" value={filterCurrency} onChange={(e) => setFilterCurrency(e.target.value.toUpperCase())} />
              <Button variant="outline" onClick={() => { setPage(1); load() }}>Uygula</Button>
            </div>
            {loading ? 'Yükleniyor...' : (
              <ul className="divide-y">
                {items.map((it) => (
                  <li key={it.id} className="py-2 flex justify-between items-center">
                    <div className="flex-1 mr-2">
                      {editingId === it.id ? (
                        <div className="grid md:grid-cols-4 gap-2">
                          <Input value={editForm.product_name || ''} onChange={(e) => setEditForm({ ...editForm, product_name: e.target.value })} />
                          <Input value={editForm.category || ''} onChange={(e) => setEditForm({ ...editForm, category: e.target.value })} />
                          <Input value={editForm.price || ''} onChange={(e) => setEditForm({ ...editForm, price: e.target.value })} />
                          <Input value={editForm.currency || ''} onChange={(e) => setEditForm({ ...editForm, currency: e.target.value.toUpperCase() })} />
                        </div>
                      ) : (
                        <>
                          <div className="font-medium">{it.product_name}</div>
                          <div className="text-sm text-gray-600">{it.category} • {it.price} {it.currency}</div>
                        </>
                      )}
                    </div>
                    {editingId === it.id ? (
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setEditingId(null)}>Vazgeç</Button>
                        <Button onClick={saveEdit}>Kaydet</Button>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => startEdit(it)}>Düzenle</Button>
                        <Button variant="outline" onClick={() => remove(it.id)}>Sil</Button>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">Toplam: {total}</div>
              <div className="flex items-center gap-2">
                <Button variant="outline" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Önceki</Button>
                <span className="text-sm">Sayfa {page}</span>
                <Button variant="outline" disabled={page * size >= total} onClick={() => setPage((p) => p + 1)}>Sonraki</Button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Sayfa Boyutu</span>
                <Input style={{width: '80px'}} value={String(size)} onChange={(e) => setSize(Math.max(1, Number(e.target.value) || 10))} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
