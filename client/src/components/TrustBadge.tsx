import { memo } from 'react'
import { cn, trustBadgeClass, trustLabel, trustScoreColor } from '@/lib/utils'

interface TrustBadgeProps {
  score: number | null
  signal: string | null
  size?: 'sm' | 'md' | 'lg'
  showScore?: boolean
}

const TrustBadge = memo(function TrustBadge({ score, signal, size = 'md', showScore = true }: TrustBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  }

  return (
    <div className="flex items-center gap-2">
      {showScore && score != null && (
        <span
          className="font-mono text-sm font-semibold"
          style={{ color: trustScoreColor(score) }}
        >
          {score.toFixed(0)}
        </span>
      )}
      <span className={cn('badge', trustBadgeClass(signal), sizeClasses[size])}>
        {trustLabel(signal)}
      </span>
    </div>
  )
})

export default TrustBadge