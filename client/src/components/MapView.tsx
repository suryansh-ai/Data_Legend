import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Navigation, X, AlertTriangle, Loader2 } from 'lucide-react'
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

  // Route & Navigation States
  const [routeInfo, setRouteInfo] = useState<{ distance: number; duration: number; destName: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // References to active route layers to allow clearing
  const routeLayerRef = useRef<L.Polyline | null>(null)
  const startMarkerRef = useRef<L.Marker | null>(null)

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

    // Listen to popup opens to attach click handler to the directions button
    map.on('popupopen', (e) => {
      const popupNode = e.popup.getElement()
      if (!popupNode) return
      
      const btn = popupNode.querySelector('.dir-popup-btn') as HTMLButtonElement
      if (btn) {
        const lat = parseFloat(btn.getAttribute('data-lat') || '0')
        const lng = parseFloat(btn.getAttribute('data-lng') || '0')
        const name = btn.getAttribute('data-name') || ''
        btn.onclick = () => {
          map.closePopup()
          getDirections(lat, lng, name)
        }
      }
    })

    return () => {
      map.remove()
      mapInstance.current = null
      routeLayerRef.current = null
      startMarkerRef.current = null
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
        <div style="min-width:180px;font-family:Inter,system-ui,sans-serif;padding:2px">
          <div style="font-weight:700;font-size:13px;margin-bottom:4px;color:#0f172a">${f.name || 'Unknown'}</div>
          <div style="font-size:11px;color:#64748b;margin-bottom:8px">${f.address_city || ''}, ${f.address_stateOrRegion || ''}</div>
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color}"></span>
            <span style="font-size:11px;font-weight:600">Trust Score: ${f._trust_score != null ? f._trust_score.toFixed(0) : 'N/A'}%</span>
          </div>
          <button 
            class="dir-popup-btn" 
            data-lat="${f.latitude!}" 
            data-lng="${f.longitude!}" 
            data-name="${f.name.replace(/"/g, '&quot;')}"
            style="width:100%;text-align:center;background:#0f766e;color:white;font-weight:700;font-size:11px;border:none;border-radius:6px;padding:6px 10px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px"
          >
            📍 Get Driving Directions
          </button>
        </div>
      `)

      if (onFacilityClick) {
        marker.on('click', () => onFacilityClick(f))
      }

      layer.addLayer(marker)
    })

    // Fit bounds if no route is active
    if (valid.length > 0 && !routeInfo) {
      if (valid.length >= 1000) {
        map.setView(center, 5)
      } else {
        const bounds = L.latLngBounds(valid.map(f => [f.latitude!, f.longitude!] as [number, number]))
        map.fitBounds(bounds, { padding: [20, 20] })
      }
    }
  }, [facilities, onFacilityClick, routeInfo])

  // Get GPS Location and fetch Route from OSRM
  const getDirections = (destLat: number, destLng: number, destName: string) => {
    if (!mapInstance.current) return
    setLoading(true)
    setError(null)

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.')
      setLoading(false)
      return
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const userLat = position.coords.latitude
        const userLng = position.coords.longitude

        try {
          // OSRM expects coordinates as: lng,lat
          const url = `https://router.project-osrm.org/route/v1/driving/${userLng},${userLat};${destLng},${destLat}?overview=full&geometries=geojson`
          const response = await fetch(url)
          
          if (!response.ok) {
            throw new Error('Routing server error. Please try again.')
          }
          
          const data = await response.json()
          
          if (!data.routes || data.routes.length === 0) {
            throw new Error('No driving route found.')
          }

          const route = data.routes[0]
          const distanceKm = route.distance / 1000
          const durationMins = route.duration / 60
          const geom = route.geometry

          const map = mapInstance.current!

          // Clear previous route elements
          if (routeLayerRef.current) {
            map.removeLayer(routeLayerRef.current)
          }
          if (startMarkerRef.current) {
            map.removeLayer(startMarkerRef.current)
          }

          // Convert GeoJSON coords [lng, lat] to Leaflet [lat, lng]
          const latLngs = geom.coordinates.map(([lng, lat]: [number, number]) => [lat, lng] as [number, number])

          // Draw the polyline path
          const polyline = L.polyline(latLngs, {
            color: '#0f766e',
            weight: 5,
            opacity: 0.8,
            lineJoin: 'round',
          }).addTo(map)

          routeLayerRef.current = polyline

          // Custom pulsing marker icon for user location
          const userIcon = L.divIcon({
            className: 'custom-user-marker',
            html: `
              <div style="position:relative;display:flex;height:20px;width:20px;align-items:center;justify-content:center;">
                <span style="position:absolute;display:inline-flex;height:100%;width:100%;border-radius:50%;background-color:#2dd4bf;opacity:0.6;animation:ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
                <span style="position:relative;display:inline-flex;border-radius:50%;height:10px;width:10px;background-color:#0d9488;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.2);"></span>
              </div>
            `,
            iconSize: [20, 20],
            iconAnchor: [10, 10],
          })

          const userMarker = L.marker([userLat, userLng], { icon: userIcon }).addTo(map)
          startMarkerRef.current = userMarker

          // Zoom map to fit the route
          map.fitBounds(polyline.getBounds(), { padding: [40, 40] })

          setRouteInfo({
            distance: distanceKm,
            duration: durationMins,
            destName,
          })
        } catch (err: any) {
          setError(err.message || 'Failed to calculate driving route.')
        } finally {
          setLoading(false)
        }
      },
      (geoError) => {
        setLoading(false)
        switch (geoError.code) {
          case geoError.PERMISSION_DENIED:
            setError('Location access denied. Enable GPS in browser settings.')
            break
          case geoError.POSITION_UNAVAILABLE:
            setError('Location details unavailable.')
            break
          case geoError.TIMEOUT:
            setError('Location request timed out.')
            break
          default:
            setError('Failed to retrieve your location.')
        }
      },
      { timeout: 10000, enableHighAccuracy: true }
    )
  }

  const clearRoute = () => {
    const map = mapInstance.current
    if (map) {
      if (routeLayerRef.current) {
        map.removeLayer(routeLayerRef.current)
        routeLayerRef.current = null
      }
      if (startMarkerRef.current) {
        map.removeLayer(startMarkerRef.current)
        startMarkerRef.current = null
      }
      const valid = facilities.filter(f => f.latitude && f.longitude)
      if (valid.length > 0) {
        const bounds = L.latLngBounds(valid.map(f => [f.latitude!, f.longitude!] as [number, number]))
        map.fitBounds(bounds, { padding: [20, 20] })
      }
    }
    setRouteInfo(null)
    setError(null)
  }

  const singleFacility = facilities.length === 1 ? facilities[0] : null

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border" style={{ height, borderColor: 'var(--border-color)' }}>
      <div
        ref={mapRef}
        style={{ height: '100%', width: '100%' }}
      />

      {/* Floating Directions Panel */}
      <div className="absolute top-3 right-3 z-[1000] w-[260px] max-w-[calc(100vw-2rem)] flex flex-col gap-2 pointer-events-auto">
        {/* Loading Indicator */}
        {loading && (
          <div className="flex items-center gap-2 p-3 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm rounded-xl border border-slate-100 dark:border-slate-800 shadow-lg text-xs font-bold text-slate-800 dark:text-slate-200">
            <Loader2 className="h-4 w-4 text-teal-600 animate-spin" />
            <span>Locating & routing...</span>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="flex items-start gap-2 p-3 bg-red-50/95 dark:bg-red-950/95 backdrop-blur-sm rounded-xl border border-red-200 dark:border-red-900/40 shadow-lg text-[11px] font-bold text-red-800 dark:text-red-300">
            <AlertTriangle className="h-4.5 w-4.5 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
            <div className="flex-1">
              <p>{error}</p>
              <button onClick={() => setError(null)} className="text-[10px] uppercase font-black tracking-wider text-red-950 dark:text-red-200 hover:underline mt-1">Dismiss</button>
            </div>
          </div>
        )}

        {/* Active Route Summary */}
        {routeInfo && (
          <div className="p-3.5 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm rounded-xl border border-slate-100 dark:border-slate-800 shadow-lg text-xs space-y-2.5">
            <div>
              <div className="text-[9px] uppercase font-black tracking-widest text-teal-600 dark:text-teal-400">Active Driving Route</div>
              <div className="font-extrabold text-slate-800 dark:text-slate-100 truncate mt-0.5">{routeInfo.destName}</div>
            </div>
            <div className="grid grid-cols-2 gap-2 border-y py-2 border-slate-100 dark:border-slate-800">
              <div>
                <span className="text-[9px] text-slate-400 font-bold uppercase block">Distance</span>
                <span className="text-xs font-black text-slate-800 dark:text-slate-200">{routeInfo.distance.toFixed(1)} km</span>
              </div>
              <div>
                <span className="text-[9px] text-slate-400 font-bold uppercase block">Est. Duration</span>
                <span className="text-xs font-black text-slate-800 dark:text-slate-200">{routeInfo.duration.toFixed(0)} mins</span>
              </div>
            </div>
            <button
              onClick={clearRoute}
              className="w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-[10px] font-black uppercase tracking-wider text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="h-3.5 w-3.5" />
              Clear Route
            </button>
          </div>
        )}

        {/* Directions button for single facility maps */}
        {singleFacility && !routeInfo && !loading && (
          <button
            onClick={() => getDirections(singleFacility.latitude!, singleFacility.longitude!, singleFacility.name)}
            className="flex items-center justify-center gap-2 py-2.5 px-4 bg-teal-700 hover:bg-teal-800 text-white rounded-xl shadow-lg border border-teal-600 transition-all font-bold text-xs active:scale-[0.98]"
          >
            <Navigation className="h-4 w-4 text-white fill-current" />
            <span>Show Route from My Location</span>
          </button>
        )}
      </div>
    </div>
  )
}
