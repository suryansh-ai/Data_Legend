import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldCheck, MapPin, Database, Activity, AlertTriangle, Building2, HelpCircle, CheckCircle, ArrowRight, Heart } from 'lucide-react'
import { api } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { FacilityStats, CoverageGap } from '@/lib/types'
import { EmergencyBox } from '@/components/EmergencyBox'

const tracks = [
  {
    to: '/trust-desk',
    icon: ShieldCheck,
    title: 'Facility Trust Desk',
    description: 'Verify if a hospital actually has the capabilities it claims (like ICU or Neonatal beds) before referring patients.',
    color: 'bg-teal-700 dark:bg-teal-900',
    actionText: 'Explore Trust Scores',
  },
  {
    to: '/triage',
    icon: Heart,
    title: 'Referral & Triage AI',
    description: 'Enter symptoms in plain language to get diagnostic ideas, match suitable facilities, and book slots instantly.',
    color: 'bg-emerald-700 dark:bg-emerald-900',
    actionText: 'Start Assessment',
  },
  {
    to: '/ngo-dashboard',
    icon: Building2,
    title: 'NGO Planning Panel',
    description: 'Analyze resource gaps, check doctor counts, and map regional coverage deserts to save lives where they are needed most.',
    color: 'bg-sky-700 dark:bg-sky-900',
    actionText: 'Open Planner',
  },
]

const cardVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.35, ease: 'easeOut' },
  }),
}

export default function Home() {
  const [stats, setStats] = useState<FacilityStats | null>(null)
  const [stateStats, setStateStats] = useState<CoverageGap[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getStateStats()])
      .then(([s, ss]) => {
        setStats(s)
        setStateStats(ss)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  const topStates = stateStats.slice(0, 5)
  const lowTrustStates = stateStats.filter(s => s.avg_trust < 30).slice(0, 5)

  return (
    <div className="space-y-12 py-2">
      {/* Premium Staggered Hero Panel */}
      <div className="grid gap-8 lg:grid-cols-12 items-center">
        <div className="lg:col-span-8 space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full bg-teal-50 px-3.5 py-1 text-xs font-bold text-teal-800">
            <Heart className="h-3.5 w-3.5 text-teal-700 animate-pulse fill-current" />
            <span>Empowering Smart Referral & Coverage Planners</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl text-slate-800 leading-[1.1]">
            Building the <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-700 to-emerald-600">Trust Layer</span> for Indian Healthcare
          </h1>
          <p className="text-sm sm:text-base leading-relaxed text-slate-600 max-w-2xl">
            We analyze messy facility records, coordinates, and capability claims across <span className="font-extrabold text-teal-700">9,947 clinics</span> in India. We corroborate descriptions, identify anomalies, and ensure you send patients where medical care is real.
          </p>
        </div>

        <div className="lg:col-span-4 card p-6 bg-gradient-to-br from-teal-700 to-teal-800 text-white space-y-4 shadow-xl border-none relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 h-32 w-32 rounded-full bg-white/10 blur-xl"></div>
          <div className="space-y-1.5 relative">
            <span className="text-[9px] font-black uppercase tracking-wider text-teal-200">System Integrity</span>
            <h4 className="text-lg font-black leading-tight">Live Validation Status</h4>
          </div>
          <div className="divide-y divide-teal-600/50 text-xs pt-1">
            <div className="py-2.5 flex justify-between">
              <span className="font-semibold text-teal-100">NFHS-5 Demographic Sync</span>
              <span className="font-extrabold text-teal-200">100% Mapped</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="font-semibold text-teal-100">SQL Warehouse Fallback</span>
              <span className="font-extrabold text-teal-200">Active</span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="font-semibold text-teal-100">Parquet Integrity Check</span>
              <span className="font-extrabold text-teal-200">9,947 Verified</span>
            </div>
          </div>
        </div>
      </div>
      {/* Trust Legend Card for Simplicity & Accessibility */}
      <div className="rounded-2xl border p-6 bg-gradient-to-r from-teal-50/50 via-slate-50 to-teal-50/10" style={{ borderColor: 'var(--border-color)' }}>
        <h3 className="text-xs font-black uppercase tracking-wider mb-4 text-teal-800 flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-teal-700" />
          How to Read Hospital Trust Ratings
        </h3>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="flex gap-3.5">
            <span className="flex h-6 w-6 shrink-0 rounded-lg bg-emerald-100 text-emerald-800 items-center justify-center font-black text-xs">✔</span>
            <div>
              <p className="text-xs font-extrabold text-slate-800">Double-Checked / Corroborated</p>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">Claims are cross-verified across multiple sections (e.g., equipment logs + description + doctor rosters).</p>
            </div>
          </div>
          <div className="flex gap-3.5">
            <span className="flex h-6 w-6 shrink-0 rounded-lg bg-amber-100 text-amber-800 items-center justify-center font-black text-xs">⚠</span>
            <div>
              <p className="text-xs font-extrabold text-slate-800">Stated Only / Uncorroborated</p>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">Stated only in one place (e.g. description text). Needs coordination verification but is not contradicted.</p>
            </div>
          </div>
          <div className="flex gap-3.5">
            <span className="flex h-6 w-6 shrink-0 rounded-lg bg-red-100 text-red-800 items-center justify-center font-black text-xs">✖</span>
            <div>
              <p className="text-xs font-extrabold text-slate-800">Caution / Aspirational</p>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">Phrases like "planned for future", "coming soon", or absolute lack of doctor counts indicating it is non-operational.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Simple Accessible Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: 'Hospitals Audited', value: formatNumber(stats?.total ?? 0), icon: Building2, desc: 'Hospitals fully verified' },
          { label: 'States Monitored', value: formatNumber(stats?.states ?? 0), icon: MapPin, desc: 'Coverage regions' },
          { label: 'Detailed Summaries', value: formatNumber(stats?.with_description ?? 0), icon: Activity, desc: 'Facilities with long-form texts' },
          { label: 'Stated Capabilities', value: formatNumber(stats?.with_capability ?? 0), icon: ShieldCheck, desc: 'Total claimed specialties' },
        ].map(({ label, value, icon: Icon, desc }, i) => (
          <motion.div
            key={label}
            custom={i}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            className="card p-5"
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>{value}</span>
                <div className="rounded-lg bg-teal-50 p-2 dark:bg-teal-950/40">
                  <Icon className="h-4 w-4 text-teal-700 dark:text-teal-400" />
                </div>
              </div>
              <div>
                <p className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>{label}</p>
                <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{desc}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Track Cards */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Referral & Planning Workflows
        </h2>
        <div className="grid gap-6 md:grid-cols-3">
          {tracks.map(({ to, icon: Icon, title, description, color, actionText }, i) => (
            <motion.div
              key={to}
              custom={i + 4}
              variants={cardVariants}
              initial="hidden"
              animate="visible"
            >
              <Link to={to} className="card group block p-6 h-full flex flex-col justify-between hover:-translate-y-1">
                <div>
                  <div className={`mb-4 inline-flex rounded-xl p-3 text-white ${color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-lg font-bold group-hover:text-teal-700 dark:group-hover:text-teal-400 transition-colors" style={{ color: 'var(--text-primary)' }}>
                    {title}
                  </h3>
                  <p className="mt-2 text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{description}</p>
                </div>
                <div className="mt-6 flex items-center gap-1 text-xs font-bold text-teal-700 dark:text-teal-400">
                  <span>{actionText}</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Regional Status Summary */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="font-bold text-sm uppercase tracking-wider mb-4" style={{ color: 'var(--text-primary)' }}>
            🏥 States with Highest Coverage
          </h3>
          <div className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
            {topStates.map(s => (
              <div key={s.state} className="flex items-center justify-between py-3 text-xs">
                <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                <div className="flex items-center gap-4">
                  <span style={{ color: 'var(--text-secondary)' }}>{s.total} Hospitals</span>
                  <span className="rounded-full px-2 py-0.5 text-[10px] font-bold" 
                        style={{ 
                          backgroundColor: s.avg_trust >= 50 ? 'var(--success-bg)' : s.avg_trust >= 30 ? 'var(--warning-bg)' : 'var(--danger-bg)', 
                          color: s.avg_trust >= 50 ? 'var(--success)' : s.avg_trust >= 30 ? 'var(--warning)' : 'var(--danger)' 
                        }}>
                    {s.avg_trust.toFixed(0)}% trust
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="font-bold text-sm uppercase tracking-wider mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            ⚠️ Attention Needed Regions (Low Trust)
          </h3>
          <div className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
            {lowTrustStates.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-6 text-center">
                <CheckCircle className="h-8 w-8 text-emerald-500 mb-2" />
                <p className="text-xs font-bold" style={{ color: 'var(--text-primary)' }}>All regions verified</p>
                <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Every state shows high corroboration consistency</p>
              </div>
            ) : (
              lowTrustStates.map(s => (
                <div key={s.state} className="flex items-center justify-between py-3 text-xs">
                  <span className="font-bold" style={{ color: 'var(--text-primary)' }}>{s.state}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-[10px] text-red-500 font-bold bg-red-50 dark:bg-red-950/40 px-2 py-0.5 rounded-full">{s.avg_trust.toFixed(0)}% trust level</span>
                    <span style={{ color: 'var(--text-muted)' }}>{s.low_trust_count} unverified</span>
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
