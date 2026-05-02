import React, { useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { 
  ArrowLeft, 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Sparkles,
  Info,
  Calendar
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { jobApi } from "../lib/api";
import toast from "react-hot-toast";

const PostJob = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    job_type: 'Full-time',
    salary_min: '',
    salary_max: '',
    application_deadline: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await jobApi.create({
        title: formData.title,
        description: formData.description,
        requirements: formData.requirements,
        location: formData.location || null,
        job_type: formData.job_type || null,
        salary_min: formData.salary_min ? parseInt(formData.salary_min) : null,
        salary_max: formData.salary_max ? parseInt(formData.salary_max) : null,
        application_deadline: formData.application_deadline ? new Date(formData.application_deadline).toISOString() : null,
      });
      
      toast.success("Job posted successfully!");
      navigate("/company/jobs");
    } catch (err) {
      console.error("Post job error:", err);
      toast.error(err.response?.data?.detail || "Failed to post job. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="mb-12">
          <button 
            onClick={() => navigate("/company/jobs")}
            className="flex items-center gap-2 text-black/40 font-black uppercase tracking-widest text-[10px] hover:text-black transition-colors mb-6"
          >
            <ArrowLeft size={14} />
            Back to Dashboard
          </button>
          <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-none">
            Create a <br />
            <span className="text-primary underline decoration-8 underline-offset-8">New Listing</span>
          </h1>
          <p className="text-black font-bold uppercase tracking-widest text-xs opacity-40 mt-6">Define the role and find your next talent</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-16">
          {/* Section 1 */}
          <div className="neo-brutal bg-white p-10 rounded-[2.5rem] space-y-8">
            <div className="flex items-center gap-4 border-b-4 border-black pb-6">
               <div className="h-12 w-12 rounded-xl bg-accent border-2 border-black flex items-center justify-center">
                 <Briefcase size={24} />
               </div>
               <h2 className="text-2xl font-black uppercase tracking-tight">Core Details</h2>
            </div>
            
            <div className="space-y-6">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Position Title</label>
                <input 
                  required
                  placeholder="e.g. Senior Product Designer"
                  className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-black focus:border-primary transition-all"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Job Type</label>
                  <select 
                    className="w-full h-16 px-6 neo-brutal bg-white rounded-2xl outline-none font-black appearance-none cursor-pointer"
                    value={formData.job_type}
                    onChange={(e) => setFormData({...formData, job_type: e.target.value})}
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
                <div className="space-y-3">
                  <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-6 top-1/2 -translate-y-1/2 text-black/40" size={20} />
                    <input 
                      required
                      placeholder="Remote or City"
                      className="w-full h-16 pl-14 pr-6 neo-brutal bg-white rounded-2xl outline-none font-black focus:border-primary transition-all"
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2 */}
          <div className="neo-brutal bg-secondary/10 p-10 rounded-[2.5rem] space-y-8">
            <div className="flex items-center gap-4 border-b-4 border-black pb-6">
               <div className="h-12 w-12 rounded-xl bg-primary border-2 border-black flex items-center justify-center text-white">
                 <Info size={24} />
               </div>
               <h2 className="text-2xl font-black uppercase tracking-tight">Job Content</h2>
            </div>
            
            <div className="space-y-8">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Role Description</label>
                <textarea 
                  required
                  placeholder="What will they be doing?"
                  className="w-full min-h-[200px] p-6 neo-brutal bg-white rounded-2xl outline-none font-bold leading-relaxed focus:border-primary transition-all"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Requirements</label>
                <textarea 
                  required
                  placeholder="Skills and qualifications needed..."
                  className="w-full min-h-[200px] p-6 neo-brutal bg-white rounded-2xl outline-none font-bold leading-relaxed focus:border-primary transition-all"
                  value={formData.requirements}
                  onChange={(e) => setFormData({...formData, requirements: e.target.value})}
                />
              </div>
            </div>
          </div>

          {/* Section 3 */}
          <div className="neo-brutal bg-white p-10 rounded-[2.5rem] space-y-8">
            <div className="flex items-center gap-4 border-b-4 border-black pb-6">
               <div className="h-12 w-12 rounded-xl bg-accent border-2 border-black flex items-center justify-center">
                 <DollarSign size={24} />
               </div>
               <h2 className="text-2xl font-black uppercase tracking-tight">Budget & Timeline</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Min Salary ($)</label>
                <input 
                  type="number"
                  placeholder="80000"
                  className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-black focus:border-primary transition-all"
                  value={formData.salary_min}
                  onChange={(e) => setFormData({...formData, salary_min: e.target.value})}
                />
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Max Salary ($)</label>
                <input 
                  type="number"
                  placeholder="120000"
                  className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-black focus:border-primary transition-all"
                  value={formData.salary_max}
                  onChange={(e) => setFormData({...formData, salary_max: e.target.value})}
                />
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Deadline</label>
                <input 
                  type="date"
                  className="w-full h-16 px-6 neo-brutal bg-white rounded-2xl outline-none font-black appearance-none"
                  value={formData.application_deadline}
                  onChange={(e) => setFormData({...formData, application_deadline: e.target.value})}
                />
              </div>
            </div>
          </div>

          <div className="flex gap-6 pt-10">
             <button 
                type="button"
                onClick={() => navigate("/company/jobs")}
                className="flex-1 h-16 neo-brutal bg-white text-black font-black uppercase tracking-widest text-sm rounded-2xl hover:bg-black/5"
             >
                Discard
             </button>
             <button 
                type="submit"
                disabled={loading}
                className="flex-[2] h-16 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-sm rounded-2xl hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center justify-center gap-3"
             >
                {loading ? "Publishing..." : "Publish Job Opening"}
                <Sparkles size={20} className="fill-white" />
             </button>
          </div>
        </form>
      </main>

      <Footer />
    </div>
  );
};

export default PostJob;
