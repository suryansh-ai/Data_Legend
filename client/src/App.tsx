import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './components/ThemeToggle'
import Layout from './components/Layout'
import Home from './pages/Home'
import TrustDesk from './pages/TrustDesk'
import FacilityDetail from './pages/FacilityDetail'
import MedicalDesert from './pages/MedicalDesert'
import DataReadiness from './pages/DataReadiness'
import { TriagePage } from './pages/Triage'
import { BookingPage } from './pages/Booking'
import { NGODashboardPage } from './pages/NGODashboard'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/trust-desk" element={<TrustDesk />} />
            <Route path="/facility/:id" element={<FacilityDetail />} />
            <Route path="/medical-desert" element={<MedicalDesert />} />
            <Route path="/data-readiness" element={<DataReadiness />} />
            <Route path="/triage" element={<TriagePage />} />
            <Route path="/booking" element={<BookingPage />} />
            <Route path="/ngo-dashboard" element={<NGODashboardPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
