import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { 
  ArrowLeft, 
  Sparkles, 
  ChevronRight,
  TrendingUp,
  Brain,
  Search
} from "lucide-react";
import { applicationApi, jobApi, interviewApi } from "../lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import toast from 'react-hot-toast';

const JobApplicants = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [applicants, setApplicants] = useState([]);
  const [reports, setReports] = useState([]);
  const [filterTop20, setFilterTop20] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const applicantsWithScore = applicants.filter(a => a.fit_score > 0);
  const averageFit = applicantsWithScore.length > 0 
    ? Math.round(applicantsWithScore.reduce((acc, a) => acc + (a.fit_score || 0), 0) / applicantsWithScore.length) 
    : 0;

  useEffect(() => {
    fetchApplicants();
  }, [jobId]);

  const fetchApplicants = async () => {
    try {
      setLoading(true);
      const response = await applicationApi.getJobApplications(jobId);
      let fetchedApplicants = response.data;

      try {
        const reportRes = await interviewApi.getJobReports(jobId);
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
        console.error("Failed to load reports", err);
      }
      
      setApplicants(fetchedApplicants);
    } catch (err) {
      toast.error("Failed to load applicants");
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerPipeline = async () => {
    try {
      await jobApi.triggerPipeline(jobId);
      toast.success("AI Pipeline triggered!");
      setTimeout(fetchApplicants, 2000);
    } catch (err) {
      toast.error("Failed to trigger pipeline");
    }
  };

  const handleViewReport = (appId) => {
    const report = reports.find(r => r.application_id === appId);
    if (report) {
      setSelectedReport(report);
      setIsReportOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
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
                {filterTop20 ? "Showing Top 20" : "Show Top 20"}
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

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="neo-brutal bg-white p-8 rounded-[2rem] flex items-center gap-6">
            <div className="h-16 w-16 rounded-2xl bg-primary border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center">
              <TrendingUp size={24} className="text-white" />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-black/40 mb-1">Average Fit</p>
              <p className="text-3xl font-black">{averageFit}%</p>
            </div>
          </div>
          <div className="neo-brutal bg-white p-8 rounded-[2rem] flex items-center gap-6">
            <div className="h-16 w-16 rounded-2xl bg-secondary border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center">
              <Brain size={24} className="text-black" />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-black/40 mb-1">Screened</p>
              <p className="text-3xl font-black">{applicants.filter(a => a.fit_score > 0).length}</p>
            </div>
          </div>
          <div className="neo-brutal bg-white p-8 rounded-[2rem] flex items-center gap-6">
            <div className="h-16 w-16 rounded-2xl bg-accent border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center">
              <Sparkles size={24} className="text-black" />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-black/40 mb-1">Shortlisted</p>
              <p className="text-3xl font-black">{applicants.filter(a => a.status === 'shortlisted').length}</p>
            </div>
          </div>
        </div>

        {/* Applicants Table */}
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
                      Fetching candidates...
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
                    .filter(app => !filterTop20 || (reports.findIndex(r => r.application_id === app.id) !== -1 && reports.findIndex(r => r.application_id === app.id) < 20))
                    .map((app) => {
                      const reportIdx = reports.findIndex(r => r.application_id === app.id);
                      const appReport = reportIdx !== -1 ? reports[reportIdx] : null;
                      const hasCompletedInterview = appReport && appReport.status === 'completed';
                      const isTop5 = hasCompletedInterview && reportIdx < 5;
                      const isTop20 = hasCompletedInterview && reportIdx >= 5 && reportIdx < 20;

                      return (
                        <tr key={app.id} className={`group hover:bg-black/5 transition-colors ${isTop5 ? 'bg-secondary/10' : isTop20 ? 'bg-primary/5' : ''}`}>
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-4">
                              <div className="h-12 w-12 rounded-xl neo-brutal bg-accent flex items-center justify-center text-lg font-black uppercase">
                                {app.candidate_name?.substring(0, 1)}
                              </div>
                              <div>
                                <p className="font-black text-lg uppercase tracking-tight flex items-center gap-2">
                                  {app.candidate_name}
                                  {isTop5 && <span className="neo-pill bg-secondary text-black text-[9px]">🏆 TOP 5</span>}
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

        {/* Report Dialog */}
        <Dialog open={isReportOpen} onOpenChange={setIsReportOpen}>
          <DialogContent className="max-w-4xl p-0 overflow-hidden neo-brutal rounded-[2rem] bg-white border-4 border-black">
            <DialogHeader className="p-8 bg-primary text-white border-b-4 border-black">
              <DialogTitle className="text-3xl font-black uppercase tracking-tighter flex items-center gap-3">
                <Brain className="fill-white" />
                AI Analysis Report
              </DialogTitle>
              {selectedReport && (
                <p className="text-white/80 font-bold uppercase tracking-widest text-xs mt-2">
                  Candidate: {selectedReport.candidate_name}
                </p>
              )}
            </DialogHeader>
            <div className="p-8 max-h-[70vh] overflow-y-auto">
              {selectedReport && (
                <div className="space-y-8">
                  <div className="neo-brutal bg-secondary p-6 rounded-2xl flex items-center justify-between">
                    <div>
                      <h3 className="font-black uppercase tracking-widest text-xs mb-1">Overall Fitness Score</h3>
                      <p className="text-sm font-bold opacity-70">Based on multi-source data analysis</p>
                    </div>
                    <div className="text-5xl font-black">{selectedReport.total_score || 0}%</div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="font-black text-xl uppercase tracking-tight">Executive Summary</h3>
                    <div className="neo-brutal bg-white p-6 rounded-2xl font-bold leading-relaxed text-black/70">
                      {selectedReport.report_summary}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="font-black text-xl uppercase tracking-tight">Technical Breakdown</h3>
                    <div className="grid grid-cols-1 gap-4">
                      {selectedReport.questions?.map((q, i) => (
                        <div key={i} className="neo-brutal bg-white p-6 rounded-2xl">
                          <div className="flex justify-between items-start gap-4 mb-4">
                            <h4 className="font-black text-sm uppercase leading-tight">{q.question}</h4>
                            <div className="neo-pill bg-accent text-black text-[10px] px-3">{q.score}/20</div>
                          </div>
                          <p className="text-sm font-bold text-black/60 italic mb-4">"{q.answer}"</p>
                          <div className="bg-black/5 p-4 rounded-xl text-xs font-bold leading-relaxed">
                            <span className="text-primary uppercase tracking-widest mb-1 block">AI Feedback:</span>
                            {q.feedback}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </main>
      <Footer />
    </div>
  );
};

export default JobApplicants;
