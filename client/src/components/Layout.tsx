import { useState } from 'react'
import { Outlet, NavLink, Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home,
  ShieldCheck,
  MapPin,
  Database,
  Menu,
  X,
  Search,
  Stethoscope,
  Calendar,
  Building2,
} from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'
import { cn } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { EmergencyBox } from './EmergencyBox'

const navItems = [
  { to: '/', icon: Home, label: 'Overview' },
  { to: '/trust-desk', icon: ShieldCheck, label: 'Trust Desk' },
  { to: '/triage', icon: Stethoscope, label: 'Triage AI' },
  { to: '/booking', icon: Calendar, label: 'Booking' },
  { to: '/ngo-dashboard', icon: Building2, label: 'NGO Panel' },
  { to: '/medical-desert', icon: MapPin, label: 'Desert Map' },
  { to: '/data-readiness', icon: Database, label: 'Readiness' },
]

function GlobalSearch() {
  const [q, setQ] = useState('')
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const navigate = useNavigate()

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setQ(val)
    if (val.trim().length >= 2) {
      try {
        const res = await api.autocomplete(val)
        setSuggestions(res)
        setShowDropdown(true)
      } catch (err) {
        console.error(err)
      }
    } else {
      setSuggestions([])
      setShowDropdown(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (q.trim()) {
      setShowDropdown(false)
      navigate(`/trust-desk?q=${encodeURIComponent(q.trim())}`)
    }
  }

  return (
    <div className="relative w-full max-w-xs">
      <form onSubmit={handleSubmit} className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
        <input
          type="text"
          value={q}
          onChange={handleInputChange}
          onFocus={() => q.trim().length >= 2 && setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
          placeholder="Search hospitals..."
          className="input pl-9 pr-4 py-1.5 text-xs w-full border-none bg-slate-100 dark:bg-slate-800"
        />
      </form>

      {/* Autocomplete Suggestions Dropdown */}
      <AnimatePresence>
        {showDropdown && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            className="absolute left-0 right-0 mt-1 max-h-60 overflow-y-auto rounded-xl border bg-white p-2 shadow-lg dark:bg-slate-900 z-50 text-[11px]"
            style={{ borderColor: 'var(--border-color)' }}
          >
            {suggestions.map((s) => (
              <button
                key={s.unique_id}
                onClick={() => {
                  setQ(s.name)
                  setShowDropdown(false)
                  navigate(`/facility/${s.unique_id}`)
                }}
                className="w-full text-left rounded-lg px-2.5 py-1.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800 flex flex-col gap-0.5"
              >
                <span className="font-bold text-slate-800 dark:text-slate-100 line-clamp-1">{s.name}</span>
                <span className="text-[10px] text-slate-400 font-semibold">{s.city ? `${s.city}, ` : ''}{s.state}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeFacility, setActiveFacility] = useState<{ name: string; phone: string } | null>(null)
  const location = useLocation()

  return (
    <div className="flex min-h-screen flex-col" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      {/* Premium Sticky Top Navbar */}
      <header
        className="sticky top-0 z-[1001] w-full border-b backdrop-blur-md transition-all duration-300"
        style={{
          backgroundColor: 'rgba(var(--bg-primary), 0.8)',
          borderColor: 'var(--border-color)',
        }}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo & Platform Name */}
          <Link to="/" className="flex items-center gap-2.5 group hover:opacity-90 transition-opacity">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-teal-600 text-base font-black text-white shadow-md group-hover:scale-105 transition-transform duration-200" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
              DL
            </div>
            <div>
              <h1 className="text-base font-black tracking-tight leading-none text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Outfit, sans-serif' }}>
                DATA LEGEND
              </h1>
              <p className="text-[9px] uppercase tracking-wider font-extrabold text-teal-600 mt-1">
                India Health Trust Layer
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    'rounded-lg px-3 py-2 text-xs font-bold transition-all duration-200',
                    isActive
                      ? 'bg-teal-50 text-teal-800 dark:bg-teal-950/40 dark:text-teal-400'
                      : 'hover:bg-slate-100 dark:hover:bg-slate-800'
                  )
                }
                style={({ isActive }) => (!isActive ? { color: 'var(--text-secondary)' } : undefined)}
              >
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Search, Theme and Menu buttons */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:block">
              <GlobalSearch />
            </div>

            <ThemeToggle />

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(prev => !prev)}
              className="rounded-lg p-2 lg:hidden transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
              style={{ color: 'var(--text-primary)' }}
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            {/* Backdrop overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-[1001] bg-slate-900/50 backdrop-blur-sm lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            {/* Drawer */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', bounce: 0, duration: 0.3 }}
              className="fixed bottom-0 right-0 top-16 z-[1002] w-full max-w-xs border-l p-6 shadow-xl lg:hidden flex flex-col"
              style={{
                backgroundColor: 'var(--bg-primary)',
                borderColor: 'var(--border-color)',
              }}
            >
              <div className="mb-4 sm:hidden">
                <GlobalSearch />
              </div>
              <nav className="flex flex-col gap-2">
                {navItems.map(({ to, icon: Icon, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-semibold transition-all duration-200',
                        isActive
                          ? 'bg-teal-50 text-teal-800 dark:bg-teal-950/40 dark:text-teal-400'
                          : 'hover:bg-slate-100 dark:hover:bg-slate-800'
                      )
                    }
                    style={({ isActive }) => (!isActive ? { color: 'var(--text-secondary)' } : undefined)}
                  >
                    <Icon className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    {label}
                  </NavLink>
                ))}
              </nav>

              <div className="mt-auto border-t pt-4 text-center text-xs" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
                1,889 Facilities Monitored
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content Layout */}
      <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <Outlet context={{ setActiveFacility }} />
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Floating Emergency Box */}
      <EmergencyBox mode="floating" activeFacility={activeFacility} />
    </div>
  )
}
