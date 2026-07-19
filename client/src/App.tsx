import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { ThemeProvider } from './components/ThemeToggle'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy-loaded pages for faster initial load and smaller bundles
const Home = lazy(() => import('./pages/Home'))
const TrustDesk = lazy(() => import('./pages/TrustDesk'))
const FacilityDetail = lazy(() => import('./pages/FacilityDetail'))
const MedicalDesert = lazy(() => import('./pages/MedicalDesert'))
const DataReadiness = lazy(() => import('./pages/DataReadiness'))
const TriagePage = lazy(() => import('./pages/Triage').then(m => ({ default: m.TriagePage })))
const BookingPage = lazy(() => import('./pages/Booking').then(m => ({ default: m.BookingPage })))
const NGODashboardPage = lazy(() => import('./pages/NGODashboard').then(m => ({ default: m.NGODashboardPage })))

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={
              <Suspense fallback={<LoadingSpinner />}>
                <Home />
              </Suspense>
            } />
            <Route path="/trust-desk" element={
              <Suspense fallback={<LoadingSpinner />}>
                <TrustDesk />
              </Suspense>
            } />
            <Route path="/facility/:id" element={
              <Suspense fallback={<LoadingSpinner />}>
                <FacilityDetail />
              </Suspense>
            } />
            <Route path="/medical-desert" element={
              <Suspense fallback={<LoadingSpinner />}>
                <MedicalDesert />
              </Suspense>
            } />
            <Route path="/data-readiness" element={
              <Suspense fallback={<LoadingSpinner />}>
                <DataReadiness />
              </Suspense>
            } />
            <Route path="/triage" element={
              <Suspense fallback={<LoadingSpinner />}>
                <TriagePage />
              </Suspense>
            } />
            <Route path="/booking" element={
              <Suspense fallback={<LoadingSpinner />}>
                <BookingPage />
              </Suspense>
            } />
            <Route path="/ngo-dashboard" element={
              <Suspense fallback={<LoadingSpinner />}>
                <NGODashboardPage />
              </Suspense>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
