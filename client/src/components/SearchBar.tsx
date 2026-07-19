import { useState } from 'react'
import { Search, X, SlidersHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  placeholder?: string
  filters?: React.ReactNode
}

export default function SearchBar({ value, onChange, onSubmit, placeholder = 'Search facilities...', filters }: SearchBarProps) {
  const [showFilters, setShowFilters] = useState(false)

  return (
    <div className="space-y-3">
      <div className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSubmit()}
            placeholder={placeholder}
            className="input pl-10 pr-10"
          />
          {value && (
            <button
              onClick={() => { onChange(''); onSubmit() }}
              className="absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: 'var(--text-muted)' }}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        {filters && (
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn('btn-secondary', showFilters && 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400')}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filters
          </button>
        )}
      </div>
      {showFilters && filters && (
        <div className="card p-4">
          {filters}
        </div>
      )}
    </div>
  )
}
