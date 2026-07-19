import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldCheck, MapPin, Database, Activity, TrendingUp, AlertTriangle, Building2, Users } from 'lucide-react'
import { api } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { FacilityStats, CoverageGap } from '@/lib/types'

const tracks = [
  {
    to: '/trust-desk',
    icon: ShieldCheck,
    title: 'Trust Desk',
    description: 'Score and verify facility capability claims against evidence',
    color: 'bg-emerald-500',
  },
  {
    to: '/medical-desert',
    icon: MapPin,
    title: 'Medical Desert',
    description: 'Identify underserved regions and coverage gaps',
    color: 'bg-amber-500',
  },
  {
    to: '/data-readiness',
    icon: Database,
    title: 'Data Readiness',
    description: 'Audit data quality and completeness across all fields',
    color: 'bg-violet-500',
  },
]

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.4 },
  }),
}

export default function Home() {
  const [stats, setStats] = useState<FacilityStats | null>(null)
  const [stateStats, setStateStats] = useState<CoverageGap[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getStateStats()])
      .then(([s, ss]) => { setStats(s); setStateStats(ss) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  const topStates = stateStats.slice(0, 5)
  const lowTrustStates = stateStats.filter(s => s.avg_trust < 30).slice(0, 5)

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div>
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Data Legend
        </h1>
        <p className="mt-2 text-lg" style={{ color: 'var(--text-secondary)' }}>
          Healthcare Facility Intelligence Platform for India
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: 'Total Facilities', value: formatNumber(stats?.total ?? 0), icon: Building2 },
          { label: 'States Covered', value: formatNumber(stats?.states ?? 0), icon: MapPin },
          { label: 'With Descriptions', value: formatNumber(stats?.with_description ?? 0), icon: Activity },
          { label: 'With Capabilities', value: formatNumber(stats?.with_capability ?? 0), icon: ShieldCheck },
        ].map(({ label, value, icon: Icon }, i) => (
          <motion.div
            key={label}
            custom={i}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            className="card"
          >
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-brand-50 p-2 dark:bg-brand-900/30">
                <Icon className="h-5 w-5 text-brand-600 dark:text-brand-400" />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Track Cards */}
      <div>
        <h2 className="mb-4 text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
          Intelligence Tracks
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {tracks.map(({ to, icon: Icon, title, description, color }, i) => (
            <motion.div
              key={to}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate="visible"
            >
              <Link to={to} className="card group block">
                <div className={`mb-3 inline-flex rounded-lg p-2 ${color}`}>
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-semibold group-hover:text-brand-600 dark:group-hover:text-brand-400" style={{ color: 'var(--text-primary)' }}>
                  {title}
                </h3>
                <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>{description}</p>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Coverage Tables */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-3 font-semibold" style={{ color: 'var(--text-primary)' }}>
            Top States by Facility Count
          </h3>
          <div className="space-y-2">
            {topStates.map(s => (
              <div key={s.state} className="flex items-center justify-between text-sm">
                <span style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                <div className="flex items-center gap-3">
                  <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{s.total}</span>
                  <span className="text-xs" style={{ color: s.avg_trust >= 50 ? '#10b981' : s.avg_trust >= 30 ? '#f59e0b' : '#ef4444' }}>
                    {s.avg_trust.toFixed(0)} avg
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="mb-3 flex items-center gap-2 font-semibold" style={{ color: 'var(--text-primary)' }}>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            Low Trust States
          </h3>
          <div className="space-y-2">
            {lowTrustStates.length === 0 ? (
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>All states have adequate trust scores</p>
            ) : (
              lowTrustStates.map(s => (
                <div key={s.state} className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-red-500">{s.avg_trust.toFixed(0)}</span>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{s.low_trust_count} low</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
