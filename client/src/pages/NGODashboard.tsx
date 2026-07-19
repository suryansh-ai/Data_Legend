/**
 * NGO Dashboard Page — Healthcare gap analysis and resource mapping.
 * Shows district-level health data, capability gaps, and intervention plans.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';

interface DashboardData {
  overview: {
    total_facilities: number;
    total_districts: number;
    states_covered: number;
  };
  state_stats: Record<string, {
    total: number;
    avg_trust: number;
    low_trust_count: number;
  }>;
  district_summary: {
    total_districts: number;
    avg_institutional_births: number;
    avg_anc_visits: number;
    avg_health_insurance: number;
    avg_electricity: number;
  };
  capability_gaps: Record<string, {
    count: number;
    coverage_pct: number;
    status: string;
  }>;
}

interface ResourceGap {
  capability: string;
  facilities_with: number;
  total_facilities: number;
  coverage_pct: number;
  severity: string;
  recommendation: string;
}

interface Intervention {
  priority: string;
  capability: string;
  current_coverage: number;
  target_coverage: number;
  facilities_needed: number;
  recommendation: string;
  impact: string;
}

export function NGODashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [resourceGaps, setResourceGaps] = useState<ResourceGap[]>([]);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [selectedState, setSelectedState] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'gaps' | 'interventions'>('overview');

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    loadResourceGaps();
    loadInterventions();
  }, [selectedState]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/ngo/dashboard');
      setDashboardData(response.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadResourceGaps = async () => {
    try {
      const params = selectedState ? `?state=${selectedState}` : '';
      const response = await api.get(`/ngo/resource-gaps${params}`);
      setResourceGaps(Object.values(response.data.resource_gaps));
    } catch (err: any) {
      console.error('Failed to load resource gaps:', err);
    }
  };

  const loadInterventions = async () => {
    try {
      const params = selectedState ? `?state=${selectedState}` : '';
      const response = await api.get(`/ngo/intervention-plan${params}`);
      setInterventions(response.data.interventions || []);
    } catch (err: any) {
      console.error('Failed to load interventions:', err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-red-800 dark:text-red-200 mb-2">
            Error Loading Dashboard
          </h2>
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          NGO Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Healthcare gap analysis and resource mapping for underserved regions
        </p>
      </motion.div>

      {/* State Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Filter by State
        </label>
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="w-full md:w-64 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="">All States</option>
          {Object.keys(dashboardData?.state_stats || {}).map(state => (
            <option key={state} value={state}>{state}</option>
          ))}
        </select>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-6 py-2 rounded-lg transition-colors ${
            activeTab === 'overview'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('gaps')}
          className={`px-6 py-2 rounded-lg transition-colors ${
            activeTab === 'gaps'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          Resource Gaps ({resourceGaps.length})
        </button>
        <button
          onClick={() => setActiveTab('interventions')}
          className={`px-6 py-2 rounded-lg transition-colors ${
            activeTab === 'interventions'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          Intervention Plan ({interventions.length})
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && dashboardData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                Total Facilities
              </h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {dashboardData.overview.total_facilities.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                Districts Covered
              </h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {dashboardData.overview.total_districts}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                States Covered
              </h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {dashboardData.overview.states_covered}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                Critical Gaps
              </h3>
              <p className="text-3xl font-bold text-red-600">
                {Object.values(dashboardData.capability_gaps).filter(g => g.status === 'critical').length}
              </p>
            </div>
          </div>

          {/* District Health Summary */}
          {dashboardData.district_summary && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                District Health Indicators (NFHS-5)
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {dashboardData.district_summary.avg_institutional_births}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Institutional Births
                  </div>
                </div>
                <div className="text-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {dashboardData.district_summary.avg_anc_visits}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    ANC 4+ Visits
                  </div>
                </div>
                <div className="text-center p-4 bg-purple-50 dark:bg-purple-900 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {dashboardData.district_summary.avg_health_insurance}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Health Insurance
                  </div>
                </div>
                <div className="text-center p-4 bg-orange-50 dark:bg-orange-900 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {dashboardData.district_summary.avg_electricity}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Electricity Access
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Capability Gaps */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              Capability Gaps
            </h3>
            <div className="space-y-3">
              {Object.entries(dashboardData.capability_gaps)
                .sort(([, a], [, b]) => a.coverage_pct - b.coverage_pct)
                .slice(0, 10)
                .map(([capability, data]) => (
                  <div key={capability} className="flex items-center gap-4">
                    <div className="w-32 text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                      {capability}
                    </div>
                    <div className="flex-1">
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                        <div
                          className={`h-2 rounded-full ${
                            data.status === 'critical' ? 'bg-red-500' :
                            data.status === 'low' ? 'bg-orange-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(100, data.coverage_pct)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="w-20 text-right text-sm text-gray-600 dark:text-gray-400">
                      {data.coverage_pct}%
                    </div>
                    <div className="w-16 text-right text-sm text-gray-500 dark:text-gray-400">
                      {data.count} facilities
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Resource Gaps Tab */}
      {activeTab === 'gaps' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {resourceGaps.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                No resource gap data available.
              </p>
            </div>
          ) : (
            resourceGaps
              .sort((a, b) => a.coverage_pct - b.coverage_pct)
              .map((gap, idx) => (
                <motion.div
                  key={gap.capability}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                        {gap.capability}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {gap.facilities_with} of {gap.total_facilities} facilities
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(gap.severity)}`}>
                      {gap.severity.toUpperCase()}
                    </span>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                      <span>Coverage</span>
                      <span>{gap.coverage_pct}%</span>
                    </div>
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div
                        className={`h-3 rounded-full ${
                          gap.severity === 'critical' ? 'bg-red-500' :
                          gap.severity === 'high' ? 'bg-orange-500' :
                          gap.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(100, gap.coverage_pct)}%` }}
                      ></div>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    <strong>Recommendation:</strong> {gap.recommendation}
                  </p>
                </motion.div>
              ))
          )}
        </motion.div>
      )}

      {/* Interventions Tab */}
      {activeTab === 'interventions' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {interventions.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                No intervention recommendations available.
              </p>
            </div>
          ) : (
            interventions.map((intervention, idx) => (
              <motion.div
                key={`${intervention.capability}-${idx}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                      {intervention.capability.replace('_', ' ')}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {intervention.recommendation}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(intervention.priority)}`}>
                      {intervention.priority.toUpperCase()} PRIORITY
                    </span>
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      {intervention.impact} IMPACT
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-lg font-semibold text-blue-600">
                      {intervention.current_coverage}%
                    </div>
                    <div className="text-xs text-gray-500">Current Coverage</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-lg font-semibold text-green-600">
                      {intervention.target_coverage}%
                    </div>
                    <div className="text-xs text-gray-500">Target Coverage</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-lg font-semibold text-orange-600">
                      {intervention.facilities_needed}
                    </div>
                    <div className="text-xs text-gray-500">Facilities Needed</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-lg font-semibold text-purple-600">
                      {intervention.target_coverage - intervention.current_coverage}%
                    </div>
                    <div className="text-xs text-gray-500">Coverage Gap</div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => window.location.href = `/trust-desk?capability=${intervention.capability}`}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Facilities
                  </button>
                  <button
                    onClick={() => window.location.href = `/medical-desert`}
                    className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900 transition-colors"
                  >
                    Medical Desert Analysis
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </motion.div>
      )}
    </div>
  );
}