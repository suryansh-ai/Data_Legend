import { Link } from 'react-router-dom'
import { MapPin, Users, Building2, ChevronRight } from 'lucide-react'
import TrustBadge from './TrustBadge'
import type { Facility } from '@/lib/types'
import { formatNumber, truncate } from '@/lib/utils'

interface FacilityCardProps {
  facility: Facility
}

export default function FacilityCard({ facility }: FacilityCardProps) {
  return (
    <Link
      to={`/facility/${facility.unique_id}`}
      className="card group block cursor-pointer"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold group-hover:text-brand-600 dark:group-hover:text-brand-400" style={{ color: 'var(--text-primary)' }}>
            {truncate(facility.name || 'Unnamed Facility', 60)}
          </h3>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-muted)' }}>
            {truncate(facility.description || '', 100)}
          </p>
        </div>
        <TrustBadge score={facility._trust_score} signal={facility._trust_signal} size="sm" />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs" style={{ color: 'var(--text-secondary)' }}>
        {facility.address_stateOrRegion && (
          <span className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {facility.address_city ? `${facility.address_city}, ` : ''}{facility.address_stateOrRegion}
          </span>
        )}
        {facility.numberDoctors != null && (
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {formatNumber(facility.numberDoctors)} doctors
          </span>
        )}
        {facility.capacity != null && (
          <span className="flex items-center gap-1">
            <Building2 className="h-3 w-3" />
            {formatNumber(facility.capacity)} beds
          </span>
        )}
      </div>

      <div className="mt-3 flex items-center justify-end text-xs font-medium text-brand-600 dark:text-brand-400">
        View details
        <ChevronRight className="ml-1 h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
      </div>
    </Link>
  )
}
