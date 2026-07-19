import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(n: number | null | undefined): string {
  if (n == null) return '—'
  return n.toLocaleString('en-IN')
}

export function formatPercent(n: number | null | undefined): string {
  if (n == null) return '—'
  return `${(n * 100).toFixed(1)}%`
}

export function truncate(str: string, len: number): string {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

export function trustColor(signal: string | null | undefined): string {
  switch (signal) {
    case 'CORROBORATED': return 'text-trust-high'
    case 'CLAIMED_ONLY': return 'text-trust-medium'
    case 'WEAK': return 'text-trust-low'
    default: return 'text-trust-unknown'
  }
}

export function trustBadgeClass(signal: string | null | undefined): string {
  switch (signal) {
    case 'CORROBORATED': return 'badge-trust-high'
    case 'CLAIMED_ONLY': return 'badge-trust-medium'
    case 'WEAK': return 'badge-trust-low'
    default: return 'badge-trust-unknown'
  }
}

export function trustLabel(signal: string | null | undefined): string {
  switch (signal) {
    case 'CORROBORATED': return 'Corroborated'
    case 'CLAIMED_ONLY': return 'Claimed Only'
    case 'WEAK': return 'Weak'
    case 'UNKNOWN': return 'Unknown'
    default: return 'N/A'
  }
}

export function trustScoreColor(score: number): string {
  if (score >= 70) return '#10b981'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}
