import React, { useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
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
    <div className="min-h-screen bg-background font-sans">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <Button 
            variant="ghost" 
            className="pl-0 text-muted-foreground hover:text-primary transition-colors"
            onClick={() => navigate("/company/jobs")}
          >
            <ArrowLeft size={18} className="mr-2" />
            Back to Jobs
          </Button>
          <h1 className="text-4xl font-extrabold tracking-tight mt-4">Post a New Position</h1>
          <p className="text-muted-foreground font-medium text-lg mt-2">Fill in the details to find your next great hire.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-10">
          {/* Basic Info */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 pb-2 border-b">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Briefcase size={18} className="text-primary" />
              </div>
              <h2 className="text-xl font-bold italic uppercase tracking-tighter">Job Details</h2>
            </div>
            
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="title">Job Title</Label>
                <Input 
                  id="title" 
                  placeholder="e.g. Senior Software Engineer" 
                  required 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="h-11"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Job Type</Label>
                  <Select 
                    defaultValue="Full-time"
                    onValueChange={(val) => setFormData({...formData, job_type: val})}
                  >
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Full-time">Full-time</SelectItem>
                      <SelectItem value="Part-time">Part-time</SelectItem>
                      <SelectItem value="Contract">Contract</SelectItem>
                      <SelectItem value="Internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                    <Input 
                      id="location" 
                      placeholder="e.g. Remote, New York, NY" 
                      required 
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                      className="pl-10 h-11"
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Description & Requirements */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 pb-2 border-b">
              <div className="h-8 w-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Info size={18} className="text-purple-500" />
              </div>
              <h2 className="text-xl font-bold italic uppercase tracking-tighter">Content</h2>
            </div>
            
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="description">Job Description</Label>
                <Textarea 
                  id="description" 
                  placeholder="Describe the role, team, and day-to-day responsibilities..." 
                  className="min-h-[150px] leading-relaxed"
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="requirements">Requirements</Label>
                <Textarea 
                  id="requirements" 
                  placeholder="List skills, experience, and qualifications..." 
                  className="min-h-[150px] leading-relaxed"
                  required
                  value={formData.requirements}
                  onChange={(e) => setFormData({...formData, requirements: e.target.value})}
                />
              </div>
            </div>
          </section>

          {/* Salary & Deadline */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 pb-2 border-b">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <DollarSign size={18} className="text-emerald-500" />
              </div>
              <h2 className="text-xl font-bold italic uppercase tracking-tighter">Settings</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="salary_min">Min Salary ($)</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                  <Input 
                    id="salary_min" 
                    type="number"
                    placeholder="80000" 
                    value={formData.salary_min}
                    onChange={(e) => setFormData({...formData, salary_min: e.target.value})}
                    className="pl-7 h-11"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary_max">Max Salary ($)</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                  <Input 
                    id="salary_max" 
                    type="number"
                    placeholder="120000" 
                    value={formData.salary_max}
                    onChange={(e) => setFormData({...formData, salary_max: e.target.value})}
                    className="pl-7 h-11"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="deadline">Deadline</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                  <Input 
                    id="deadline" 
                    type="date"
                    value={formData.application_deadline}
                    onChange={(e) => setFormData({...formData, application_deadline: e.target.value})}
                    className="pl-10 h-11"
                  />
                </div>
              </div>
            </div>
          </section>

          <div className="pt-6 flex gap-4">
            <Button 
              type="submit" 
              className="flex-1 h-14 font-bold text-lg shadow-xl shadow-primary/20"
              disabled={loading}
            >
              {loading ? "Publishing..." : "Publish Job Opening"}
              {!loading && <Sparkles size={18} className="ml-2 fill-current" />}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              className="h-14 px-8 font-bold text-lg"
              onClick={() => navigate("/company/jobs")}
            >
              Cancel
            </Button>
          </div>
        </form>
      </main>

      <Footer />
    </div>
  );
};

export default PostJob;
