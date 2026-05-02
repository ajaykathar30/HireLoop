import React, { useState, useEffect } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { 
  Search, 
  MapPin, 
  Briefcase, 
  Sparkles, 
  TrendingUp,
  Clock,
  Building2,
  DollarSign,
  Bookmark,
  ChevronRight,
  Filter,
  FileText
} from "lucide-react";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { jobApi, applicationApi, interviewApi } from "../lib/api";
import toast from 'react-hot-toast';

const formatRelativeTime = (date) => {
  if (!date) return "Recently";
  const now = new Date();
  const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
  if (diffInSeconds < 60) return "just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  return new Date(date).toLocaleDateString();
};

const CandidateHome = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ applications: 0, interviews: 0 });
  const [sessions, setSessions] = useState([]);
  const [activeTab, setActiveTab] = useState("recommended");
  const [selectedJob, setSelectedJob] = useState(null);
  const [coverNote, setCoverNote] = useState("");
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchStats();
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await interviewApi.getMySessions();
      setSessions(res.data || []);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  const fetchStats = async () => {
    try {
      const [appRes, intRes] = await Promise.all([
        applicationApi.getMyApplications(),
        interviewApi.getMySessions()
      ]);
      setStats({
        applications: appRes.data?.length || 0,
        interviews: intRes.data?.length || 0
      });
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await jobApi.getAllJobs();
      setJobs(response.data);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
      toast.error("Could not load jobs");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!selectedJob) return;
    setApplying(true);
    try {
      await applicationApi.apply({
        job_id: selectedJob.id,
        cover_note: coverNote
      });
      toast.success(`Successfully applied!`);
      setSelectedJob(null);
      setCoverNote("");
      fetchStats();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Application failed");
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-12 mb-16 border-b-4 border-black pb-12">
          <div className="space-y-6">
            <div className="neo-pill bg-primary text-white text-[10px] uppercase tracking-widest inline-flex items-center gap-2">
              <Sparkles size={12} className="fill-white" />
              AI Matching is active
            </div>
            <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-[0.9]">
              Your next <span className="text-primary underline decoration-8 underline-offset-8">big move</span> <br />
              starts here.
            </h1>
            <p className="text-black font-bold text-xl max-w-xl opacity-70">
              Analyzed your profile and found <span className="bg-secondary px-2">{jobs.length} roles</span> that match your unique skills.
            </p>
          </div>
          
          <div className="flex gap-6">
            <div className="neo-brutal bg-white p-6 rounded-2xl text-center min-w-[120px]">
              <p className="text-4xl font-black">{stats.applications}</p>
              <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Applied</p>
            </div>
            <div className="neo-brutal bg-accent p-6 rounded-2xl text-center min-w-[120px]">
              <p className="text-4xl font-black">{stats.interviews}</p>
              <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Interviews</p>
            </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="neo-brutal bg-white p-6 rounded-3xl grid grid-cols-1 md:grid-cols-12 gap-4 mb-20">
          <div className="md:col-span-5 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-black/40" size={20} />
            <input 
              placeholder="Search roles, skills..." 
              className="w-full h-14 pl-12 pr-4 bg-black/5 rounded-2xl border-2 border-transparent focus:border-black focus:bg-white outline-none font-bold transition-all"
            />
          </div>
          <div className="md:col-span-4 relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-black/40" size={20} />
            <input 
              placeholder="City or Remote" 
              className="w-full h-14 pl-12 pr-4 bg-black/5 rounded-2xl border-2 border-transparent focus:border-black focus:bg-white outline-none font-bold transition-all"
            />
          </div>
          <div className="md:col-span-3 flex gap-3">
            <button className="h-14 px-6 neo-brutal bg-white flex items-center justify-center rounded-2xl">
              <Filter size={20} />
            </button>
            <button className="flex-1 h-14 neo-brutal bg-black text-white font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-primary transition-all">
              Search
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
          {/* Main Feed */}
          <div className="lg:col-span-8 space-y-10">
            <div className="flex items-center gap-8 border-b-2 border-black/10">
              <button 
                onClick={() => setActiveTab("recommended")}
                className={`pb-4 text-sm font-black uppercase tracking-widest transition-all ${activeTab === 'recommended' ? 'border-b-4 border-black text-black' : 'text-black/20 hover:text-black'}`}
              >
                Recommended
              </button>
              <button 
                onClick={() => setActiveTab("interviews")}
                className={`pb-4 text-sm font-black uppercase tracking-widest transition-all flex items-center gap-2 ${activeTab === 'interviews' ? 'border-b-4 border-black text-black' : 'text-black/20 hover:text-black'}`}
              >
                My Interviews
                {sessions.length > 0 && (
                  <span className="neo-pill bg-accent text-black text-[9px] px-2 py-0.5">{sessions.length}</span>
                )}
              </button>
            </div>

            <div className="space-y-8">
              {loading ? (
                [1,2,3].map(i => (
                  <div key={i} className="h-48 neo-brutal bg-black/5 animate-pulse rounded-3xl" />
                ))
              ) : activeTab === "recommended" ? (
                jobs.map((job) => (
                  <div key={job.id} className="neo-brutal bg-white rounded-3xl overflow-hidden group hover:-translate-y-2 transition-all duration-300">
                    <div className="p-8">
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex gap-6">
                          <div className="h-16 w-16 rounded-2xl neo-brutal bg-accent flex items-center justify-center text-2xl font-black uppercase">
                            {job.company_name?.substring(0, 1)}
                          </div>
                          <div>
                            <h3 className="text-2xl font-black uppercase tracking-tight mb-1 group-hover:text-primary transition-colors">{job.title}</h3>
                            <div className="flex items-center gap-4 text-sm font-bold text-black/40">
                              <span className="flex items-center gap-1.5"><Building2 size={16} /> {job.company_name}</span>
                              <span className="flex items-center gap-1.5"><MapPin size={16} /> {job.location || "Remote"}</span>
                            </div>
                          </div>
                        </div>
                        <div className="neo-pill bg-secondary text-black text-[10px] uppercase tracking-widest">98% Match</div>
                      </div>
                      
                      <div className="flex items-center gap-6 text-xs font-black uppercase tracking-widest text-black/40 mb-8">
                        <span className="flex items-center gap-2"><Briefcase size={16} /> {job.job_type}</span>
                        <span className="flex items-center gap-2"><DollarSign size={16} /> {job.salary_min && job.salary_max ? `$${job.salary_min/1000}k - $${job.salary_max/1000}k` : "Salary Undisclosed"}</span>
                        <span className="flex items-center gap-2"><Clock size={16} /> {formatRelativeTime(job.created_at)}</span>
                      </div>

                      <div className="flex items-center justify-between pt-8 border-t-2 border-black/5">
                        <button className="flex items-center gap-2 text-black/40 font-black uppercase tracking-widest text-[10px] hover:text-black transition-colors">
                          <Bookmark size={16} /> Save for later
                        </button>
                        <button 
                          onClick={() => setSelectedJob(job)}
                          className="h-12 px-8 neo-brutal bg-black text-white font-black uppercase tracking-widest text-xs rounded-xl hover:bg-primary transition-all"
                        >
                          Apply Now
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                /* Interviews Tab Content */
                sessions.length === 0 ? (
                  <div className="text-center py-20 bg-black/5 rounded-[3rem] border-4 border-dashed border-black/10">
                    <Sparkles size={48} className="mx-auto mb-4 text-black/10" />
                    <p className="font-black uppercase tracking-widest text-black/30">No active interviews yet.</p>
                    <p className="text-xs font-bold text-black/20 mt-2">Keep applying! AI screening is fast.</p>
                  </div>
                ) : (
                  sessions.map((session) => (
                    <div key={session.id} className="neo-brutal bg-white rounded-3xl overflow-hidden border-2 border-black">
                      <div className="p-8">
                        <div className="flex justify-between items-center mb-6">
                          <div className="flex items-center gap-4">
                            <div className="h-14 w-14 rounded-xl bg-accent border-2 border-black flex items-center justify-center font-black uppercase">
                              {session.company_name?.substring(0, 1)}
                            </div>
                            <div>
                              <h3 className="text-xl font-black uppercase tracking-tight">{session.job_title}</h3>
                              <p className="text-xs font-black uppercase tracking-widest text-black/40">{session.company_name}</p>
                            </div>
                          </div>
                          <div className={`neo-pill text-[9px] uppercase font-black px-3 ${session.status === 'completed' ? 'bg-primary text-white' : 'bg-secondary text-black'}`}>
                            {session.status}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-8">
                          <div className="bg-black/5 p-4 rounded-2xl">
                            <p className="text-[10px] font-black uppercase tracking-widest text-black/40 mb-1">Deadline</p>
                            <p className="text-sm font-bold">{new Date(session.deadline_at).toLocaleDateString()}</p>
                          </div>
                          <div className="bg-black/5 p-4 rounded-2xl">
                            <p className="text-[10px] font-black uppercase tracking-widest text-black/40 mb-1">Phase</p>
                            <p className="text-sm font-bold uppercase">Voice Screening</p>
                          </div>
                        </div>

                        {session.status !== 'completed' ? (
                          <button 
                            onClick={() => window.location.href = `/interview/${session.id}`}
                            className="w-full h-14 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-xs rounded-2xl hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center justify-center gap-2"
                          >
                            <Sparkles size={16} className="fill-white" />
                            Start AI Voice Interview
                          </button>
                        ) : (
                          <div className="w-full h-14 bg-black/5 rounded-2xl flex items-center justify-center font-black uppercase tracking-widest text-xs text-black/30 gap-2">
                            Interview Completed
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-8">
            <div className="neo-brutal bg-secondary p-8 rounded-3xl">
              <h3 className="text-xl font-black uppercase tracking-tight mb-6 flex items-center gap-3">
                <TrendingUp size={24} /> Career Growth
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-xs font-black uppercase mb-2 tracking-widest">
                    <span>Profile Strength</span>
                    <span>85%</span>
                  </div>
                  <div className="h-4 neo-brutal bg-white rounded-full overflow-hidden p-0.5">
                    <div className="h-full bg-primary rounded-full" style={{ width: '85%' }} />
                  </div>
                </div>
                <div className="pt-6 border-t-2 border-black/10">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-black/40 mb-4">Recommended Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {["Next.js", "Docker", "System Design"].map(s => (
                      <span key={s} className="neo-pill bg-white text-black text-[9px] uppercase tracking-widest">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Application Dialog */}
      <Dialog open={!!selectedJob} onOpenChange={(open) => !open && setSelectedJob(null)}>
        <DialogContent className="max-w-xl p-0 overflow-hidden neo-brutal rounded-[2rem] bg-white border-4 border-black">
          <DialogHeader className="p-8 bg-black text-white border-b-4 border-black">
            <DialogTitle className="text-3xl font-black uppercase tracking-tighter">Submit Application</DialogTitle>
            <DialogDescription className="text-white/60 font-bold uppercase tracking-widest text-xs mt-2">
              Applying for {selectedJob?.title} @ {selectedJob?.company_name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="p-8 space-y-8">
            <div className="neo-brutal bg-accent p-6 rounded-2xl flex items-start gap-4">
              <div className="mt-1 bg-black p-2 rounded-xl text-white">
                <FileText size={20} />
              </div>
              <div>
                <p className="font-black uppercase tracking-tight">Profile is Ready</p>
                <p className="text-xs font-bold opacity-60">We'll use your analyzed AI resume for this submission.</p>
              </div>
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Cover Note (Optional)</label>
              <textarea 
                placeholder="Why are you a great fit?"
                className="w-full min-h-[160px] p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all"
                value={coverNote}
                onChange={(e) => setCoverNote(e.target.value)}
              />
            </div>

            <div className="flex gap-4 pt-4">
              <button 
                onClick={() => setSelectedJob(null)}
                className="flex-1 h-14 neo-brutal bg-white text-black font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-black/5"
              >
                Cancel
              </button>
              <button 
                onClick={handleApply} 
                disabled={applying}
                className="flex-[2] h-14 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-xs rounded-2xl hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                {applying ? "Sending..." : "Submit Application"}
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
};

export default CandidateHome;
