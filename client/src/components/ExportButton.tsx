import { Download, FileText, Table } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface ExportButtonProps {
  data: Record<string, unknown>[]
  filename: string
}

export default function ExportButton({ data, filename }: ExportButtonProps) {
  const [open, setOpen] = useState(false)

  const exportCSV = () => {
    if (!data.length) return
    const headers = Object.keys(data[0])
    const csv = [
      headers.join(','),
      ...data.map(row => headers.map(h => `"${String(row[h] ?? '').replace(/"/g, '""')}"`).join(','))
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.csv`
    a.click()
    URL.revokeObjectURL(url)
    setOpen(false)
  }

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.json`
    a.click()
    URL.revokeObjectURL(url)
    setOpen(false)
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="btn-secondary">
        <Download className="h-4 w-4" />
        Export
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div
            className="absolute right-0 top-full z-20 mt-1 w-40 rounded-lg border py-1 shadow-lg"
            style={{
              backgroundColor: 'var(--bg-primary)',
              borderColor: 'var(--border-color)',
            }}
          >
            <button onClick={exportCSV} className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-brand-50 dark:hover:bg-slate-800/50" style={{ color: 'var(--text-primary)' }}>
              <Table className="h-4 w-4" />
              Export CSV
            </button>
            <button onClick={exportJSON} className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-brand-50 dark:hover:bg-slate-800/50" style={{ color: 'var(--text-primary)' }}>
              <FileText className="h-4 w-4" />
              Export JSON
            </button>
          </div>
        </>
      )}
    </div>
  )
}
