import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { ShieldCheck, Heart, AlertTriangle, ArrowLeft, Activity, Calendar, Stethoscope, ChevronRight, Sparkles } from 'lucide-react';
import { EmergencyBox } from '../components/EmergencyBox';

interface TriageResult {
  symptoms: string[];
  specialties: Array<{ name: string; confidence: number }>;
  urgency: {
    level: string;
    score: number;
    description: string;
  };
  recommendations: string[];
  red_flags: string[];
}

interface Hospital {
  facility_id: string;
  name: string;
  city: string;
  state: string;
  trust_score: number;
  trust_signal: string;
  distance_km: number | null;
  composite_score: number;
  score_breakdown: Record<string, number>;
  specialties_matched: string[];
  has_emergency: boolean;
  has_icu: boolean;
  has_maternity: boolean;
}

export function TriagePage() {
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState<number | ''>('');
  const [patientGender, setPatientGender] = useState('');
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'input' | 'result' | 'hospitals'>('input');

  const handleTriage = async () => {
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Perform triage assessment
      const triageResponse = await api.post<{ status: string; data: TriageResult }>('/triage/assess', {
        symptoms,
        patient_age: patientAge || undefined,
        patient_gender: patientGender || undefined,
      });

      const data = triageResponse.data;
      setTriageResult(data);
      setStep('result');

      // Get hospital recommendations
      if (data.specialties && data.specialties.length > 0) {
        const specialties = data.specialties.map((s: any) => s.name);
        const recommendationResponse = await api.post<{ status: string; data: Hospital[] }>('/triage/recommend', {
          specialties,
          urgency_level: data.urgency.level,
          max_distance_km: 100,
        });

        setHospitals(recommendationResponse.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to perform triage');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setTriageResult(null);
    setHospitals([]);
    setStep('input');
    setError(null);
  };

  const getFirstAidAdvisory = (level: string) => {
    switch (level.toUpperCase()) {
      case 'EMERGENT':
        return {
          title: "Critical Emergency First-Aid Advice",
          tips: [
            "Call the national emergency health helpline (108 / 102) immediately.",
            "Do NOT give the patient anything to eat or drink (including water).",
            "Keep the patient calm, sitting upright, and loosen any tight clothing.",
            "If unconscious but breathing, place them in the recovery position (on their side).",
            "If chest pain is present, keep them completely at rest and avoid any physical exertion."
          ]
        };
      case 'URGENT':
        return {
          title: "Urgent Care Advisory",
          tips: [
            "Seek consultation at a hospital clinic or outpatient desk today.",
            "Avoid strenuous physical activities or heavy lifting until assessed.",
            "Monitor body temperature and heart rate hourly.",
            "Keep a written log of when symptoms start and any changes to report to the doctor."
          ]
        };
      default:
        return {
          title: "Routine Care & Observation Advice",
          tips: [
            "Monitor symptoms closely for the next 24-48 hours.",
            "Ensure adequate hydration and rest.",
            "If symptoms worsen or you develop new danger signs, repeat this assessment immediately."
          ]
        };
    }
  };

  const getUrgencyBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case 'EMERGENT':
        return {
          bg: 'bg-red-50 text-red-700 border-red-100',
          indicator: 'bg-red-500',
        };
      case 'URGENT':
        return {
          bg: 'bg-amber-50 text-amber-700 border-amber-100',
          indicator: 'bg-amber-500',
        };
      case 'SEMI_URGENT':
        return {
          bg: 'bg-teal-50 text-teal-700 border-teal-100',
          indicator: 'bg-teal-500',
        };
      default:
        return {
          bg: 'bg-slate-50 text-slate-700 border-slate-100',
          indicator: 'bg-teal-500',
        };
    }
  };

  const getUrgencyMeta = (level: string) => {
    switch (level) {
      case 'EMERGENT':
        return {
          title: '🚨 CRITICAL - Seek Emergency Care Immediately',
          color: 'bg-red-50 text-red-900 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30',
          indicator: 'bg-red-500',
        };
      case 'URGENT':
        return {
          title: '⚠️ URGENT - Go to a Clinic/Hospital Today',
          color: 'bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/30',
          indicator: 'bg-amber-500',
        };
      case 'SEMI_URGENT':
        return {
          title: '🕒 SEMI-URGENT - Seek medical attention within 24-48 hours',
          color: 'bg-yellow-50 text-yellow-900 border-yellow-200 dark:bg-yellow-950/20 dark:text-yellow-400 dark:border-yellow-900/30',
          indicator: 'bg-yellow-500',
        };
      default:
        return {
          title: 'ℹ️ ROUTINE - Normal consultation recommended',
          color: 'bg-teal-50 text-teal-900 border-teal-200 dark:bg-teal-950/20 dark:text-teal-400 dark:border-teal-900/30',
          indicator: 'bg-teal-500',
        };
    }
  };

  return (
    <div className="space-y-8 py-2 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
          AI Referral & Triage Copilot
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Input patient symptoms to evaluate emergency level and match with certified, high-trust clinics.
        </p>
      </div>

      {/* Step 1: Input */}
      {step === 'input' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6 space-y-6 md:col-span-2"
          >
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <Stethoscope className="h-5 w-5 text-teal-600" />
                Patient Assessment
              </h2>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400">Describe Symptoms in Plain Words</label>
                </div>

                {/* Premium Textarea Wrapper */}
                <div className="relative rounded-xl border bg-white dark:bg-slate-900 focus-within:ring-2 focus-within:ring-teal-500 transition-all overflow-hidden" style={{ borderColor: 'var(--border-color)' }}>
                  <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Example: Chest discomfort radiating to left arm, sweating, breathing troubles since 30 minutes..."
                    rows={5}
                    className="w-full resize-none p-4 pb-14 text-xs bg-transparent border-none focus:outline-none focus:ring-0 text-slate-800 dark:text-slate-100"
                  />

                  {/* Bottom Actions Bar inside Textarea */}
                  <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between border-t pt-2" style={{ borderColor: 'var(--border-color)' }}>
                    <div className="flex items-center gap-2">
                      {symptoms && (
                        <button
                          type="button"
                          onClick={() => setSymptoms('')}
                          className="text-[10px] text-slate-500 hover:text-red-500 font-extrabold"
                        >
                          Clear
                        </button>
                      )}
                    </div>

                    <span className="text-[10px] text-slate-400 font-semibold">{symptoms.length} chars</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400">Patient Age (Years)</label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value ? parseInt(e.target.value) : '')}
                    placeholder="e.g. 45"
                    min={0}
                    className="input py-2"
                  />
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-bold text-slate-600 dark:text-slate-400">Patient Gender</label>
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    className="input py-2"
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {error && (
              <div className="p-3.5 rounded-xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 text-xs text-red-700 dark:text-red-400">
                {error}
              </div>
            )}

            <button
              onClick={handleTriage}
              disabled={loading || !symptoms.trim()}
              className="btn-primary w-full py-3 text-sm font-bold"
            >
              {loading ? 'Analyzing Symptoms...' : 'Analyze Triage Priority'}
            </button>
          </motion.div>

          <div className="md:col-span-1 space-y-4">
            <EmergencyBox mode="inline" />
          </div>
        </div>
      )}

      {/* Step 2: Assessment Results */}
      {step === 'result' && triageResult && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Back Action */}
          <button onClick={() => setStep('input')} className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline">
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Modify Symptoms</span>
          </button>

          {/* Urgency Alert */}
          {(() => {
            const meta = getUrgencyMeta(triageResult.urgency.level)
            return (
              <div className={`p-6 rounded-2xl border-2 space-y-2 ${meta.color}`}>
                <div className="flex items-center gap-2">
                  <span className={`h-3 w-3 rounded-full ${meta.indicator}`} />
                  <h3 className="font-extrabold text-base uppercase tracking-wider">{meta.title}</h3>
                </div>
                <p className="text-xs leading-relaxed opacity-90">{triageResult.urgency.description}</p>
              </div>
            )
          })()}

          {/* Red Flags Alert */}
          {triageResult.red_flags.length > 0 && (
            <div className="p-6 rounded-2xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 space-y-3">
              <h3 className="font-bold text-sm text-red-900 dark:text-red-400 flex items-center gap-2">
                <AlertTriangle className="h-4.5 w-4.5 text-red-600" />
                CRITICAL DANGER SIGNS (Seek Care Immediate)
              </h3>
              <ul className="list-disc list-inside text-xs text-red-800 dark:text-red-300 space-y-1">
                {triageResult.red_flags.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
            </div>
          )}

          {/* First-Aid / Advisory Guidelines */}
          {(() => {
            const advice = getFirstAidAdvisory(triageResult.urgency.level);
            const isEmergent = triageResult.urgency.level.toUpperCase() === 'EMERGENT';
            return (
              <div className={`p-6 rounded-2xl border font-semibold space-y-3 ${
                isEmergent 
                  ? 'border-red-200 bg-red-50/50 text-red-900 animate-pulse' 
                  : 'border-teal-100 bg-teal-50/30 text-teal-900'
              }`}>
                <h3 className="text-sm font-black uppercase tracking-wider flex items-center gap-2">
                  <Activity className="h-4.5 w-4.5 text-teal-600" />
                  {advice.title}
                </h3>
                <ul className="list-disc list-inside text-xs leading-relaxed space-y-2 opacity-90">
                  {advice.tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            );
          })()}

          {/* Symptoms & Specialties Breakdown */}
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="card p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Identified Symptoms</h3>
              <div className="flex flex-wrap gap-1.5">
                {triageResult.symptoms.map((symptom, idx) => (
                  <span key={idx} className="rounded-lg bg-slate-100 dark:bg-slate-800 px-2.5 py-1 text-xs font-bold text-slate-800 dark:text-slate-200 capitalize">
                    {symptom}
                  </span>
                ))}
              </div>
            </div>

            <div className="card p-5 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Match Specialties</h3>
              <div className="divide-y" style={{ borderColor: 'var(--border-color)' }}>
                {triageResult.specialties.map((spec, idx) => (
                  <div key={idx} className="flex justify-between py-2 text-xs">
                    <span className="font-bold capitalize" style={{ color: 'var(--text-primary)' }}>{spec.name}</span>
                    <span className="text-[10px] bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400 px-2 py-0.5 rounded-full font-bold">
                      {Math.round(spec.confidence * 100)}% Match
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Core Recommendations */}
          <div className="card p-6 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Diagnostic Advice</h3>
            <ul className="space-y-2 text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {triageResult.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-teal-600 font-bold">✓</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Bottom Action Area */}
          <div className="flex items-center gap-3">
            {hospitals.length > 0 ? (
              <button
                onClick={() => setStep('hospitals')}
                className="btn-primary flex-1 py-3 text-xs"
              >
                <span>View Recommended Hospitals ({hospitals.length})</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                onClick={() => navigate('/trust-desk')}
                className="btn-primary flex-1 py-3 text-xs"
              >
                Go to Facility Finder
              </button>
            )}
          </div>
        </motion.div>
      )}

      {/* Step 3: Hospital Matches */}
      {step === 'hospitals' && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Header Action */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              Recommended Health Facilities
            </h2>
            <button
              onClick={() => setStep('result')}
              className="text-xs font-bold text-teal-700 dark:text-teal-400 hover:underline"
            >
              ← Back to Assessment
            </button>
          </div>

          {hospitals.length === 0 ? (
            <div className="card p-8 text-center">
              <p className="text-xs text-slate-500">
                No verified clinics match this medical need in the vicinity.
              </p>
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2">
              {hospitals.map((hospital, idx) => (
                <motion.div
                  key={hospital.facility_id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="card p-5 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-extrabold text-base leading-tight" style={{ color: 'var(--text-primary)' }}>
                          {hospital.name}
                        </h3>
                        <p className="text-xs font-semibold text-slate-400 mt-0.5">
                          {hospital.city}, {hospital.state}
                        </p>
                      </div>
                      <div className="text-right flex flex-col items-end">
                        <span className="text-lg font-black text-teal-700 dark:text-teal-400">{hospital.trust_score.toFixed(0)}%</span>
                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Trust Score</span>
                      </div>
                    </div>

                    {/* Explainable AI Match Justification */}
                    <div className="p-3.5 rounded-xl border border-teal-100/50 bg-teal-50/20 text-[11px] text-slate-600 font-semibold space-y-1 mt-3">
                      <span className="text-[9px] font-black uppercase tracking-wider text-teal-800 flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-teal-600" />
                        AI Recommendation Logic
                      </span>
                      <p className="leading-relaxed">
                        Recommended for <span className="font-extrabold text-teal-900 capitalize">{hospital.specialties_matched[0] || 'general medicine'}</span> due to a strong {hospital.trust_score.toFixed(0)}% trust rating. It has verified {hospital.has_emergency ? 'emergency services' : ''} {hospital.has_icu ? 'and active intensive care units' : ''} located {hospital.distance_km ? `${hospital.distance_km} km away` : 'locally'}.
                      </p>
                    </div>

                    {/* Meta Indicators */}
                    <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t" style={{ borderColor: 'var(--border-color)' }}>
                      <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border" style={{ borderColor: 'var(--border-color)' }}>
                        <span className="text-xs font-bold block text-teal-600">{hospital.composite_score.toFixed(1)}</span>
                        <span className="text-[9px] text-slate-400 block font-semibold uppercase tracking-wider">Rank</span>
                      </div>
                      {hospital.distance_km !== null && (
                        <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border" style={{ borderColor: 'var(--border-color)' }}>
                          <span className="text-xs font-bold block text-emerald-600">{hospital.distance_km} km</span>
                          <span className="text-[9px] text-slate-400 block font-semibold uppercase tracking-wider">Distance</span>
                        </div>
                      )}
                      <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border" style={{ borderColor: 'var(--border-color)' }}>
                        <div className="flex justify-center gap-0.5 mt-0.5">
                          {hospital.has_emergency && <span className="text-[8px] font-bold bg-red-100 text-red-800 px-1 rounded">ER</span>}
                          {hospital.has_icu && <span className="text-[8px] font-bold bg-orange-100 text-orange-800 px-1 rounded">ICU</span>}
                        </div>
                        <span className="text-[9px] text-slate-400 block font-semibold uppercase tracking-wider mt-0.5">Service</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-6">
                    <button
                      onClick={() => navigate(`/facility/${hospital.facility_id}`)}
                      className="btn-secondary flex-1 py-1.5 text-xs font-bold"
                    >
                      Inspect Evidence
                    </button>
                    <button
                      onClick={() => navigate(`/booking?facility=${hospital.facility_id}`)}
                      className="btn-primary flex-1 py-1.5 text-xs font-bold"
                    >
                      Book Bed/Slot
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          <button
            onClick={() => setStep('input')}
            className="btn-secondary w-full py-3 text-xs"
          >
            Start New Triage
          </button>
        </motion.div>
      )}
    </div>
  );
}