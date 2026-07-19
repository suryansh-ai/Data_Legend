import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Phone, PhoneCall, Copy, Check, X, ShieldAlert, HeartHandshake, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EmergencyBoxProps {
  mode?: 'inline' | 'floating'
  className?: string
  activeFacility?: { name: string; phone: string } | null
}

export function EmergencyBox({ mode = 'inline', className, activeFacility }: EmergencyBoxProps) {
  const [copiedNumber, setCopiedNumber] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)

  const emergencyContacts = [
    { number: '102', label: 'National Ambulance', desc: 'Free government ambulance service' },
    { number: '108', label: 'Medical Disaster Helpline', desc: 'Emergency response and triage dispatch' },
    { number: '112', label: 'All-in-One Emergency', desc: 'Unified national emergency helpline' },
  ]

  const handleCopy = (num: string) => {
    navigator.clipboard.writeText(num)
    setCopiedNumber(num)
    setTimeout(() => setCopiedNumber(null), 2000)
  }

  const handleCall = (num: string) => {
    window.location.href = `tel:${num}`
  }

  const content = (
    <div
      className={cn(
        "relative overflow-hidden border bg-white dark:bg-slate-950 p-6 rounded-2xl transition-all duration-300",
        "border-red-500/30 dark:border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.08)]",
        "hover:shadow-[0_0_25px_rgba(239,68,68,0.15)] hover:border-red-500/50",
        className
      )}
    >
      {/* Decorative Emergency Background Accent */}
      <div className="absolute right-0 top-0 -translate-y-6 translate-x-6 w-32 h-32 rounded-full bg-red-500/5 blur-3xl pointer-events-none" />

      {/* Header with Pulsing Indicator */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          {/* Pulsing red beacon */}
          <div className="relative flex h-3.5 w-3.5 items-center justify-center">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600"></span>
          </div>
          <div>
            <span className="text-[10px] font-black uppercase tracking-wider text-red-600 dark:text-red-400">
              India Medical Emergency Desk
            </span>
            <h4 className="text-base font-black text-slate-800 dark:text-slate-100 flex items-center gap-1.5 leading-none mt-1">
              <ShieldAlert className="h-4.5 w-4.5 text-red-600" />
              Emergency Response Box
            </h4>
          </div>
        </div>
        {mode === 'floating' && (
          <button
            onClick={() => setIsOpen(false)}
            className="rounded-lg p-1 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Critical First-Aid Advisory */}
      <div className="mb-5 p-3 rounded-xl bg-red-50/50 dark:bg-red-950/20 border border-red-100/50 dark:border-red-950/50 text-[11px] text-red-800 dark:text-red-300">
        <p className="font-extrabold flex items-center gap-1 mb-1 text-red-900 dark:text-red-200">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          Critical Alert Checklist
        </p>
        <ul className="list-disc pl-4 space-y-0.5 font-medium leading-relaxed">
          <li>Call if patient is unconscious, has severe bleeding, or chest pain.</li>
          <li>Ensure you know your exact coordinate location or nearest hospital landmark.</li>
          <li>Do not give food or fluids if patient is choking or unconscious.</li>
        </ul>
      </div>

      {/* Call Buttons Grid */}
      <div className="space-y-3">
        {/* Primary Call Button */}
        <button
          onClick={() => handleCall('102')}
          className="w-full flex items-center justify-between gap-3 p-3.5 rounded-xl text-white font-extrabold text-xs transition-all duration-300 transform active:scale-[0.98] shadow-md hover:shadow-lg bg-gradient-to-r from-red-600 via-rose-600 to-red-600 hover:from-red-700 hover:to-rose-700 group"
        >
          <div className="flex items-center gap-2.5">
            <div className="bg-white/20 p-1.5 rounded-lg">
              <PhoneCall className="h-4 w-4 text-white animate-bounce" />
            </div>
            <div className="text-left">
              <div className="leading-tight text-white/80 text-[10px] font-bold uppercase tracking-wider">Primary Responder</div>
              <div className="text-[13px] font-black tracking-wide">Call National Ambulance (102)</div>
            </div>
          </div>
          <span className="text-[10px] uppercase font-black tracking-widest px-2 py-1 bg-white/10 rounded-lg group-hover:bg-white/20 transition-colors">
            DIAL NOW
          </span>
        </button>

        {/* Secondary Numbers */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {emergencyContacts.filter(c => c.number !== '102').map((contact) => (
            <div
              key={contact.number}
              className="flex items-center justify-between gap-2 p-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors"
            >
              <div className="min-w-0">
                <p className="text-[10px] font-black text-slate-800 dark:text-slate-200 truncate">{contact.label}</p>
                <p className="text-[11px] font-extrabold text-teal-600 dark:text-teal-400 mt-0.5">{contact.number}</p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <button
                  onClick={() => handleCopy(contact.number)}
                  title={`Copy ${contact.number}`}
                  className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-900 text-slate-400 hover:text-slate-600 transition-all active:scale-95"
                >
                  {copiedNumber === contact.number ? (
                    <Check className="h-3.5 w-3.5 text-green-600" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </button>
                <button
                  onClick={() => handleCall(contact.number)}
                  title={`Call ${contact.number}`}
                  className="p-1.5 rounded-lg bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400 border border-teal-100 dark:border-teal-950/60 hover:bg-teal-100 transition-all active:scale-95"
                >
                  <Phone className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Support Tagline */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-900 flex items-center justify-center gap-1.5 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
        <HeartHandshake className="h-3.5 w-3.5 text-teal-600" />
        Data Legend • Indian Health Trust Layer
      </div>
    </div>
  )

  if (mode === 'inline') {
    return content
  }

  return (
    <div className="fixed bottom-6 right-6 z-[1050] flex flex-col items-end">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 350 }}
            className="mb-4 w-[340px] max-w-[calc(100vw-2rem)]"
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={() => {
          if (activeFacility && activeFacility.phone) {
            handleCall(activeFacility.phone)
          } else {
            setIsOpen(!isOpen)
          }
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title={activeFacility ? `Call ${activeFacility.name} Desk (${activeFacility.phone})` : "Emergency Ambulance Desk"}
        className={cn(
          "flex h-14 w-14 items-center justify-center rounded-full text-white shadow-xl focus:outline-none transition-colors border",
          isOpen
            ? "bg-slate-800 border-slate-700 text-slate-200"
            : activeFacility
              ? "bg-gradient-to-br from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 border-emerald-500 shadow-[0_4px_20px_rgba(16,185,129,0.4)]"
              : "bg-gradient-to-br from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 border-red-500 shadow-[0_4px_20px_rgba(239,68,68,0.4)]"
        )}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <div className="relative flex items-center justify-center">
            <span className={cn(
              "animate-ping absolute inline-flex h-10 w-10 rounded-full opacity-40",
              activeFacility ? "bg-emerald-400" : "bg-red-400"
            )}></span>
            <PhoneCall className="h-6 w-6 relative text-white animate-pulse" />
          </div>
        )}
      </motion.button>
    </div>
  )
}
