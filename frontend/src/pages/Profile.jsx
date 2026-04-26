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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  Info,
  Briefcase,
  Play,
  Clock,
  CheckCircle2
} from "lucide-react";
import { useSelector } from "react-redux";
import { authApi, candidateApi, companyApi, applicationApi, interviewApi } from "../lib/api";
import { useNavigate } from 'react-router-dom';
import toast from "react-hot-toast";
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const Profile = () => {
  const navigate = useNavigate();
  const { user: authUser, role } = useSelector((state) => state.auth);
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [open, setOpen] = useState(false);

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
                  <Avatar className="h-40 w-40 border-8 border-background rounded-[40px] shadow-xl bg-background">
                    <AvatarImage src={role === 'company' ? profile?.logo_url : ''} className="object-cover" />
                    <AvatarFallback className="bg-primary text-primary-foreground text-5xl font-black rounded-[32px]">
                      {role === 'company' ? profile?.name?.[0] : profile?.full_name?.[0]}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="mb-2 space-y-1">
                    <div className="flex items-center gap-3">
                      <h1 className="text-4xl font-black tracking-tight">
                        {role === 'company' ? (profile?.name || "Company Name") : (profile?.full_name || "User Name")}
                      </h1>
                      <Badge className="bg-primary/10 text-primary uppercase text-[10px] font-black tracking-tighter border-primary/20">
                        {role}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground font-bold flex items-center gap-2 text-lg">
                      <Mail size={18} className="text-primary/60" />
                      {authUser?.email}
                    </p>
                  </div>
                </div>
                
                <Dialog open={open} onOpenChange={setOpen}>
                  <DialogTrigger className="inline-flex items-center justify-center rounded-2xl bg-primary px-8 h-12 text-lg font-bold text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90 transition-colors cursor-pointer">
                    <Pencil size={18} className="mr-2" />
                    Edit Profile
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
                          {updating ? "Saving..." : "Save Profile Changes"}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="bg-muted/50 p-1 rounded-2xl mb-8">
              <TabsTrigger value="overview" className="rounded-xl font-bold px-6">Overview</TabsTrigger>
              {role === 'candidate' && <TabsTrigger value="applications" className="rounded-xl font-bold px-6">My Applications</TabsTrigger>}
            </TabsList>

            <TabsContent value="overview" className="space-y-8 outline-none">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-8">
                        <section className="bg-card border rounded-[32px] p-8 shadow-sm">
                            <h3 className="text-xl font-black mb-6 flex items-center gap-3">
                                <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
                                    <Info size={20} />
                                </div>
                                {role === 'company' ? 'About Our Company' : 'Professional Summary'}
                            </h3>
                            <div className="text-muted-foreground font-medium leading-relaxed text-lg whitespace-pre-wrap">
                            {role === 'company' 
                                ? (profile?.description || "No description provided.")
                                : (profile?.resume_text ? (profile.resume_text.substring(0, 500) + "...") : "Upload your resume to see your profile summary.")
                            }
                            </div>
                        </section>
                    </div>

                    <aside className="space-y-8">
                        <section className="bg-card border rounded-[32px] p-8 shadow-sm">
                            <h3 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-6 pb-2 border-b">
                            Details
                            </h3>
                            <div className="space-y-6">
                            {role === 'company' ? (
                                <div className="flex items-start gap-4">
                                    <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                                        <Globe size={18} />
                                    </div>
                                    <div className="overflow-hidden">
                                        <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Website</p>
                                        <p className="text-sm font-bold text-primary truncate">{profile?.website || "Not set"}</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-start gap-4">
                                    <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center text-muted-foreground shrink-0">
                                        <Briefcase size={18} />
                                    </div>
                                    <div>
                                        <p className="text-[10px] uppercase font-black text-muted-foreground mb-0.5 tracking-tighter">Experience</p>
                                        <p className="text-sm font-bold">{profile?.experience_years || 0} Years</p>
                                    </div>
                                </div>
                            )}
                            </div>
                        </section>
                    </aside>
                </div>
            </TabsContent>

            <TabsContent value="applications" className="space-y-6 outline-none">
                {applications.length === 0 ? (
                    <div className="py-20 text-center border-2 border-dashed rounded-[32px] bg-muted/5">
                        <p className="text-muted-foreground font-bold italic">You haven't applied to any jobs yet.</p>
                        <Button variant="link" onClick={() => navigate('/candidate-home')} className="mt-2">Browse Jobs</Button>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {applications.map((app) => (
                            <Card key={app.id} className="border-muted-foreground/10 rounded-[24px] overflow-hidden hover:shadow-md transition-shadow">
                                <CardContent className="p-6">
                                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                        <div className="flex items-center gap-4">
                                            <Avatar className="h-12 w-12 rounded-xl border bg-muted/20">
                                                <AvatarImage src={app.company_logo} />
                                                <AvatarFallback className="font-bold text-primary bg-primary/5">
                                                    {app.company_name?.substring(0,2).toUpperCase()}
                                                </AvatarFallback>
                                            </Avatar>
                                            <div>
                                                <h4 className="font-black text-lg leading-tight">{app.job_title}</h4>
                                                <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold mt-1">
                                                    <Building2 size={12} /> {app.company_name}
                                                    <span>•</span>
                                                    <Clock size={12} /> {new Date(app.applied_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-4">
                                            <Badge className={`uppercase text-[10px] font-black px-3 py-1 rounded-full ${
                                                app.status === 'shortlisted' 
                                                ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' 
                                                : app.status === 'rejected'
                                                ? 'bg-red-500/10 text-red-600 border-red-500/20'
                                                : 'bg-muted text-muted-foreground'
                                            }`}>
                                                {app.status}
                                            </Badge>

                                            {app.status === 'shortlisted' && (
                                                <Button 
                                                    size="sm" 
                                                    className="font-black rounded-xl bg-primary shadow-lg shadow-primary/20 animate-pulse hover:animate-none"
                                                    onClick={() => handleStartInterview(app.id)}
                                                >
                                                    <Play size={14} className="mr-1.5 fill-current" />
                                                    Start AI Interview
                                                </Button>
                                            )}

                                            {app.status === 'interviewed' && (
                                                <div className="flex items-center gap-1.5 text-emerald-600 font-bold text-sm">
                                                    <CheckCircle2 size={18} />
                                                    Interview Done
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Profile;
