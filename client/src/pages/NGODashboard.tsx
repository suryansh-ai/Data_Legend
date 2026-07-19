import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { Building2, MapPin, AlertTriangle, ShieldCheck, Activity, BarChart, ChevronRight, CheckCircle2, TrendingUp, Info } from 'lucide-react';

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
  const navigate = useNavigate();
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
      const response = await api.get<DashboardData>('/ngo/dashboard');
      // Wait, is response.data wrapped inside a data key? Yes, /api/ngo/dashboard wraps response in {"status": "success", "data": ...}
      // Let's verify what api.get('/ngo/dashboard') returns.
      // In backend server/routes/ngo.py:
      // return { "status": "success", "data": { "overview": ..., "state_stats": ... } }
      // The frontend client api.ts fetch client returns the raw JSON.
      // So `response` is the parsed JSON dict: { "status": "success", "data": { "overview": ... } }
      // So `response.data` contains the overview/state_stats!
      // This means response.data is correct!
      setDashboardData((response as any).data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadResourceGaps = async () => {
    try {
      const params = selectedState ? `?state=${selectedState}` : '';
      const response = await api.get<{ data: { resource_gaps: Record<string, ResourceGap> } }>(`/ngo/resource-gaps${params}`);
      setResourceGaps(Object.values(response.data.resource_gaps));
    } catch (err: any) {
      console.error('Failed to load resource gaps:', err);
    }
  };

  const loadInterventions = async () => {
    try {
      const params = selectedState ? `?state=${selectedState}` : '';
      const response = await api.get<{ data: { interventions: Intervention[] } }>(`/ngo/intervention-plan${params}`);
      setInterventions(response.data.interventions || []);
    } catch (err: any) {
      console.error('Failed to load interventions:', err);
    }
  };

  const handleExportReport = () => {
    let headers: string[] = [];
    let rows: any[][] = [];
    let filename = 'gap_analysis_report.csv';

    if (activeTab === 'gaps') {
      headers = ['Department Capability', 'Hospitals with Capability', 'Total Audited Hospitals', 'Coverage Percentage', 'Deficit Severity', 'Policy Recommendation'];
      rows = resourceGaps.map(g => [
        g.capability,
        g.facilities_with,
        g.total_facilities,
        g.coverage_pct.toFixed(1) + '%',
        g.severity.toUpperCase(),
        g.recommendation
      ]);
      filename = `${selectedState || 'national'}_resource_gaps_report.csv`;
    } else if (activeTab === 'interventions') {
      headers = ['Priority', 'Target Specialty Capability', 'Current Coverage %', 'Target Coverage %', 'Additional Beds/Facilities Needed', 'Deployment Advice', 'Projected Impact'];
      rows = interventions.map(i => [
        i.priority.toUpperCase(),
        i.capability,
        i.current_coverage.toFixed(1) + '%',
        i.target_coverage.toFixed(1) + '%',
        i.facilities_needed,
        i.recommendation,
        i.impact
      ]);
      filename = `${selectedState || 'national'}_intervention_plan_report.csv`;
    } else {
      headers = ['Metric / Indicator', 'Value / Percentage', 'Context / Details'];
      rows = [
        ['Total audited locations', dashboardData?.overview.total_facilities || 0, 'Clinics cataloged in target region'],
        ['Districts monitored', dashboardData?.overview.total_districts || 0, 'Unique NFHS-5 mapped districts'],
        ['States covered', dashboardData?.overview.states_covered || 0, 'Monitored administrative areas'],
        ['Institutional Births Avg %', (dashboardData?.district_summary?.avg_institutional_births || 0) + '%', 'NFHS-5 delivery statistics'],
        ['ANC 4+ visits Avg %', (dashboardData?.district_summary?.avg_anc_visits || 0) + '%', 'NFHS-5 antenatal indicators'],
        ['Insurance Coverage %', (dashboardData?.district_summary?.avg_health_insurance || 0) + '%', 'NFHS-5 healthcare coverage policies'],
        ['District Electricity %', (dashboardData?.district_summary?.avg_electricity || 0) + '%', 'Infrastructure availability']
      ];
      filename = `${selectedState || 'national'}_overview_metrics_report.csv`;
    }

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getSeverityMeta = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          label: 'Critical Shortage',
          color: 'text-red-700 bg-red-50 dark:bg-red-950/20 dark:text-red-400 border-red-200/40',
          barColor: 'bg-red-500',
        };
      case 'high':
        return {
          label: 'High Gap',
          color: 'text-amber-700 bg-amber-50 dark:bg-amber-950/20 dark:text-amber-400 border-amber-200/40',
          barColor: 'bg-amber-500',
        };
      case 'medium':
        return {
          label: 'Moderate Shortage',
          color: 'text-yellow-700 bg-yellow-50 dark:bg-yellow-950/20 dark:text-yellow-400 border-yellow-200/40',
          barColor: 'bg-yellow-500',
        };
      default:
        return {
          label: 'Adequate Coverage',
          color: 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/20 dark:text-emerald-400 border-emerald-200/40',
          barColor: 'bg-emerald-500',
        };
    }
  };

  const getPriorityMeta = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-950/40 dark:text-red-400';
      case 'medium':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400';
      default:
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-400';
    }
  };

  if (loading) return <div className="flex items-center justify-center min-h-[300px]"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-700"></div></div>;

  if (error) {
    return (
      <div className="card p-6 border-red-200 bg-red-50 text-red-800 space-y-4">
        <h2 className="text-lg font-bold">Error Loading Dashboard</h2>
        <p className="text-xs">{error}</p>
        <button onClick={loadDashboardData} className="btn-primary">Retry</button>
      </div>
    );
  }

  const criticalGapsCount = dashboardData
    ? Object.values(dashboardData.capability_gaps).filter(g => g.status === 'critical').length
    : 0;

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            NGO Coverage Planner
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Identify medical deserts, audit resource shortfalls, and deploy targeted interventions.
          </p>
        </div>

        {/* State Filter & Exporter */}
        <div className="flex items-center gap-3">
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="input py-1.5 text-xs w-auto border-slate-200 font-bold"
          >
            <option value="">National Overview</option>
            {dashboardData && Object.keys(dashboardData.state_stats || {}).map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
          <button
            onClick={handleExportReport}
            className="btn-secondary py-1.5 px-4 text-xs font-bold flex items-center gap-1.5"
            title="Download CSV Report"
          >
            <span>📥 Export CSV</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex rounded-xl border p-1 bg-slate-100 dark:bg-slate-800 overflow-x-auto scrollbar-thin" style={{ borderColor: 'var(--border-color)' }}>
        {[
          { id: 'overview', label: 'Overview Metrics' },
          { id: 'gaps', label: `Resource Gaps (${resourceGaps.length})` },
          { id: 'interventions', label: `Intervention Plans (${interventions.length})` },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 min-w-[120px] text-center px-4 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && dashboardData && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="card p-5 space-y-1">
              <span className="text-3xl font-extrabold text-teal-700 dark:text-teal-400">
                {dashboardData.overview.total_facilities.toLocaleString()}
              </span>
              <p className="text-xs font-bold text-slate-800 dark:text-slate-200">Total Clinics</p>
              <p className="text-[10px] text-slate-400">Tracked in registry</p>
            </div>
            <div className="card p-5 space-y-1">
              <span className="text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
                {dashboardData.overview.total_districts}
              </span>
              <p className="text-xs font-bold text-slate-800 dark:text-slate-200">Districts</p>
              <p className="text-[10px] text-slate-400">Audited health codes</p>
            </div>
            <div className="card p-5 space-y-1">
              <span className="text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
                {dashboardData.overview.states_covered}
              </span>
              <p className="text-xs font-bold text-slate-800 dark:text-slate-200">States Covered</p>
              <p className="text-[10px] text-slate-400">Active regional desks</p>
            </div>
            <div className="card p-5 space-y-1 border-red-200 bg-red-50/20">
              <span className="text-3xl font-extrabold text-red-600">
                {criticalGapsCount}
              </span>
              <p className="text-xs font-bold text-red-800 dark:text-red-400">Critical Gaps</p>
              <p className="text-[10px] text-red-500">Departments needing beds</p>
            </div>
          </div>

          {/* NFHS-5 Health Indicators */}
          {dashboardData.district_summary && (
            <div className="card p-6 space-y-4">
              <div>
                <h3 className="font-bold text-sm uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
                  📊 National Health Indicators (NFHS-5)
                </h3>
                <p className="text-[10px] text-slate-400">Cross-compared regional public health metrics.</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { value: `${dashboardData.district_summary.avg_institutional_births}%`, label: 'Institutional Births', color: 'bg-teal-50 text-teal-700 border-teal-100' },
                  { value: `${dashboardData.district_summary.avg_anc_visits}%`, label: 'ANC 4+ Checkups', color: 'bg-emerald-50 text-emerald-700 border-emerald-100' },
                  { value: `${dashboardData.district_summary.avg_health_insurance}%`, label: 'Insurance Cover', color: 'bg-sky-50 text-sky-700 border-sky-100' },
                  { value: `${dashboardData.district_summary.avg_electricity}%`, label: 'Power Availability', color: 'bg-amber-50 text-amber-700 border-amber-100' },
                ].map((item, idx) => (
                  <div key={idx} className={`p-4 rounded-xl border text-center ${item.color}`}>
                    <span className="text-2xl font-black block">{item.value}</span>
                    <span className="text-[10px] font-bold block mt-1 uppercase tracking-wider">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Capability Coverage Bar Gaps */}
          <div className="card p-6 space-y-4">
            <h3 className="font-bold text-sm uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
              🩺 Medical Specialty Gaps
            </h3>
            <div className="space-y-4">
              {Object.entries(dashboardData.capability_gaps)
                .sort(([, a], [, b]) => a.coverage_pct - b.coverage_pct)
                .slice(0, 8)
                .map(([capability, data]) => (
                  <div key={capability} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-bold">
                    <span className="capitalize w-32" style={{ color: 'var(--text-primary)' }}>{capability}</span>
                    <div className="flex-1 flex items-center gap-3 w-full">
                      <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full flex-1 overflow-hidden">
                        <div
                          className={`h-2 rounded-full ${
                            data.status === 'critical' ? 'bg-red-500' :
                            data.status === 'low' ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(100, data.coverage_pct)}%` }}
                        />
                      </div>
                      <span className="w-12 text-right" style={{ color: 'var(--text-secondary)' }}>{data.coverage_pct}%</span>
                    </div>
                    <span className="text-[10px] text-slate-400 w-24 text-right">{data.count} clinics</span>
                  </div>
                ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Resource Gaps Tab */}
      {activeTab === 'gaps' && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-6 sm:grid-cols-2"
        >
          {resourceGaps.length === 0 ? (
            <div className="card p-8 text-center col-span-2">
              <p className="text-xs text-slate-500">No gap analytics compiled.</p>
            </div>
          ) : (
            resourceGaps
              .sort((a, b) => a.coverage_pct - b.coverage_pct)
              .map((gap) => {
                const meta = getSeverityMeta(gap.severity)
                return (
                  <motion.div
                    key={gap.capability}
                    className="card p-5 flex flex-col justify-between"
                  >
                    <div className="space-y-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-extrabold text-base capitalize" style={{ color: 'var(--text-primary)' }}>
                            {gap.capability} Services
                          </h3>
                          <p className="text-xs font-semibold text-slate-400 mt-0.5">
                            {gap.facilities_with} of {gap.total_facilities} clinics equipped
                          </p>
                        </div>
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider ${meta.color}`}>
                          {meta.label}
                        </span>
                      </div>

                      {/* Bar Gauge */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          <span>Coverage Density</span>
                          <span>{gap.coverage_pct}%</span>
                        </div>
                        <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${meta.barColor}`} style={{ width: `${Math.min(100, gap.coverage_pct)}%` }} />
                        </div>
                      </div>
                    </div>

                    <div className="mt-6 pt-3 border-t text-xs leading-relaxed" style={{ borderColor: 'var(--border-color)', color: 'var(--text-secondary)' }}>
                      <strong>Action Plan:</strong> {gap.recommendation}
                    </div>
                  </motion.div>
                )
              })
          )}
        </motion.div>
      )}

      {/* Interventions Tab */}
      {activeTab === 'interventions' && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {interventions.length === 0 ? (
            <div className="card p-8 text-center">
              <p className="text-xs text-slate-500">No active intervention policies needed.</p>
            </div>
          ) : (
            interventions.map((intervention, idx) => (
              <motion.div
                key={`${intervention.capability}-${idx}`}
                className="card p-6 flex flex-col md:flex-row justify-between gap-6"
              >
                <div className="space-y-4 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-extrabold text-base capitalize" style={{ color: 'var(--text-primary)' }}>
                      Fix {intervention.capability.replace('_', ' ')}
                    </h3>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${getPriorityMeta(intervention.priority)}`}>
                      {intervention.priority} Priority
                    </span>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400">
                      {intervention.impact} Impact
                    </span>
                  </div>

                  <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                    <strong>Intervention Policy:</strong> {intervention.recommendation}
                  </p>

                  {/* Actions */}
                  <div className="flex flex-wrap gap-2 pt-2">
                    <button
                      onClick={() => navigate(`/trust-desk?capability=${intervention.capability}`)}
                      className="btn-primary py-1.5 px-4 text-xs font-bold"
                    >
                      View Clinics
                    </button>
                    <button
                      onClick={() => navigate(`/medical-desert`)}
                      className="btn-secondary py-1.5 px-4 text-xs font-bold"
                    >
                      Desert Map Analysis
                    </button>
                  </div>
                </div>

                {/* Progress Gauges Grid */}
                <div className="grid grid-cols-2 gap-3 min-w-[240px]">
                  <div className="p-3 rounded-xl border bg-slate-50 dark:bg-slate-900 text-center" style={{ borderColor: 'var(--border-color)' }}>
                    <span className="text-base font-black text-slate-800 dark:text-slate-100">{intervention.current_coverage}%</span>
                    <span className="text-[9px] block text-slate-400 font-bold uppercase tracking-wider mt-0.5">Current Cover</span>
                  </div>
                  <div className="p-3 rounded-xl border bg-slate-50 dark:bg-slate-900 text-center" style={{ borderColor: 'var(--border-color)' }}>
                    <span className="text-base font-black text-teal-700 dark:text-teal-400">{intervention.target_coverage}%</span>
                    <span className="text-[9px] block text-slate-400 font-bold uppercase tracking-wider mt-0.5">Target Cover</span>
                  </div>
                  <div className="p-3 rounded-xl border bg-slate-50 dark:bg-slate-900 text-center" style={{ borderColor: 'var(--border-color)' }}>
                    <span className="text-base font-black text-red-600">{intervention.facilities_needed}</span>
                    <span className="text-[9px] block text-slate-400 font-bold uppercase tracking-wider mt-0.5">Clinics Needed</span>
                  </div>
                  <div className="p-3 rounded-xl border bg-emerald-50 dark:bg-emerald-950/20 text-center border-emerald-100 dark:border-emerald-900/30">
                    <span className="text-base font-black text-emerald-700 dark:text-emerald-400">+{intervention.target_coverage - intervention.current_coverage}%</span>
                    <span className="text-[9px] block text-emerald-600 dark:text-emerald-500 font-bold uppercase tracking-wider mt-0.5">Target Gap</span>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </motion.div>
      )}
    </div>
  );
}