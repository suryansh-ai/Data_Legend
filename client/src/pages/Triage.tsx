/**
 * Triage Page — AI-powered symptom assessment and hospital recommendation.
 * Patients can describe symptoms and get matched to appropriate facilities.
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { VoiceInput } from '../components/VoiceInput';
import { api } from '../lib/api';

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
      const triageResponse = await api.post('/triage/assess', {
        symptoms,
        patient_age: patientAge || undefined,
        patient_gender: patientGender || undefined,
      });

      setTriageResult(triageResponse.data);
      setStep('result');

      // Get hospital recommendations
      if (triageResponse.data.specialties.length > 0) {
        const specialties = triageResponse.data.specialties.map((s: any) => s.name);
        const recommendationResponse = await api.post('/triage/recommend', {
          specialties,
          urgency_level: triageResponse.data.urgency.level,
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

  const handleVoiceInput = (text: string) => {
    setSymptoms(prev => prev ? `${prev} ${text}` : text);
  };

  const getUrgencyColor = (level: string) => {
    switch (level) {
      case 'EMERGENT': return 'bg-red-100 text-red-800 border-red-200';
      case 'URGENT': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'SEMI_URGENT': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'NON_URGENT': return 'bg-green-100 text-green-800 border-green-200';
      case 'ROUTINE': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTrustColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Medical Triage
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Describe your symptoms and get matched to the right healthcare facility
        </p>
      </motion.div>

      {/* Step 1: Symptom Input */}
      {step === 'input' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6"
        >
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            Describe Your Symptoms
          </h2>

          <div className="mb-6">
            <VoiceInput
              onTranscript={handleVoiceInput}
              placeholder="Speak or type your symptoms (e.g., 'chest pain, shortness of breath')"
              className="mb-4"
            />
            
            <textarea
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Describe your symptoms in detail..."
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Patient Age (optional)
              </label>
              <input
                type="number"
                value={patientAge}
                onChange={(e) => setPatientAge(e.target.value ? parseInt(e.target.value) : '')}
                placeholder="Age"
                min={0}
                max={150}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Patient Gender (optional)
              </label>
              <select
                value={patientGender}
                onChange={(e) => setPatientGender(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900 rounded-lg">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          <button
            onClick={handleTriage}
            disabled={loading || !symptoms.trim()}
            className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Analyzing Symptoms...' : 'Get Assessment'}
          </button>
        </motion.div>
      )}

      {/* Step 2: Triage Result */}
      {step === 'result' && triageResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Urgency Assessment */}
          <div className={`p-6 rounded-xl border-2 ${getUrgencyColor(triageResult.urgency.level)}`}>
            <h3 className="text-lg font-semibold mb-2">Urgency Level: {triageResult.urgency.level}</h3>
            <p className="text-sm mb-2">{triageResult.urgency.description}</p>
            <p className="text-xs opacity-75">Score: {triageResult.urgency.score}/5</p>
          </div>

          {/* Red Flags */}
          {triageResult.red_flags.length > 0 && (
            <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
                ⚠️ Red Flags Detected
              </h3>
              <ul className="list-disc list-inside text-red-700 dark:text-red-300">
                {triageResult.red_flags.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
              <p className="mt-3 text-sm text-red-600 dark:text-red-400">
                Please seek immediate medical attention!
              </p>
            </div>
          )}

          {/* Symptoms & Specialties */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Identified Symptoms
              </h3>
              <ul className="space-y-2">
                {triageResult.symptoms.map((symptom, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{symptom}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Recommended Specialties
              </h3>
              <ul className="space-y-2">
                {triageResult.specialties.map((spec, idx) => (
                  <li key={idx} className="flex items-center justify-between">
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{spec.name}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {Math.round(spec.confidence * 100)}% match
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              Recommendations
            </h3>
            <ul className="space-y-2">
              {triageResult.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => setStep('input')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
            >
              New Assessment
            </button>
            {hospitals.length > 0 && (
              <button
                onClick={() => setStep('hospitals')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Recommended Hospitals ({hospitals.length})
              </button>
            )}
          </div>
        </motion.div>
      )}

      {/* Step 3: Hospital Recommendations */}
      {step === 'hospitals' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Recommended Hospitals
            </h2>
            <button
              onClick={() => setStep('result')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700"
            >
              ← Back to Assessment
            </button>
          </div>

          {hospitals.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                No hospitals found matching your criteria. Try adjusting your search.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {hospitals.map((hospital, idx) => (
                <motion.div
                  key={hospital.facility_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {hospital.name}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {hospital.city}, {hospital.state}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getTrustColor(hospital.trust_score)}`}>
                        {hospital.trust_score.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Trust Score
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-lg font-semibold text-blue-600">
                        {hospital.composite_score.toFixed(1)}
                      </div>
                      <div className="text-xs text-gray-500">Overall Score</div>
                    </div>
                    {hospital.distance_km !== null && (
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-lg font-semibold text-green-600">
                          {hospital.distance_km} km
                        </div>
                        <div className="text-xs text-gray-500">Distance</div>
                      </div>
                    )}
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-lg font-semibold text-purple-600">
                        {hospital.specialties_matched.length}
                      </div>
                      <div className="text-xs text-gray-500">Specialties Matched</div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex justify-center gap-1">
                        {hospital.has_emergency && (
                          <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">ER</span>
                        )}
                        {hospital.has_icu && (
                          <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">ICU</span>
                        )}
                        {hospital.has_maternity && (
                          <span className="px-2 py-1 bg-pink-100 text-pink-800 text-xs rounded">OB</span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">Services</div>
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Score Breakdown
                    </h4>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                      {Object.entries(hospital.score_breakdown).map(([key, value]) => (
                        <div key={key} className="text-center">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {value.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500 capitalize">
                            {key.replace('_', ' ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => window.location.href = `/facility/${hospital.facility_id}`}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => window.location.href = `/booking?facility=${hospital.facility_id}`}
                      className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900 transition-colors"
                    >
                      Book Appointment
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          <button
            onClick={() => setStep('input')}
            className="w-full py-3 border border-gray-300 rounded-lg hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
          >
            Start New Assessment
          </button>
        </motion.div>
      )}
    </div>
  );
}