import React, { useEffect, useState } from 'react'
import { useApiClient } from '../services/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { toast } from 'sonner'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts'

export function JobsPage() {
  const api = useApiClient()
  const [jobType, setJobType] = useState('supplier_discovery')
  const [rfqId, setRfqId] = useState('')
  const [jobId, setJobId] = useState('')
  const [status, setStatus] = useState<any>(null)
  const [recent, setRecent] = useState<any[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [polling, setPolling] = useState(false)
  const [view, setView] = useState<'recent' | 'history'>('recent')
  const [detail, setDetail] = useState<any | null>(null)
  const [trend, setTrend] = useState<{ days: string[]; series: Record<string, number[]> } | null>(null)
  const [trendDays, setTrendDays] = useState(7)

  const startJob = async () => {
    try {
      const res = await api.orchestrateJob({ job_type: jobType, rfq_id: rfqId || undefined })
      if ((res as any).success && (res as any).data?.job_id) {
        setJobId((res as any).data.job_id)
        toast.success('Job kuyruğa eklendi')
      } else {
        toast.error((res as any).message || 'Başlatılamadı')
      }
    } catch (e: any) {
      toast.error(e.message || 'Hata')
    }
  }

  const checkStatus = async () => {
    if (!jobId) return
    try {
      const res = await api.getOrchestrateStatus(jobId)
      if ((res as any).success) {
        setStatus((res as any).data?.job || null)
      } else {
        toast.error((res as any).message || 'Durum alınamadı')
      }
    } catch (e: any) {
      toast.error(e.message || 'Hata')
    }
  }

  const loadRecent = async () => {
    try {
      const res = await api.getRecentJobs({ limit: 10, job_type: jobType || undefined })
      if ((res as any).success) {
        setRecent(((res as any).data?.jobs || []) as any[])
      }
    } catch (e) {
      // ignore
    }
  }

  const loadHistory = async () => {
    try {
      const res = await api.getJobHistory({ limit: 20, job_type: jobType || undefined })
      if ((res as any).success) {
        setHistory(((res as any).data?.jobs || []) as any[])
      }
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => {
    let t: any
    if (polling && jobId) {
      const loop = async () => {
        await checkStatus()
        t = setTimeout(loop, 2000)
      }
      loop()
    }
    return () => t && clearTimeout(t)
  }, [polling, jobId])

  useEffect(() => {
    if (view === 'recent') loadRecent()
    else loadHistory()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, jobType])

  const loadTrend = async (days: number) => {
    try {
      const res: any = await api.getJobsAnalytics(days)
      if (res?.success) setTrend({ days: res.data.days, series: res.data.series })
    } catch {}
  }

  useEffect(() => {
    loadTrend(trendDays)
  }, [trendDays])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 space-y-6">
        <Card>
          {trend && (
            <CardContent className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium">Jobs Trend ({trendDays} gün)</div>
                <div className="inline-flex border rounded overflow-hidden">
                  <button className={`px-3 py-1 text-sm ${trendDays===7?'bg-gray-200':''}`} onClick={() => setTrendDays(7)}>7g</button>
                  <button className={`px-3 py-1 text-sm ${trendDays===30?'bg-gray-200':''}`} onClick={() => setTrendDays(30)}>30g</button>
                </div>
              </div>
              <div style={{ width: '100%', height: 220 }}>
                <ResponsiveContainer>
                  <LineChart data={trend.days.map((d, i) => ({
                    day: d.slice(5),
                    queued: trend.series.queued[i] || 0,
                    in_progress: trend.series.in_progress[i] || 0,
                    completed: trend.series.completed[i] || 0,
                    failed: trend.series.failed[i] || 0,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="queued" stroke="#8884d8" dot={false} />
                    <Line type="monotone" dataKey="in_progress" stroke="#ffbf00" dot={false} />
                    <Line type="monotone" dataKey="completed" stroke="#22c55e" dot={false} />
                    <Line type="monotone" dataKey="failed" stroke="#ef4444" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          )}
          <CardHeader>
            <CardTitle>Orchestrate Job</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid md:grid-cols-3 gap-2">
              <select className="border rounded px-3 py-2" value={jobType} onChange={e => setJobType(e.target.value)}>
                <option value="supplier_discovery">supplier_discovery</option>
                <option value="email_campaign">email_campaign</option>
                <option value="rfq_process">rfq_process</option>
              </select>
              <Input placeholder="RFQ ID (opsiyonel)" value={rfqId} onChange={e => setRfqId(e.target.value)} />
              <Button onClick={startJob}>Başlat</Button>
            </div>
            {jobId && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Job ID: {jobId}</span>
                <Button variant="outline" onClick={checkStatus}>Durumu Getir</Button>
                <Button variant={polling ? 'destructive' : 'outline'} onClick={() => setPolling(p => !p)}>
                  {polling ? 'Durdur' : 'Oto-Poll'}
                </Button>
              </div>
            )}
            {status && (
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">{JSON.stringify(status, null, 2)}</pre>
            )}
            <div className="pt-4 border-t">
              <div className="flex items-center gap-2 mb-2">
                <div className="inline-flex border rounded overflow-hidden">
                  <button className={`px-3 py-1 text-sm ${view==='recent'?'bg-gray-200':''}`} onClick={() => setView('recent')}>Recent</button>
                  <button className={`px-3 py-1 text-sm ${view==='history'?'bg-gray-200':''}`} onClick={() => setView('history')}>History</button>
                </div>
                <Button variant="outline" onClick={view==='recent'?loadRecent:loadHistory}>Yenile</Button>
                <span className="text-xs text-gray-500">(filtre: {jobType})</span>
              </div>
              {(view==='recent' ? recent : history).length > 0 && (
                <table className="text-xs w-full table-auto border">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="text-left p-2">Job</th>
                      <th className="text-left p-2">Type</th>
                      <th className="text-left p-2">Status</th>
                      <th className="text-left p-2">Updated</th>
                      <th className="text-left p-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(view==='recent' ? recent : history).map((j: any) => {
                      const id = j.job_id || j.id
                      return (
                        <tr key={id} className="border-t">
                          <td className="p-2">
                            <button
                              className="font-mono text-indigo-600 hover:underline"
                              onClick={async () => {
                                setJobId(id); setStatus(null); setPolling(false);
                                await checkStatus(); setDetail(status)
                              }}
                              title="Durumu getir"
                            >
                              {String(id).slice(-8)}
                            </button>
                          </td>
                          <td className="p-2">{j.job_type || '-'}</td>
                          <td className="p-2">{j.status}</td>
                          <td className="p-2">{j.updated_at || '-'}</td>
                          <td className="p-2">
                            <Button
                              variant="outline"
                              disabled={j.status !== 'queued'}
                              onClick={async () => {
                                try {
                                  const res = await api.cancelJob(id)
                                  if ((res as any).success) {
                                    toast.success('İş iptal edildi')
                                    view==='recent' ? loadRecent() : loadHistory()
                                  } else {
                                    toast.error((res as any).message || 'İptal edilemedi')
                                  }
                                } catch (e: any) {
                                  toast.error(e.message || 'Hata')
                                }
                              }}
                            >
                              İptal
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              )}
              {detail && (
                <div className="mt-3 border rounded p-3 bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">Detay</div>
                    <Button variant="outline" onClick={() => setDetail(null)}>Kapat</Button>
                  </div>
                  <pre className="text-xs overflow-auto">{JSON.stringify(detail, null, 2)}</pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
