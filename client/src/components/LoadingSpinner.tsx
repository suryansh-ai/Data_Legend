export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
      <p className="mt-3 text-sm" style={{ color: 'var(--text-muted)' }}>{text}</p>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-4 w-3/4 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }} />
      <div className="mt-2 h-3 w-1/2 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }} />
      <div className="mt-4 h-3 w-full rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }} />
      <div className="mt-1 h-3 w-2/3 rounded" style={{ backgroundColor: 'var(--bg-tertiary)' }} />
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {Array.from({ length: cols }).map((_, j) => (
            <div
              key={j}
              className="h-4 animate-pulse rounded"
              style={{
                backgroundColor: 'var(--bg-tertiary)',
                width: `${Math.random() * 40 + 30}%`,
              }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
