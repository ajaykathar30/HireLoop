import React, { useEffect, useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { 
  Plus, 
  Search, 
  MapPin, 
  Briefcase, 
  Eye,
  ChevronRight
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { jobApi } from "../lib/api";
import toast from 'react-hot-toast';

const CompanyJobs = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await jobApi.getCompanyJobs();
      setJobs(response.data);
    } catch (err) {
      toast.error("Failed to fetch jobs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-16 border-b-4 border-black pb-10">
          <div>
            <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter">Manage Jobs</h1>
            <p className="text-black font-bold uppercase tracking-widest text-xs opacity-40 mt-2">Active listings and pipeline status</p>
          </div>
          <button 
            className="h-16 px-10 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-sm rounded-full flex items-center gap-3 hover:bg-black transition-all"
            onClick={() => navigate("/company/jobs/create")}
          >
            <Plus size={20} />
            Post New Job
          </button>
        </div>

        <div className="neo-brutal bg-white rounded-[2rem] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-black text-white uppercase tracking-widest text-[10px] font-black border-b-2 border-black">
                  <th className="px-8 py-6">Role Title</th>
                  <th className="px-6 py-6">Type</th>
                  <th className="px-6 py-6">Location</th>
                  <th className="px-6 py-6">Status</th>
                  <th className="px-6 py-6 text-right pr-8">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-black/5">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-8 py-20 text-center font-bold text-black/40 uppercase tracking-widest">
                      Loading your listings...
                    </td>
                  </tr>
                ) : jobs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-8 py-20 text-center">
                      <div className="flex flex-col items-center gap-6">
                         <div className="h-20 w-20 rounded-full bg-black/5 flex items-center justify-center">
                           <Briefcase size={32} className="opacity-20" />
                         </div>
                         <p className="font-black uppercase tracking-widest text-black/40">No jobs posted yet</p>
                         <button 
                            className="neo-pill bg-secondary text-black text-xs px-8"
                            onClick={() => navigate("/company/jobs/create")}
                         >
                            Create First Listing
                         </button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.id} className="group hover:bg-black/5 transition-colors">
                      <td className="px-8 py-8">
                        <div>
                          <p className="font-black text-xl uppercase tracking-tight group-hover:text-primary transition-colors">{job.title}</p>
                          <p className="text-[10px] font-bold text-black/40 uppercase tracking-widest mt-1">ID: {job.id.substring(0, 8)}</p>
                        </div>
                      </td>
                      <td className="px-6 py-8">
                        <div className="neo-pill bg-white border-black/10 text-[10px] text-black font-black uppercase tracking-widest inline-block">
                          {job.job_type}
                        </div>
                      </td>
                      <td className="px-6 py-8">
                        <div className="flex items-center gap-2 text-sm font-bold text-black/60 uppercase tracking-tight">
                          <MapPin size={16} />
                          {job.location}
                        </div>
                      </td>
                      <td className="px-6 py-8">
                        <div className={`neo-pill text-[10px] font-black uppercase tracking-widest inline-block ${
                          job.status === 'open' 
                          ? 'bg-accent text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]' 
                          : 'bg-black/5 text-black/40'
                        }`}>
                          {job.status}
                        </div>
                      </td>
                      <td className="px-6 py-8 text-right pr-8">
                        <div className="flex justify-end gap-3">
                          <button 
                            onClick={() => navigate(`/company/jobs/${job.id}/applicants`)}
                            className="h-12 px-6 neo-brutal bg-white text-black font-black uppercase tracking-widest text-[10px] rounded-xl hover:bg-black hover:text-white transition-all flex items-center gap-2"
                          >
                            <Eye size={16} />
                            View Pipeline
                          </button>
                          <button className="h-12 w-12 neo-brutal bg-white flex items-center justify-center hover:bg-primary hover:text-white transition-all rounded-xl">
                            <ChevronRight size={20} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
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

export default CompanyJobs;
