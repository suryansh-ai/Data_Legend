import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowLeft, MapPin, Users, Building2, Shield, FileText,
  Plus, Star, AlertTriangle, CheckCircle2, ExternalLink
} from 'lucide-react'
import { api } from '@/lib/api'
import TrustBadge from '@/components/TrustBadge'
import TrustChart from '@/components/TrustChart'
import MapView from '@/components/MapView'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import type { Facility, TrustResult, FacilityNote } from '@/lib/types'
import { formatNumber, trustLabel, cn } from '@/lib/utils'

export default function FacilityDetail() {
  const { id } = useParams<{ id: string }>()
  const [facility, setFacility] = useState<Facility | null>(null)
  const [trust, setTrust] = useState<TrustResult | null>(null)
  const [notes, setNotes] = useState<FacilityNote[]>([])
  const [newNote, setNewNote] = useState('')
  const [inShortlist, setInShortlist] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      api.getFacility(id),
      api.scoreFacility(id),
      api.getNotes(id).catch(() => []),
      api.getShortlist().catch(() => []),
    ])
      .then(([f, t, n, sl]) => {
        setFacility(f)
        setTrust(t)
        setNotes(n)
        setInShortlist(sl.includes(id))
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleAddNote = async () => {
    if (!newNote.trim() || !id) return
    await api.addNote(id, newNote)
    setNotes([{ note: newNote, created_at: new Date().toISOString() }, ...notes])
    setNewNote('')
  }

  const handleShortlistToggle = async () => {
    if (!id) return
    if (inShortlist) {
      await api.removeFromShortlist(id)
    } else {
      await api.addToShortlist(id)
    }
    setInShortlist(!inShortlist)
  }

  if (loading) return <LoadingSpinner />
  if (error || !facility) {
    return (
      <EmptyState
        icon={<AlertTriangle className="h-6 w-6 text-amber-500" />}
        title="Facility not found"
        description={error || 'The requested facility could not be loaded'}
        action={<Link to="/trust-desk" className="btn-primary">Back to Trust Desk</Link>}
      />
    )
  }

  const capabilities = trust
    ? Object.entries(trust.capabilities).filter(([, c]) => c.evidence.length > 0)
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link to="/trust-desk" className="mb-3 inline-flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700 dark:text-brand-400">
          <ArrowLeft className="h-4 w-4" />
          Back to Trust Desk
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {facility.name || 'Unnamed Facility'}
              </h1>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
                {facility.address_stateOrRegion && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {facility.address_city ? `${facility.address_city}, ` : ''}{facility.address_stateOrRegion}
                  </span>
                )}
                {facility.numberDoctors != null && (
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {formatNumber(facility.numberDoctors)} doctors
                  </span>
                )}
                {facility.capacity != null && (
                  <span className="flex items-center gap-1">
                    <Building2 className="h-4 w-4" />
                    {formatNumber(facility.capacity)} beds
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <TrustBadge score={facility._trust_score} signal={facility._trust_signal} size="lg" />
              <button
                onClick={handleShortlistToggle}
                className={cn('btn-secondary', inShortlist && 'bg-amber-50 text-amber-600 dark:bg-amber-900/30')}
              >
                <Star className={cn('h-4 w-4', inShortlist && 'fill-current')} />
                {inShortlist ? 'Shortlisted' : 'Shortlist'}
              </button>
            </div>
          </div>

          {facility.description && (
            <p className="mt-4 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {facility.description}
            </p>
          )}
        </motion.div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Trust Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h2 className="mb-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
            <Shield className="mr-2 inline h-5 w-5 text-brand-500" />
            Trust Breakdown
          </h2>
          {trust ? (
            <>
              <TrustChart trust={trust} variant="radar" />
              <div className="mt-4 space-y-2">
                {Object.entries(trust.capabilities).map(([name, cap]) => (
                  <div key={name} className="flex items-center justify-between text-sm">
                    <span style={{ color: 'var(--text-primary)' }}>{name}</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-20 overflow-hidden rounded-full" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${cap.score * 100}%`,
                            backgroundColor: cap.signal === 'CORROBORATED' ? '#10b981' :
                              cap.signal === 'CLAIMED_ONLY' ? '#f59e0b' :
                              cap.signal === 'WEAK' ? '#ef4444' : '#6b7280',
                          }}
                        />
                      </div>
                      <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        {trustLabel(cap.signal)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-center">
                <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                  <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                    {trust.metadata.total_claims}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Total Claims</p>
                </div>
                <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                  <p className="text-2xl font-bold text-emerald-500">
                    {trust.metadata.corroborated_claims}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Corroborated</p>
                </div>
              </div>
            </>
          ) : (
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No trust data available</p>
          )}
        </motion.div>

        {/* Map + Evidence */}
        <div className="space-y-6">
          {facility.latitude && facility.longitude && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <MapView
                facilities={[facility]}
                height="250px"
                center={[facility.latitude, facility.longitude]}
                zoom={12}
              />
            </motion.div>
          )}

          {/* Evidence */}
          {capabilities.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <h2 className="mb-3 font-semibold" style={{ color: 'var(--text-primary)' }}>
                <FileText className="mr-2 inline h-5 w-5 text-brand-500" />
                Evidence ({capabilities.length} capabilities found)
              </h2>
              <div className="max-h-64 space-y-2 overflow-y-auto scrollbar-thin">
                {capabilities.map(([name, cap]) => (
                  <div key={name} className="rounded-lg border p-3" style={{ borderColor: 'var(--border-color)' }}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{name}</span>
                      <span className={cn('badge text-xs',
                        cap.signal === 'CORROBORATED' ? 'badge-trust-high' :
                        cap.signal === 'CLAIMED_ONLY' ? 'badge-trust-medium' :
                        cap.signal === 'WEAK' ? 'badge-trust-low' : 'badge-trust-unknown'
                      )}>
                        {trustLabel(cap.signal)}
                      </span>
                    </div>
                    {cap.evidence.map((ev, i) => (
                      <p key={i} className="mt-1 text-xs italic" style={{ color: 'var(--text-muted)' }}>
                        "{ev.text}" <span className="not-italic">— {ev.field}</span>
                      </p>
                    ))}
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Notes */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h2 className="mb-3 font-semibold" style={{ color: 'var(--text-primary)' }}>
          Analyst Notes
        </h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
            placeholder="Add a note about this facility..."
            className="input flex-1"
          />
          <button onClick={handleAddNote} className="btn-primary" disabled={!newNote.trim()}>
            <Plus className="h-4 w-4" />
            Add
          </button>
        </div>
        <div className="mt-3 space-y-2">
          {notes.length === 0 ? (
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No notes yet</p>
          ) : (
            notes.map((n, i) => (
              <div key={i} className="rounded-lg border p-3 text-sm" style={{ borderColor: 'var(--border-color)' }}>
                <p style={{ color: 'var(--text-primary)' }}>{n.note}</p>
                <p className="mt-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                  {new Date(n.created_at).toLocaleDateString()}
                </p>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  )
}
