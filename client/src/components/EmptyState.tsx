import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description: string
  action?: ReactNode
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && (
        <div className="mb-4 rounded-full p-4" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{title}</h3>
      <p className="mt-1 max-w-sm text-sm" style={{ color: 'var(--text-muted)' }}>{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
