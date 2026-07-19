import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { Facility } from '@/lib/types'
import { trustScoreColor } from '@/lib/utils'

interface MapViewProps {
  facilities: Facility[]
  height?: string
  onFacilityClick?: (facility: Facility) => void
  center?: [number, number]
  zoom?: number
}

export default function MapView({
  facilities,
  height = '500px',
  onFacilityClick,
  center = [20.5937, 78.9629],
  zoom = 5,
}: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)
  const markersLayer = useRef<L.LayerGroup | null>(null)

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return

    const map = L.map(mapRef.current, {
      center,
      zoom,
      scrollWheelZoom: true,
      attributionControl: false,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map)

    markersLayer.current = L.layerGroup().addTo(map)
    mapInstance.current = map

    return () => {
      map.remove()
      mapInstance.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapInstance.current
    const layer = markersLayer.current
    if (!map || !layer) return

    layer.clearLayers()

    const valid = facilities.filter(f => f.latitude && f.longitude)

    valid.forEach(f => {
      const color = trustScoreColor(f._trust_score ?? 0)
      const marker = L.circleMarker([f.latitude!, f.longitude!], {
        radius: 6,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85,
      })

      marker.bindPopup(`
        <div style="min-width:180px;font-family:Inter,system-ui,sans-serif">
          <div style="font-weight:600;font-size:13px;margin-bottom:4px">${f.name || 'Unknown'}</div>
          <div style="font-size:11px;color:#6b7280;margin-bottom:6px">${f.address_city || ''} ${f.address_stateOrRegion || ''}</div>
          <div style="display:flex;align-items:center;gap:6px">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color}"></span>
            <span style="font-size:12px;font-weight:500">Trust: ${f._trust_score != null ? f._trust_score.toFixed(0) : 'N/A'}</span>
          </div>
        </div>
      `)

      if (onFacilityClick) {
        marker.on('click', () => onFacilityClick(f))
      }

      layer.addLayer(marker)
    })

    if (valid.length > 0) {
      const bounds = L.latLngBounds(valid.map(f => [f.latitude!, f.longitude!] as [number, number]))
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [facilities, onFacilityClick])

  return (
    <div
      ref={mapRef}
      style={{ height, width: '100%', borderRadius: '12px', overflow: 'hidden' }}
      className="border"
    />
  )
}
