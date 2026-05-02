import React, { useEffect, useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { 
  User, 
  Mail, 
  Linkedin, 
  Building2, 
  Globe, 
  Pencil,
  MapPin,
  Info,
  Briefcase,
  Play,
  Clock,
  CheckCircle2,
  X,
  Upload
} from "lucide-react";
import { useSelector } from "react-redux";
import { authApi, candidateApi, companyApi, applicationApi, interviewApi } from "../lib/api";
import { useNavigate } from 'react-router-dom';
import toast from "react-hot-toast";

const Profile = () => {
  const navigate = useNavigate();
  const { user: authUser, role } = useSelector((state) => state.auth);
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Form State
  const [formData, setFormData] = useState({});
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetchProfile();
    if (role === 'candidate') {
        fetchApplications();
    }
  }, [role]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await authApi.getMe();
      const profileData = response.data.profile || {};
      setProfile(profileData);
      setFormData(profileData);
    } catch (err) {
      console.error(err);
      toast.error("Failed to fetch profile details");
    } finally {
      setLoading(false);
    }
  };

  const fetchApplications = async () => {
    try {
      const response = await applicationApi.getMyApplications();
      setApplications(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartInterview = async (appId) => {
    try {
        const response = await interviewApi.getSessionByAppId(appId);
        const session = response.data;
        navigate(`/interview/${session.id}`);
    } catch (err) {
        toast.error("Interview session not ready yet. Please wait.");
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setUpdating(true);
    try {
      if (role === 'candidate') {
        const updateData = { ...formData };
        if (file) updateData.resume_file = file;
        await candidateApi.updateProfile(updateData);
      } else {
        const updatePayload = {
          name: formData.name,
          industry: formData.industry,
          website: formData.website,
          description: formData.description,
          logo_file: file
        };
        await companyApi.updateProfile(updatePayload);
      }
      toast.success("Profile updated!");
      await fetchProfile();
      setOpen(false);
      setFile(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Update failed");
    } finally {
      setUpdating(false);
    }
  };

  if (loading && !profile) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white">
        <div className="h-16 w-16 border-8 border-black border-t-primary rounded-full animate-spin mb-6" />
        <p className="text-xl font-black uppercase tracking-tighter animate-pulse">Loading Profile...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white font-sans">
      <Navbar />
      
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="space-y-12">
          {/* Header */}
          <div className="neo-brutal bg-white rounded-[3rem] overflow-hidden">
            <div className="h-40 bg-primary/10 border-b-4 border-black" />
            <div className="px-10 pb-10">
               <div className="flex flex-col md:flex-row md:items-end justify-between -mt-16 gap-8">
                  <div className="flex flex-col md:flex-row items-end gap-8">
                    <div className="h-40 w-40 neo-brutal bg-white rounded-[2.5rem] border-4 border-black overflow-hidden flex items-center justify-center shadow-xl">
                       {profile?.logo_url ? (
                         <img src={profile.logo_url} className="w-full h-full object-cover" />
                       ) : (
                         <span className="text-6xl font-black text-primary">
                           {role === 'company' ? profile?.name?.[0] : profile?.full_name?.[0]}
                         </span>
                       )}
                    </div>
                    <div className="mb-2">
                       <div className="flex items-center gap-4">
                          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter leading-none">
                            {role === 'company' ? (profile?.name || "Company") : (profile?.full_name || "User")}
                          </h1>
                          <div className="neo-pill bg-black text-white text-[10px] font-black uppercase tracking-widest px-4">
                            {role}
                          </div>
                       </div>
                       <p className="text-black/40 font-bold uppercase tracking-widest text-xs mt-4 flex items-center gap-2">
                          <Mail size={16} /> {authUser?.email}
                       </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => setOpen(true)}
                    className="h-14 px-8 neo-brutal bg-secondary text-black font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-black hover:text-white transition-all flex items-center gap-2"
                  >
                    <Pencil size={18} /> Edit Profile
                  </button>
               </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex gap-4 border-b-4 border-black pb-1">
             <button 
               onClick={() => setActiveTab('overview')}
               className={`px-8 py-4 font-black uppercase tracking-widest text-sm transition-all ${activeTab === 'overview' ? 'border-b-8 border-primary text-primary' : 'text-black/40 hover:text-black'}`}
             >
               Overview
             </button>
             {role === 'candidate' && (
               <button 
                 onClick={() => setActiveTab('applications')}
                 className={`px-8 py-4 font-black uppercase tracking-widest text-sm transition-all ${activeTab === 'applications' ? 'border-b-8 border-primary text-primary' : 'text-black/40 hover:text-black'}`}
               >
                 My Applications
               </button>
             )}
          </div>

          {/* Content */}
          <div className="pt-8">
             {activeTab === 'overview' ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                   <div className="lg:col-span-2 space-y-10">
                      <section className="neo-brutal bg-white p-10 rounded-[2.5rem]">
                         <div className="flex items-center gap-4 border-b-4 border-black pb-6 mb-8">
                            <div className="h-10 w-10 bg-accent rounded-xl neo-brutal flex items-center justify-center">
                               <Info size={20} />
                            </div>
                            <h3 className="text-xl font-black uppercase tracking-tight">
                              {role === 'company' ? 'About Our Company' : 'Professional Summary'}
                            </h3>
                         </div>
                         <p className="text-black/60 font-bold leading-relaxed text-lg whitespace-pre-wrap">
                            {role === 'company' 
                                ? (profile?.description || "No description provided.")
                                : (profile?.resume_text ? (profile.resume_text.substring(0, 600) + "...") : "Upload your resume to generate your summary.")
                            }
                         </p>
                      </section>
                   </div>

                   <div className="space-y-10">
                      <section className="neo-brutal bg-white p-8 rounded-[2.5rem]">
                         <h3 className="text-[10px] font-black uppercase tracking-widest text-black/40 mb-8 border-b-2 border-black/5 pb-4">Profile Details</h3>
                         <div className="space-y-8">
                            {role === 'company' ? (
                               <div className="flex items-center gap-4">
                                  <div className="h-12 w-12 bg-black/5 rounded-2xl flex items-center justify-center text-black/40">
                                     <Globe size={20} />
                                  </div>
                                  <div>
                                     <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Website</p>
                                     <p className="text-sm font-black uppercase tracking-tight text-primary underline">{profile?.website || "Not set"}</p>
                                  </div>
                               </div>
                            ) : (
                               <div className="flex items-center gap-4">
                                  <div className="h-12 w-12 bg-black/5 rounded-2xl flex items-center justify-center text-black/40">
                                     <Briefcase size={20} />
                                  </div>
                                  <div>
                                     <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Experience</p>
                                     <p className="text-sm font-black uppercase tracking-tight">{profile?.experience_years || 0} Years</p>
                                  </div>
                               </div>
                            )}
                            <div className="flex items-center gap-4">
                               <div className="h-12 w-12 bg-black/5 rounded-2xl flex items-center justify-center text-black/40">
                                  <MapPin size={20} />
                               </div>
                               <div>
                                  <p className="text-[10px] font-black uppercase tracking-widest text-black/40">Location</p>
                                  <p className="text-sm font-black uppercase tracking-tight">Mumbai, India</p>
                               </div>
                            </div>
                         </div>
                      </section>
                   </div>
                </div>
             ) : (
                <div className="space-y-8">
                   {applications.length === 0 ? (
                      <div className="py-24 text-center neo-brutal bg-black/5 rounded-[3rem] border-4 border-dashed border-black/10">
                         <p className="text-black/40 font-black uppercase tracking-widest text-sm italic">No applications found.</p>
                         <button onClick={() => navigate('/candidate-home')} className="mt-6 neo-pill bg-primary text-white text-xs px-8">Browse Jobs</button>
                      </div>
                   ) : (
                      <div className="grid gap-6">
                         {applications.map((app) => (
                            <div key={app.id} className="neo-brutal bg-white p-8 rounded-[2rem] hover:bg-black/5 transition-all">
                               <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                                  <div className="flex items-center gap-6">
                                     <div className="h-16 w-16 neo-brutal bg-white rounded-2xl flex items-center justify-center text-primary border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] font-black text-2xl">
                                        {app.company_name?.substring(0,1).toUpperCase()}
                                     </div>
                                     <div>
                                        <h4 className="font-black text-2xl uppercase tracking-tighter leading-none">{app.job_title}</h4>
                                        <div className="flex items-center gap-4 text-black/40 text-[10px] font-black uppercase tracking-widest mt-2">
                                           <div className="flex items-center gap-1.5"><Building2 size={12} /> {app.company_name}</div>
                                           <div className="flex items-center gap-1.5"><Clock size={12} /> {new Date(app.applied_at).toLocaleDateString()}</div>
                                        </div>
                                     </div>
                                  </div>

                                  <div className="flex items-center gap-6">
                                     <div className={`neo-pill text-[10px] font-black uppercase tracking-widest px-6 ${
                                         app.status === 'shortlisted' ? 'bg-accent text-black border-2 border-black' :
                                         app.status === 'rejected' ? 'bg-black/5 text-black/20 border-2 border-black/5' :
                                         'bg-black/5 text-black/60 border-2 border-black/5'
                                     }`}>
                                        {app.status}
                                     </div>

                                     {app.status === 'shortlisted' && (
                                        <button 
                                            className="h-14 px-8 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-xs rounded-xl hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center gap-2 animate-pulse hover:animate-none"
                                            onClick={() => handleStartInterview(app.id)}
                                        >
                                            <Play size={16} fill="white" /> Start AI Interview
                                        </button>
                                     )}

                                     {app.status === 'interviewed' && (
                                        <div className="flex items-center gap-2 text-accent font-black uppercase tracking-widest text-xs">
                                           <CheckCircle2 size={20} className="fill-black text-accent" /> Done
                                        </div>
                                     )}
                                  </div>
                               </div>
                            </div>
                         ))}
                      </div>
                   )}
                </div>
             )}
          </div>
        </div>
      </main>

      {/* Modal Edit */}
      {open && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
           <div className="w-full max-w-2xl neo-brutal bg-white rounded-[3rem] p-10 relative max-h-[90vh] overflow-y-auto">
              <button onClick={() => setOpen(false)} className="absolute top-8 right-8 text-black/40 hover:text-black">
                 <X size={24} />
              </button>
              <div className="mb-10">
                 <h2 className="text-4xl font-black uppercase tracking-tighter">Update Profile</h2>
                 <p className="text-black/40 font-bold uppercase tracking-widest text-xs mt-2">Customize your identity</p>
              </div>

              <form onSubmit={handleUpdate} className="space-y-8">
                 {role === 'candidate' ? (
                   <div className="space-y-6">
                      <div className="space-y-3">
                         <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Full Name</label>
                         <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.full_name || ''} onChange={(e) => setFormData({...formData, full_name: e.target.value})} />
                      </div>
                      <div className="grid grid-cols-2 gap-6">
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Phone</label>
                            <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.phone || ''} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
                         </div>
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">LinkedIn URL</label>
                            <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.linkedin_url || ''} onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})} />
                         </div>
                      </div>
                      <div className="grid grid-cols-2 gap-6">
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Experience (Years)</label>
                            <input type="number" className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.experience_years || ''} onChange={(e) => setFormData({...formData, experience_years: e.target.value})} />
                         </div>
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Update Resume</label>
                            <div className="relative">
                               <input type="file" accept=".pdf" className="hidden" id="resume-upload" onChange={(e) => setFile(e.target.files[0])} />
                               <label htmlFor="resume-upload" className="w-full h-16 neo-brutal bg-white rounded-2xl flex items-center justify-center gap-2 cursor-pointer font-black uppercase tracking-widest text-[10px] hover:bg-black/5">
                                  <Upload size={16} /> {file ? file.name.substring(0,15) + '...' : "Upload PDF"}
                               </label>
                            </div>
                         </div>
                      </div>
                   </div>
                 ) : (
                   <div className="space-y-6">
                      <div className="space-y-3">
                         <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Company Name</label>
                         <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} />
                      </div>
                      <div className="grid grid-cols-2 gap-6">
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Industry</label>
                            <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.industry || ''} onChange={(e) => setFormData({...formData, industry: e.target.value})} />
                         </div>
                         <div className="space-y-3">
                            <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Website</label>
                            <input className="w-full h-16 p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.website || ''} onChange={(e) => setFormData({...formData, website: e.target.value})} />
                         </div>
                      </div>
                      <div className="space-y-3">
                         <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Description</label>
                         <textarea className="w-full min-h-[120px] p-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                      </div>
                   </div>
                 )}

                 <button type="submit" disabled={updating} className="w-full h-16 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-sm rounded-2xl mt-4">
                    {updating ? "Saving..." : "Save Profile Changes"}
                 </button>
              </form>
           </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default Profile;
