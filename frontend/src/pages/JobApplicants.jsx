import React, { useEffect, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import {
  ArrowLeft,
  Sparkles,
  ChevronRight,
  TrendingUp,
  Brain,
  X,
} from 'lucide-react';
import { applicationApi, jobApi, interviewApi } from '../lib/api';
import toast from 'react-hot-toast';

/* ─────────────────────────────────────────────────────────────
   FULL-SCREEN REPORT MODAL — built as a raw portal so shadcn
   sm:max-w-sm can never constrain it.
───────────────────────────────────────────────────────────── */
const ReportModal = ({ report, onClose }) => {
  /* Close on Escape */
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  /* Helpers */
  const pctColor  = (p) => p >= 70 ? 'text-green-600' : p >= 40 ? 'text-purple-600' : 'text-red-500';
  const barColor  = (p) => p >= 70 ? 'bg-accent'       : p >= 40 ? 'bg-primary'      : 'bg-red-400';
  const badgeColor= (p) => p >= 70 ? 'bg-accent text-black' : p >= 40 ? 'bg-secondary text-black' : 'bg-red-100 text-red-700';
  const label     = (p) => p >= 70 ? 'Strong Match'    : p >= 40 ? 'Moderate'        : 'Low Match';
  const gaugeClr  = (p) => p >= 70 ? '#c8f356'         : p >= 40 ? '#c4b5fd'         : '#f87171';

  return createPortal(
    /* Backdrop */
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Modal box */}
      <div
        className="relative flex flex-col bg-white border-4 border-black rounded-[2rem] overflow-hidden"
        style={{
          width: 'min(900px, 95vw)',
          maxHeight: '92vh',
          boxShadow: '10px 10px 0px 0px rgba(0,0,0,1)',
        }}
      >
        {/* ── STICKY HEADER ─────────────────────────────────── */}
        <div className="flex-shrink-0 bg-black text-white px-8 py-7 border-b-4 border-black">
          <div className="flex items-start justify-between gap-4">
            {/* Title + candidate */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <Brain className="fill-white flex-shrink-0" size={24} />
                <h2 className="text-2xl font-black uppercase tracking-tighter leading-none">
                  AI Analysis Report
                </h2>
              </div>
              <p className="text-white/50 font-bold uppercase tracking-widest text-[11px] mt-2">
                Candidate:{' '}
                <span className="text-white">{report.candidate_name}</span>
              </p>
            </div>

            {/* Score badges + close */}
            <div className="flex items-start gap-3 flex-shrink-0">
              <div className="text-center bg-white/10 rounded-2xl px-4 py-3 border border-white/20">
                <p className="text-white/50 text-[9px] font-black uppercase tracking-widest mb-1">Fit Score</p>
                <p className="text-3xl font-black text-accent leading-none">{report.fit_score || 0}%</p>
              </div>
              {report.status === 'completed' && (
                <div className="text-center bg-white/10 rounded-2xl px-4 py-3 border border-white/20">
                  <p className="text-white/50 text-[9px] font-black uppercase tracking-widest mb-1">Interview</p>
                  <p className="text-3xl font-black text-secondary leading-none">{report.total_score || 0}%</p>
                </div>
              )}
              <button
                onClick={onClose}
                className="h-10 w-10 rounded-xl bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
              >
                <X size={20} className="text-white" />
              </button>
            </div>
          </div>
        </div>

        {/* ── SCROLLABLE BODY ───────────────────────────────── */}
        <div className="flex-1 overflow-y-auto px-8 py-8 space-y-12">

          {/* ─ Phase 1: AI Screening ─ */}
          <section className="space-y-6">
            <div className="flex items-center gap-3 border-b-2 border-black pb-4">
              <div className="h-9 w-9 rounded-xl bg-accent border-2 border-black flex items-center justify-center font-black text-sm"
                style={{ boxShadow: '2px 2px 0 #000' }}>
                1
              </div>
              <h3 className="font-black text-xl uppercase tracking-tight">AI Screening</h3>
              <span className="rounded-full bg-accent text-black text-[9px] uppercase font-black px-3 py-1 border border-black">
                Completed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Radial gauge */}
              <div className="border-2 border-black rounded-2xl p-6 flex flex-col items-center gap-4"
                style={{ boxShadow: '4px 4px 0 #000' }}>
                <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Fit Score</p>
                <div className="relative h-28 w-28">
                  <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="14" fill="none" stroke="#e5e5e5" strokeWidth="4" />
                    <circle cx="18" cy="18" r="14" fill="none"
                      stroke={gaugeClr(report.fit_score || 0)}
                      strokeWidth="4"
                      strokeDasharray={`${(report.fit_score || 0) * 0.88} 88`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-black">{report.fit_score || 0}</span>
                  </div>
                </div>
                <p className={`text-xs font-black uppercase tracking-wide ${pctColor(report.fit_score || 0)}`}>
                  {label(report.fit_score || 0)}
                </p>
              </div>

              {/* Reasoning */}
              <div className="md:col-span-2 border-2 border-black rounded-2xl p-6 space-y-3"
                style={{ boxShadow: '4px 4px 0 #000' }}>
                <p className="text-[10px] font-black uppercase tracking-widest text-black/40">AI Reasoning</p>
                <p className="font-semibold text-sm leading-relaxed text-black/70 bg-black/[0.04] p-4 rounded-xl border border-black/10">
                  {report.fit_reasoning || 'Screening reasoning not available.'}
                </p>
              </div>
            </div>
          </section>

          {/* ─ Phase 2: Voice Interview ─ */}
          <section className="space-y-6">
            <div className="flex items-center gap-3 border-b-2 border-black pb-4">
              <div className="h-9 w-9 rounded-xl bg-primary border-2 border-black flex items-center justify-center font-black text-sm text-white"
                style={{ boxShadow: '2px 2px 0 #000' }}>
                2
              </div>
              <h3 className="font-black text-xl uppercase tracking-tight">Voice Interview</h3>
              <span
                className={`rounded-full text-[9px] uppercase font-black px-3 py-1 border border-black ${
                  report.status === 'completed' ? 'bg-primary text-white' : 'bg-black/10 text-black'
                }`}
              >
                {report.status || 'Pending'}
              </span>
            </div>

            {report.status === 'completed' ? (
              <div className="space-y-8">

                {/* Overall score + summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="border-2 border-black rounded-2xl p-6 flex flex-col items-center justify-center gap-2 text-center"
                    style={{ background: 'var(--secondary, #e9e0ff)', boxShadow: '4px 4px 0 #000' }}>
                    <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Overall Performance</p>
                    <p className="text-5xl font-black leading-none">{report.total_score || 0}%</p>
                    <p className="text-xs font-bold text-black/50 uppercase">Avg. Interview Score</p>
                  </div>
                  <div className="md:col-span-2 border-2 border-black rounded-2xl p-6 space-y-3"
                    style={{ boxShadow: '4px 4px 0 #000' }}>
                    <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Executive Summary</p>
                    <p className="font-semibold text-sm leading-relaxed text-black/70">
                      {report.report_summary}
                    </p>
                  </div>
                </div>

                {/* Per-question breakdown */}
                <div className="space-y-5">
                  <h4 className="font-black text-sm uppercase tracking-widest text-black/40">
                    Technical Breakdown — All Questions
                  </h4>

                  {report.questions?.map((q, i) => {
                    const pct = Math.round((q.score / 20) * 100);
                    return (
                      <div key={i}
                        className="border-2 border-black rounded-2xl overflow-hidden"
                        style={{ boxShadow: '4px 4px 0 #000' }}>

                        {/* Question row */}
                        <div className="flex items-center justify-between gap-4 px-6 py-5 border-b-2 border-black/8 bg-black/[0.02]">
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <div className="h-8 w-8 flex-shrink-0 rounded-lg bg-black flex items-center justify-center text-white font-black text-xs">
                              Q{i + 1}
                            </div>
                            <p className="font-black text-sm uppercase leading-snug">{q.question}</p>
                          </div>
                          <div className={`flex-shrink-0 text-sm font-black px-4 py-1 rounded-full border-2 border-black ${badgeColor(pct)}`}
                            style={{ boxShadow: '2px 2px 0 #000' }}>
                            {q.score}/20
                          </div>
                        </div>

                        {/* Score bar */}
                        <div className="px-6 pt-4">
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-2.5 bg-black/8 rounded-full overflow-hidden">
                              <div className={`h-full rounded-full ${barColor(pct)}`}
                                style={{ width: `${pct}%`, transition: 'width 0.8s ease' }} />
                            </div>
                            <span className={`text-xs font-black min-w-[2.5rem] text-right ${pctColor(pct)}`}>
                              {pct}%
                            </span>
                          </div>
                        </div>

                        {/* Answer + feedback */}
                        <div className="px-6 pb-6 pt-4 space-y-3">
                          <div className="bg-black/[0.04] rounded-xl p-4 border border-black/8">
                            <p className="text-[10px] font-black uppercase tracking-widest text-black/30 mb-2">
                              Candidate's Answer
                            </p>
                            <p className="text-sm font-semibold text-black/60 italic leading-relaxed">
                              "{q.answer}"
                            </p>
                          </div>
                          <div className="rounded-xl p-4 border border-purple-200"
                            style={{ background: 'rgba(110,86,207,0.05)' }}>
                            <p className="text-[10px] font-black uppercase tracking-widest text-purple-600 mb-2">
                              AI Evaluator Feedback
                            </p>
                            <p className="text-sm font-semibold leading-relaxed text-black/70">
                              {q.feedback}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-black/20 rounded-[2rem] p-16 text-center bg-black/[0.03]">
                <Brain size={56} className="mx-auto mb-5 text-black/20" />
                <p className="font-black uppercase tracking-widest text-base text-black/40">
                  Interview results pending
                </p>
                <p className="text-sm font-semibold text-black/30 mt-2">
                  The candidate has not completed the voice interview yet.
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>,
    document.body
  );
};


/* ══════════════════════════════════════════════════════════════
   MAIN PAGE
══════════════════════════════════════════════════════════════ */
const JobApplicants = () => {
  const { jobId }   = useParams();
  const navigate    = useNavigate();
  const [applicants,      setApplicants]      = useState([]);
  const [reports,         setReports]         = useState([]);
  const [filterTop20,     setFilterTop20]     = useState(false);
  const [selectedReport,  setSelectedReport]  = useState(null);
  const [loading,         setLoading]         = useState(true);

  const applicantsWithScore = applicants.filter(a => a.fit_score > 0);
  const averageFit =
    applicantsWithScore.length > 0
      ? Math.round(
          applicantsWithScore.reduce((acc, a) => acc + (a.fit_score || 0), 0) /
            applicantsWithScore.length
        )
      : 0;

  useEffect(() => { fetchApplicants(); }, [jobId]);

  const fetchApplicants = async () => {
    try {
      setLoading(true);
      const response = await applicationApi.getJobApplications(jobId);
      let fetchedApplicants = response.data;

      try {
        const reportRes    = await interviewApi.getJobReports(jobId);
        const fetchedReports = reportRes.data.reports || [];
        setReports(fetchedReports);

        fetchedApplicants.sort((a, b) => {
          const idxA = fetchedReports.findIndex(r => r.application_id === a.id);
          const idxB = fetchedReports.findIndex(r => r.application_id === b.id);
          if (idxA !== -1 && idxB !== -1) return idxA - idxB;
          if (idxA !== -1) return -1;
          if (idxB !== -1) return 1;
          return (b.fit_score || 0) - (a.fit_score || 0);
        });
      } catch (err) {
        console.error('Failed to load reports', err);
      }

      setApplicants(fetchedApplicants);
    } catch (err) {
      toast.error('Failed to load applicants');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerPipeline = async () => {
    try {
      await jobApi.triggerPipeline(jobId);
      toast.success('AI Pipeline triggered!');
      setTimeout(fetchApplicants, 2000);
    } catch (err) {
      toast.error('Failed to trigger pipeline');
    }
  };

  const handleViewReport = (appId) => {
    const report = reports.find(r => r.application_id === appId);
    if (report) setSelectedReport(report);
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      {/* Full-screen portal modal */}
      {selectedReport && (
        <ReportModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 border-b-4 border-black pb-10">
          <div>
            <button
              onClick={() => navigate('/company/jobs')}
              className="flex items-center gap-2 text-black/40 font-black uppercase tracking-widest text-xs mb-4 hover:text-black transition-colors"
            >
              <ArrowLeft size={14} /> Back to Jobs
            </button>
            <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter flex items-center gap-4">
              Applicants
              <div className="neo-pill bg-secondary text-black text-xs px-4">
                {applicants.length} Total
              </div>
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              className={`neo-pill text-xs uppercase tracking-widest h-12 px-8 ${filterTop20 ? 'bg-primary text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-white text-black'}`}
              onClick={() => setFilterTop20(!filterTop20)}
            >
              {filterTop20 ? 'Showing Top 20' : 'Show Top 20'}
            </button>
            <button
              className="neo-brutal bg-accent text-black h-12 px-8 rounded-full font-black uppercase tracking-widest text-xs flex items-center gap-2"
              onClick={handleTriggerPipeline}
              disabled={loading}
            >
              <Sparkles size={14} className="fill-current" />
              Trigger AI Screening
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {[
            { icon: <TrendingUp size={24} className="text-white" />, bg: 'bg-primary', label: 'Average Fit',  value: `${averageFit}%` },
            { icon: <Brain size={24} className="text-black" />,       bg: 'bg-secondary', label: 'Screened',  value: applicants.filter(a => a.fit_score > 0).length },
            { icon: <Sparkles size={24} className="text-black" />,    bg: 'bg-accent',    label: 'Shortlisted', value: applicants.filter(a => a.status === 'shortlisted').length },
          ].map((s, i) => (
            <div key={i} className="neo-brutal bg-white p-8 rounded-[2rem] flex items-center gap-6">
              <div className={`h-16 w-16 rounded-2xl ${s.bg} border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center`}>
                {s.icon}
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-widest text-black/40 mb-1">{s.label}</p>
                <p className="text-3xl font-black">{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Table */}
        <div className="neo-brutal bg-white rounded-[2rem] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-black text-white uppercase tracking-widest text-xs font-black">
                  <th className="px-8 py-6">Candidate</th>
                  <th className="px-6 py-6">AI Fit Score</th>
                  <th className="px-6 py-6">Status</th>
                  <th className="px-6 py-6 text-right pr-8">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black/5">
                {loading ? (
                  <tr>
                    <td colSpan={4} className="px-8 py-20 text-center font-bold text-black/40 uppercase tracking-widest">
                      Fetching candidates…
                    </td>
                  </tr>
                ) : applicants.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-8 py-20 text-center font-bold text-black/40 uppercase tracking-widest">
                      No candidates found.
                    </td>
                  </tr>
                ) : (
                  applicants
                    .filter(app =>
                      !filterTop20 ||
                      (reports.findIndex(r => r.application_id === app.id) !== -1 &&
                       reports.findIndex(r => r.application_id === app.id) < 20)
                    )
                    .map((app) => {
                      const reportIdx    = reports.findIndex(r => r.application_id === app.id);
                      const appReport    = reportIdx !== -1 ? reports[reportIdx] : null;
                      const hasCompleted = appReport && appReport.status === 'completed';
                      const isTop5       = hasCompleted && reportIdx < 5;
                      const isTop20      = hasCompleted && reportIdx >= 5 && reportIdx < 20;

                      return (
                        <tr
                          key={app.id}
                          className={`group hover:bg-black/5 transition-colors ${isTop5 ? 'bg-secondary/10' : isTop20 ? 'bg-primary/5' : ''}`}
                        >
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-4">
                              <div className="h-12 w-12 rounded-xl neo-brutal bg-accent flex items-center justify-center text-lg font-black uppercase">
                                {app.candidate_name?.substring(0, 1)}
                              </div>
                              <div>
                                <p className="font-black text-lg uppercase tracking-tight flex items-center gap-2">
                                  {app.candidate_name}
                                  {isTop5  && <span className="neo-pill bg-secondary text-black text-[9px]">🏆 TOP 5</span>}
                                  {isTop20 && <span className="neo-pill bg-primary text-white text-[9px]">🚀 TOP 20</span>}
                                </p>
                                <p className="text-[10px] font-bold text-black/40 uppercase tracking-widest">
                                  Applied {new Date(app.applied_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-6">
                            <div className="flex items-center gap-3">
                              <div className="w-24 h-3 neo-brutal bg-white rounded-full overflow-hidden">
                                <div
                                  className={`h-full transition-all duration-1000 ${app.fit_score >= 80 ? 'bg-accent' : app.fit_score >= 50 ? 'bg-secondary' : 'bg-destructive'}`}
                                  style={{ width: `${app.fit_score || 0}%` }}
                                />
                              </div>
                              <span className="font-black text-sm">{app.fit_score || 0}%</span>
                            </div>
                          </td>
                          <td className="px-6 py-6">
                            <div className="neo-pill bg-white border-black/10 text-[10px] text-black/60 uppercase tracking-widest inline-block">
                              {app.status}
                            </div>
                          </td>
                          <td className="px-6 py-6 text-right pr-8">
                            <div className="flex items-center justify-end gap-3">
                              {appReport && (
                                <button
                                  onClick={() => handleViewReport(app.id)}
                                  className="neo-pill bg-black text-white text-[10px] uppercase tracking-widest hover:bg-primary transition-all"
                                >
                                  Report
                                </button>
                              )}
                              <button className="h-10 w-10 neo-brutal bg-white flex items-center justify-center hover:bg-accent transition-all rounded-xl">
                                <ChevronRight size={18} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                )}
              </tbody>
            </table>
          </div>
        </div>

      </main>
      <Footer />
    </div>
  );
};

export default JobApplicants;
