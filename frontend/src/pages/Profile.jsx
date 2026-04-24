import React, { useEffect, useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  User, 
  Mail, 
  Phone, 
  Linkedin, 
  FileText, 
  Building2, 
  Globe, 
  Pencil,
  Plus,
  ExternalLink,
  MapPin,
  Info
} from "lucide-react";
import { useSelector } from "react-redux";
import { authApi, candidateApi, companyApi } from "../lib/api";
import toast from "react-hot-toast";

const Profile = () => {
  const { user: authUser, role } = useSelector((state) => state.auth);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [open, setOpen] = useState(false);

  // Form State
  const [formData, setFormData] = useState({});
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

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
      toast.success("Profile updated successfully!");
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
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-bold text-muted-foreground animate-pulse uppercase tracking-widest">Loading Profile...</p>
        </div>
      </div>
    );
  }

  // Final check if no profile exists yet
  if (!profile && !loading) {
    return (
        <div className="min-h-screen bg-background">
            <Navbar />
            <div className="flex flex-col items-center justify-center py-32">
                <p className="text-xl font-bold text-muted-foreground">No profile data found.</p>
                <Button onClick={() => setOpen(true)} className="mt-4">Create Profile</Button>
            </div>
            <Footer />
        </div>
    )
  }

  return (
    <div className="min-h-screen bg-background font-sans">
      <Navbar />
      
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {/* Profile Header Card */}
          <div className="bg-card border rounded-[32px] overflow-hidden shadow-sm relative">
            <div className="h-48 bg-gradient-to-r from-primary/20 via-primary/5 to-background w-full" />
            
            <div className="px-8 pb-8">
              <div className="flex flex-col md:flex-row md:items-end justify-between -mt-16 gap-6">
                <div className="flex flex-col md:flex-row items-end gap-6">
                  <div className="relative group">
                    <Avatar className="h-40 w-40 border-8 border-background rounded-[40px] shadow-xl bg-background">
                      <AvatarImage src={role === 'company' ? profile?.logo_url : ''} className="object-cover" />
                      <AvatarFallback className="bg-primary text-primary-foreground text-5xl font-black rounded-[32px]">
                        {role === 'company' ? profile?.name?.[0] : profile?.full_name?.[0]}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  
                  <div className="mb-2 space-y-1">
                    <div className="flex items-center gap-3">
                      <h1 className="text-4xl font-black tracking-tight">
                        {role === 'company' ? (profile?.name || "Company Name") : (profile?.full_name || "User Name")}
                      </h1>
                      <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border border-primary/20">
                        {role || 'user'}
                      </div>
                    </div>
                    <p className="text-muted-foreground font-bold flex items-center gap-2 text-lg">
                      <Mail size={18} className="text-primary/60" />
                      {authUser?.email}
                    </p>
                    {role === 'company' && profile?.industry && (
                      <p className="text-sm font-bold text-primary flex items-center gap-2">
                        <Building2 size={16} />
                        {profile.industry}
                      </p>
                    )}
                  </div>
                </div>
                
                <Dialog open={open} onOpenChange={setOpen}>
                  <DialogTrigger asChild>
                    <Button size="lg" className="font-bold shadow-lg shadow-primary/20 h-12 px-8 rounded-2xl">
                      <Pencil size={18} className="mr-2" />
                      Edit Profile
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[600px] rounded-[32px]">
                    <DialogHeader>
                      <DialogTitle className="text-2xl font-black">Update Your Profile</DialogTitle>
                      <DialogDescription className="font-medium text-muted-foreground">
                        Customize how you appear to others on HireLoop.
                      </DialogDescription>
                    </DialogHeader>
                    
                    <form onSubmit={handleUpdate} className="space-y-6 py-4">
                      {role === 'candidate' ? (
                        <div className="grid gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="full_name" className="font-bold">Full Name</Label>
                            <Input id="full_name" className="h-11 rounded-xl" value={formData.full_name || ''} onChange={(e) => setFormData({...formData, full_name: e.target.value})} />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="phone" className="font-bold">Phone Number</Label>
                              <Input id="phone" className="h-11 rounded-xl" value={formData.phone || ''} onChange={(e) => setFormData({...formData, phone: e.target.value})} />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="linkedin" className="font-bold">LinkedIn URL</Label>
                              <Input id="linkedin" className="h-11 rounded-xl" value={formData.linkedin_url || ''} onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})} />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="experience" className="font-bold">Experience (Years)</Label>
                              <Input id="experience" type="number" className="h-11 rounded-xl" value={formData.experience_years || ''} onChange={(e) => setFormData({...formData, experience_years: e.target.value})} />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="resume" className="font-bold">Resume (PDF)</Label>
                              <Input id="resume" type="file" accept=".pdf" className="h-11 rounded-xl pt-2" onChange={(e) => setFile(e.target.files[0])} />
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="grid gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="name" className="font-bold">Company Name</Label>
                            <Input id="name" className="h-11 rounded-xl" value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="industry" className="font-bold">Industry</Label>
                              <Input id="industry" className="h-11 rounded-xl" value={formData.industry || ''} onChange={(e) => setFormData({...formData, industry: e.target.value})} />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="website" className="font-bold">Website</Label>
                              <Input id="website" className="h-11 rounded-xl" value={formData.website || ''} onChange={(e) => setFormData({...formData, website: e.target.value})} />
                            </div>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="description" className="font-bold">Company Description</Label>
                            <Textarea id="description" className="min-h-[100px] rounded-xl" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="logo" className="font-bold">Company Logo</Label>
                            <Input id="logo" type="file" accept="image/*" className="h-11 rounded-xl pt-2" onChange={(e) => setFile(e.target.files[0])} />
                          </div>
                        </div>
                      )}
                      
                      <DialogFooter className="pt-4">
                        <Button type="submit" disabled={updating} className="w-full h-12 font-bold text-lg rounded-xl">
                          {updating ? (
                            <div className="flex items-center gap-2">
                              <div className="h-4 w-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
                              Saving...
                            </div>
                          ) : "Save Profile Changes"}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              {/* About Section */}
              <section className="bg-card border rounded-[32px] p-8 shadow-sm">
                <h3 className="text-xl font-black mb-6 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
                    <Info size={20} />
                  </div>
                  {role === 'company' ? 'About Our Company' : 'Professional Summary'}
                </h3>
                <div className="text-muted-foreground font-medium leading-relaxed text-lg whitespace-pre-wrap">
                  {role === 'company' 
                    ? (profile?.description || "No description provided yet. Let candidates know what your company is all about by clicking the edit button.")
                    : (profile?.resume_text ? (profile.resume_text.substring(0, 500) + "...") : "Upload your resume to see your parsed profile summary here.")
                  }
                </div>
              </section>

              {/* Statistics/Impact Section */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="bg-emerald-500/5 border border-emerald-500/20 p-6 rounded-3xl text-center">
                  <p className="text-3xl font-black text-emerald-600 mb-1">
                    {role === 'company' ? '24' : '12'}
                  </p>
                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-600/70">
                    {role === 'company' ? 'Active Jobs' : 'Applications'}
                  </p>
                </div>
                <div className="bg-blue-500/5 border border-blue-500/20 p-6 rounded-3xl text-center">
                  <p className="text-3xl font-black text-blue-600 mb-1">
                    {role === 'company' ? '1.2k' : '98%'}
                  </p>
                  <p className="text-xs font-bold uppercase tracking-wider text-blue-600/70">
                    {role === 'company' ? 'Applications' : 'Profile Match'}
                  </p>
                </div>
                <div className="bg-purple-500/5 border border-purple-500/20 p-6 rounded-3xl text-center">
                  <p className="text-3xl font-black text-purple-600 mb-1">
                    {role === 'company' ? '5.0' : '4'}
                  </p>
                  <p className="text-xs font-bold uppercase tracking-wider text-purple-600/70">
                    {role === 'company' ? 'Rating' : 'Offers'}
                  </p>
                </div>
              </div>
            </div>

            {/* Sidebar Details */}
            <aside className="space-y-8">
              <section className="bg-card border rounded-[32px] p-8 shadow-sm">
                <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-6 pb-2 border-b">
                  Contact Details
                </h3>
                <div className="space-y-6">
                  {role === 'company' ? (
                    <>
                      <div className="flex items-start gap-4">
                        <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                          <Globe size={18} />
                        </div>
                        <div className="overflow-hidden">
                          <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Website</p>
                          <a href={profile?.website} target="_blank" rel="noopener noreferrer" className="text-sm font-bold text-primary hover:underline flex items-center gap-1">
                            {profile?.website?.replace(/^https?:\/\//, '') || "Not set"}
                            <ExternalLink size={12} />
                          </a>
                        </div>
                      </div>
                      <div className="flex items-start gap-4">
                        <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                          <Building2 size={18} />
                        </div>
                        <div>
                          <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Industry</p>
                          <p className="text-sm font-bold">{profile?.industry || "Not specified"}</p>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex items-start gap-4">
                        <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                          <Phone size={18} />
                        </div>
                        <div>
                          <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Phone</p>
                          <p className="text-sm font-bold">{profile?.phone || "Not set"}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-4">
                        <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                          <Linkedin size={18} />
                        </div>
                        <div className="overflow-hidden">
                          <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">LinkedIn</p>
                          <a href={profile?.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-sm font-bold text-primary hover:underline truncate block">
                            {profile?.linkedin_url || "Not set"}
                          </a>
                        </div>
                      </div>
                    </>
                  )}
                  <div className="flex items-start gap-4">
                    <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                      <MapPin size={18} />
                    </div>
                    <div>
                      <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Location</p>
                      <p className="text-sm font-bold">Global / Remote</p>
                    </div>
                  </div>
                </div>
              </section>

              {role === 'candidate' && (
                <section className="bg-card border rounded-[32px] p-8 shadow-sm">
                  <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-6 pb-2 border-b">
                    Technical Assets
                  </h3>
                  <div className="bg-muted/30 border border-dashed rounded-2xl p-6 flex flex-col items-center text-center gap-4">
                    {profile?.resume_url ? (
                      <>
                        <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                          <FileText size={24} />
                        </div>
                        <div>
                          <p className="text-sm font-bold">Resume Uploaded</p>
                          <a href={profile.resume_url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-primary hover:underline font-black uppercase tracking-widest mt-1 block">View PDF</a>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="h-12 w-12 rounded-xl bg-muted flex items-center justify-center text-muted-foreground">
                          <Plus size={24} />
                        </div>
                        <p className="text-sm font-bold text-muted-foreground italic">Add your resume</p>
                      </>
                    )}
                  </div>
                </section>
              )}
            </aside>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Profile;
