import { useEffect, useState } from 'react'
import { useParams, Link, useOutletContext } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowLeft, MapPin, Users, Building2, Shield, FileText,
  Plus, Star, AlertTriangle, CheckCircle, XCircle, Info, Edit3,
  Phone, Mail, Globe, Calendar
} from 'lucide-react'
import { api } from '@/lib/api'
import TrustBadge from '@/components/TrustBadge'
import MapView from '@/components/MapView'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import type { Facility, TrustResult, FacilityNote, Override } from '@/lib/types'
import { formatNumber, cn } from '@/lib/utils'



export default function FacilityDetail() {
  const { id } = useParams<{ id: string }>()
  const { setActiveFacility } = useOutletContext<{ setActiveFacility: (f: { name: string; phone: string } | null) => void }>()
  const [facility, setFacility] = useState<Facility | null>(null)
  const [trust, setTrust] = useState<TrustResult | null>(null)
  const [notes, setNotes] = useState<FacilityNote[]>([])
  const [newNote, setNewNote] = useState('')
  const [inShortlist, setInShortlist] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadingTrust, setLoadingTrust] = useState(true)
  const [error, setError] = useState('')

  // Override State
  const [showOverrideForm, setShowOverrideForm] = useState(false)
  const [overrideScore, setOverrideScore] = useState(50)
  const [overrideReason, setOverrideReason] = useState('')
  const [activeOverride, setActiveOverride] = useState<Override | null>(null)

  const loadData = async () => {
    if (!id) return
    setLoading(true)
    setLoadingTrust(true)

    const facilityPromise = api.getFacility(id)
    const trustPromise = api.scoreFacility(id)
    const notesPromise = api.getNotes(id).catch(() => [])
    const shortlistPromise = api.getShortlist().catch(() => [])
    const overridePromise = api.getOverride(id).catch(() => null)

    let facilityData: Facility | null = null

    try {
      const f = await facilityPromise
      facilityData = f
      setFacility(f)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }

    try {
      const t = await trustPromise
      setTrust(t)
    } catch (e) {
      console.warn('Failed to load trust details:', e)
    } finally {
      setLoadingTrust(false)
    }

    try {
      const [n, sl, ov] = await Promise.all([notesPromise, shortlistPromise, overridePromise])
      setNotes(n)
      setInShortlist(sl.includes(id))
      if (ov && 'new_score' in ov) {
        setActiveOverride(ov)
        setOverrideScore(ov.new_score)
        setOverrideReason(ov.reason)
      } else if (facilityData) {
        setActiveOverride(null)
        setOverrideScore(facilityData._trust_score || 50)
      }
    } catch (e) {
      console.warn('Failed to load secondary facility data:', e)
    }
  }

  useEffect(() => {
    loadData()
  }, [id])

  useEffect(() => {
    if (facility) {
      let rawPhone = facility.officialPhone || '';
      if (!rawPhone && facility.phone_numbers) {
        try {
          const phones = typeof facility.phone_numbers === 'string'
            ? JSON.parse(facility.phone_numbers)
            : facility.phone_numbers;
          if (Array.isArray(phones) && phones.length > 0) {
            rawPhone = phones[0];
          } else if (typeof phones === 'string') {
            rawPhone = phones;
          }
        } catch (e) {
          rawPhone = String(facility.phone_numbers);
        }
      }
      const cleanPhone = String(rawPhone).replace(/[\[\]"']/g, '').trim();
      
      if (cleanPhone) {
        setActiveFacility({
          name: facility.name,
          phone: cleanPhone
        });
      } else {
        setActiveFacility(null);
      }
    } else {
      setActiveFacility(null);
    }
    
    return () => {
      setActiveFacility(null);
    };
  }, [facility, setActiveFacility])

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

  const handleSaveOverride = async () => {
    if (!id || !facility) return
    const originalScore = facility._trust_score || 0
    await api.setOverride(id, originalScore, overrideScore, overrideReason)
    setShowOverrideForm(false)
    loadData() // Refresh details
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

  const getSignalMeta = (signal: string | null) => {
    switch (signal) {
      case 'CORROBORATED':
        return {
          title: 'Double-Checked & Proven (High)',
          color: 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/30 dark:text-teal-400',
          desc: 'This hospital has proven its claims across multiple independent records (descriptions, equipment logs, or staff lists). Very safe to refer patients.'
        }
      case 'CLAIMED_ONLY':
        return {
          title: 'Single Claim Only (Unverified)',
          color: 'text-amber-700 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400',
          desc: 'This hospital states it has this service, but only in one single place. No extra documents corroborate this claim. Caution is advised.'
        }
      case 'WEAK':
        return {
          title: 'Weak / Aspirational Claim (Low)',
          color: 'text-red-700 bg-red-50 dark:bg-red-950/30 dark:text-red-400',
          desc: 'Context suggests this capability is coming in the future, under construction, not equipped, or lack of staff.'
        }
      default:
        return {
          title: 'No Service Stated (Unknown)',
          color: 'text-slate-600 bg-slate-100 dark:bg-slate-800 dark:text-slate-400',
          desc: 'No keyword references or documentation found.'
        }
    }
  }

  const displayScore = activeOverride ? activeOverride.new_score : (facility._trust_score || 0)
  const displaySignal = activeOverride ? 'OVERRIDDEN' : (facility._trust_signal || 'UNKNOWN')

  return (
    <div className="space-y-8 py-2">
      {/* Back Button */}
      <Link to="/trust-desk" className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline">
        <ArrowLeft className="h-3.5 w-3.5" />
        <span>Back to Facility Finder</span>
      </Link>

      {/* Main Facility Information Card */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-8 space-y-6"
      >
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between pb-6 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <div className="space-y-4 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-lg bg-teal-50 text-teal-800 border border-teal-100">
                Verified Health Provider
              </span>
              {facility._facility_type && (
                <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 border">
                  {facility._facility_type}
                </span>
              )}
              {facility._operator_type && (
                <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 border">
                  {facility._operator_type}
                </span>
              )}
            </div>

            <h1 className="text-3xl font-black tracking-tight" style={{ color: 'var(--text-primary)', fontFamily: 'Outfit, sans-serif' }}>
              {facility.name || 'Unnamed Clinic'}
            </h1>
            
            {facility.description && (
              <p className="text-xs leading-relaxed max-w-4xl text-slate-600 font-semibold" style={{ color: 'var(--text-secondary)' }}>
                {facility.description}
              </p>
            )}
          </div>

          {/* Action Area (Score / Shortlist) */}
          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 min-w-[220px]">
            <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-teal-50/40 border text-center relative overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
              <span className="text-[9px] font-bold uppercase tracking-wider text-teal-800/80">Composite Trust Score</span>
              <span className="text-4xl font-black text-teal-700 my-1.5" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>{displayScore.toFixed(0)}%</span>
              
              <span className={cn('text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-wider shadow-sm',
                displaySignal === 'OVERRIDDEN' ? 'bg-amber-100 text-amber-700' :
                displaySignal === 'CORROBORATED' ? 'bg-emerald-100 text-emerald-800' :
                displaySignal === 'CLAIMED_ONLY' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
              )}>
                {displaySignal}
              </span>
            </div>

            <div className="flex gap-2 w-full">
              <button
                onClick={handleShortlistToggle}
                className={cn('btn-secondary flex-1 py-2 text-xs font-bold', inShortlist && 'bg-amber-50 text-amber-700 border-amber-300')}
              >
                <Star className={cn('h-3.5 w-3.5', inShortlist && 'fill-current text-amber-500')} />
                <span>{inShortlist ? 'Shortlisted' : 'Shortlist'}</span>
              </button>
              <button
                onClick={() => setShowOverrideForm(prev => !prev)}
                className="btn-secondary py-2 text-xs"
                title="Override Assessment"
              >
                <Edit3 className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Operational Statistics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl border bg-slate-50/50 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
              <Users className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Doctors Count</span>
              <span className="text-base font-black text-slate-800" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {facility.numberDoctors != null ? `${formatNumber(facility.numberDoctors)} Verified` : 'Unspecified'}
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border bg-slate-50/50 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Patient Beds</span>
              <span className="text-base font-black text-slate-800" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {facility.capacity != null ? `${formatNumber(facility.capacity)} Beds` : 'Unspecified'}
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border bg-slate-50/50 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
              <Calendar className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Year Established</span>
              <span className="text-base font-black text-slate-800" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {facility.yearEstablished || 'Unspecified'}
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl border bg-slate-50/50 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal-700 flex items-center justify-center shrink-0">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Volunteers</span>
              <span className="text-base font-black text-slate-800 capitalize" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {facility.acceptsVolunteers != null ? (facility.acceptsVolunteers ? 'Accepted' : 'No') : 'Unspecified'}
              </span>
            </div>
          </div>
        </div>

        {/* Location & Contact Cards */}
        <div className="grid md:grid-cols-2 gap-6 pt-2">
          {/* Address Card */}
          <div className="p-5 rounded-2xl border bg-slate-50/30 space-y-3">
            <h3 className="text-xs font-black uppercase text-teal-800 tracking-wider flex items-center gap-2">
              <MapPin className="h-4 w-4 text-teal-600" />
              Location Details
            </h3>
            <div className="text-xs space-y-1.5 text-slate-700 leading-relaxed font-semibold">
              {facility.address_line1 && <p className="text-slate-800 font-extrabold">{facility.address_line1}</p>}
              {facility.address_line2 && <p>{facility.address_line2}</p>}
              <p className="text-slate-800 font-bold">
                {facility.city || facility.address_city}, {facility.state || facility.address_stateOrRegion} - {facility.pincode || 'No Pincode'}
              </p>
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wide mt-2">
                Region Type: {facility.state_type || 'State'} | Country: {facility.country || 'India'}
              </p>
            </div>
          </div>

          {/* Contact Details Card */}
          <div className="p-5 rounded-2xl border bg-slate-50/30 space-y-3">
            <h3 className="text-xs font-black uppercase text-teal-800 tracking-wider flex items-center gap-2">
              <Phone className="h-4 w-4 text-teal-600" />
              Contact & Inquiries
            </h3>
            <div className="text-xs space-y-2.5 font-semibold text-slate-700">
              <div className="flex items-center gap-2">
                <span className="text-[9px] uppercase font-bold text-slate-400 min-w-[65px] flex items-center gap-1">
                  <Phone className="h-3 w-3" /> Phone:
                </span>
                <span className="text-slate-800 font-bold">{facility.officialPhone || facility.phone_numbers || 'Not listed'}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[9px] uppercase font-bold text-slate-400 min-w-[65px] flex items-center gap-1">
                  <Mail className="h-3 w-3" /> Email:
                </span>
                {facility.email ? (
                  <a href={`mailto:${facility.email}`} className="text-teal-700 hover:underline font-extrabold">{facility.email}</a>
                ) : (
                  <span className="text-slate-400 italic">Not listed</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[9px] uppercase font-bold text-slate-400 min-w-[65px] flex items-center gap-1">
                  <Globe className="h-3 w-3" /> Website:
                </span>
                {facility.officialWebsite || facility.websites ? (
                  <a href={facility.officialWebsite || facility.websites} target="_blank" rel="noopener noreferrer" className="text-teal-700 hover:underline font-extrabold truncate max-w-[220px]">
                    {facility.officialWebsite || facility.websites}
                  </a>
                ) : (
                  <span className="text-slate-400 italic">Not listed</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Override Form */}
        {showOverrideForm && (
          <div className="p-5 rounded-2xl border bg-slate-50 space-y-4 animate-fade-in" style={{ borderColor: 'var(--border-color)' }}>
            <h3 className="text-sm font-black text-slate-800 flex items-center gap-1.5">
              <Edit3 className="h-4.5 w-4.5 text-teal-600" />
              Override Trust Assessment
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600">Override Trust Score: {overrideScore}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={overrideScore}
                  onChange={(e) => setOverrideScore(Number(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600">Override Reason / Justification</label>
                <input
                  type="text"
                  placeholder="e.g. Verified coordinates on site visit"
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="input py-1.5"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowOverrideForm(false)} className="btn-secondary py-1.5 px-4 text-xs font-bold">Cancel</button>
              <button onClick={handleSaveOverride} className="btn-primary py-1.5 px-4 text-xs font-bold">Save Override</button>
            </div>
          </div>
        )}
      </motion.div>

      {/* Main Columns */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Trust Progress Meter / Checklist (Accessible Visualisation) */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-6 flex flex-col justify-between"
          >
            <div>
              <h2 className="text-lg font-bold mb-1 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <Shield className="h-5 w-5 text-teal-700 dark:text-teal-400" />
                Capability Verification
              </h2>
              <p className="text-xs mb-5" style={{ color: 'var(--text-muted)' }}>
                We cross-examine the facility claims. Below is the simplified verification status.
              </p>

              {trust ? (
                <div className="space-y-4">
                  {Object.entries(trust.capabilities).map(([name, cap]) => {
                    const meta = getSignalMeta(cap.signal)
                    return (
                      <div key={name} className="flex flex-col gap-1.5 p-3 rounded-xl border bg-slate-50 dark:bg-slate-900" style={{ borderColor: 'var(--border-color)' }}>
                        <div className="flex items-center justify-between text-xs font-bold">
                          <span className="capitalize" style={{ color: 'var(--text-primary)' }}>{name} service</span>
                          <span className={cn('px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider', meta.color)}>
                            {cap.signal === 'CORROBORATED' ? 'Double Checked' :
                             cap.signal === 'CLAIMED_ONLY' ? 'Claim Only' :
                             cap.signal === 'WEAK' ? 'Unreliable' : 'Not Listed'}
                          </span>
                        </div>
                        <p className="text-[10px] leading-relaxed" style={{ color: 'var(--text-muted)' }}>{meta.desc}</p>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-xs italic" style={{ color: 'var(--text-muted)' }}>No verification logs available.</p>
              )}
            </div>

            {trust && (
              <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border text-center" style={{ borderColor: 'var(--border-color)' }}>
                  <span className="text-xl font-black text-slate-800 dark:text-slate-100">{trust.metadata.total_claims}</span>
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Claims Made</p>
                </div>
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 text-center">
                  <span className="text-xl font-black text-emerald-700 dark:text-emerald-400">{trust.metadata.corroborated_claims}</span>
                  <p className="text-[10px] font-bold text-emerald-600 dark:text-emerald-500 uppercase tracking-wider">Independent Proofs</p>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {facility.latitude && facility.longitude && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <MapView
                facilities={[facility]}
                height="280px"
                center={[facility.latitude, facility.longitude]}
                zoom={14}
              />
            </motion.div>
          )}

          {/* Evidence Citations */}
          {capabilities.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
              <h2 className="text-lg font-bold mb-1 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <FileText className="h-5 w-5 text-teal-700 dark:text-teal-400" />
                Evidence Receipts & Quotes
              </h2>
              <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
                Here are the exact sentence snippets extracted from the documents:
              </p>

              <div className="max-h-64 space-y-3 overflow-y-auto scrollbar-thin pr-1">
                {capabilities.map(([name, cap]) => (
                  <div key={name} className="p-3 rounded-xl border bg-slate-50 dark:bg-slate-900 space-y-2" style={{ borderColor: 'var(--border-color)' }}>
                    <div className="flex items-center justify-between text-xs font-bold capitalize">
                      <span style={{ color: 'var(--text-primary)' }}>{name} Evidence</span>
                    </div>
                    {cap.evidence.map((ev, i) => (
                      <div key={i} className="text-[11px] leading-relaxed border-l-2 border-teal-500 pl-3.5 py-0.5">
                        <span className="italic" style={{ color: 'var(--text-secondary)' }}>"{ev.text}"</span>
                        <span className="block font-bold text-[9px] uppercase tracking-wider text-slate-400 mt-1">Field: {ev.field}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Analyst Notes Section */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-6 space-y-4"
          >
            <h2 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
              Planner Overrides & Notes History
            </h2>
            <div className="flex gap-2">
              <input
                type="text"
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
                placeholder="Add verification notes, updates, or overrides..."
                className="input flex-1"
              />
              <button onClick={handleAddNote} className="btn-primary" disabled={!newNote.trim()}>
                <Plus className="h-4 w-4" />
                <span>Add Note</span>
              </button>
            </div>

            <div className="max-h-72 space-y-3 overflow-y-auto scrollbar-thin pr-1">
              {notes.length === 0 ? (
                <p className="text-xs italic" style={{ color: 'var(--text-muted)' }}>No audit notes entered yet for this facility.</p>
              ) : (
                notes.map((n, i) => (
                  <div key={i} className="p-4 rounded-xl border bg-slate-50 dark:bg-slate-900/60 text-xs space-y-1" style={{ borderColor: 'var(--border-color)' }}>
                    <p className="leading-relaxed" style={{ color: 'var(--text-primary)' }}>{n.note}</p>
                    <span className="block text-[10px] font-bold text-slate-400">
                      Logged on {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
