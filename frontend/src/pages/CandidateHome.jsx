import React, { useState, useEffect } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Button } from "../components/ui/button";
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
  ArrowRight
} from "lucide-react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { jobApi } from "../lib/api";

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

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await jobApi.getAllJobs();
      setJobs(response.data);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary/10 selection:text-primary">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-12">
          <div className="space-y-2">
            <Badge variant="secondary" className="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-primary/5 text-primary border-primary/10 mb-2">
              <Sparkles size={12} className="mr-1.5 fill-primary" />
              AI Matching is active
            </Badge>
            <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-foreground">
              Your next career move <br />
              starts <span className="text-primary">right here.</span>
            </h1>
            <p className="text-muted-foreground text-lg max-w-xl">
              We've analyzed your profile and found {jobs.length} new roles that match your skills and experience.
            </p>
          </div>
          
          <div className="flex gap-4">
            <Card className="shadow-sm border-muted-foreground/10 bg-muted/5">
              <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                <span className="text-2xl font-bold text-primary">12</span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Applications</span>
              </CardContent>
            </Card>
            <Card className="shadow-sm border-muted-foreground/10 bg-muted/5">
              <CardContent className="p-4 flex flex-col items-center justify-center text-center">
                <span className="text-2xl font-bold text-primary">5</span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Interviews</span>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-16 p-4 bg-muted/30 rounded-2xl border">
          <div className="md:col-span-5 relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
            <Input 
              placeholder="Job title, keywords, or company" 
              className="pl-10 h-12 bg-background border-muted-foreground/20 focus-visible:ring-primary/20"
            />
          </div>
          <div className="md:col-span-4 relative group">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
            <Input 
              placeholder="City, state, or remote" 
              className="pl-10 h-12 bg-background border-muted-foreground/20 focus-visible:ring-primary/20"
            />
          </div>
          <div className="md:col-span-3 flex gap-2">
            <Button variant="outline" size="lg" className="h-12 border-muted-foreground/20">
              <Filter size={18} className="mr-2" />
              Filters
            </Button>
            <Button size="lg" className="flex-1 h-12 shadow-sm font-bold">
              Find Jobs
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Main Feed */}
          <div className="lg:col-span-8">
            <Tabs defaultValue="recommended" className="w-full">
              <div className="flex items-center justify-between border-b mb-6">
                <TabsList className="bg-transparent h-auto p-0 gap-8 rounded-none">
                  <TabsTrigger 
                    value="recommended" 
                    className="px-0 py-3 bg-transparent border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-foreground rounded-none text-base font-semibold shadow-none transition-all"
                  >
                    Recommended
                  </TabsTrigger>
                  <TabsTrigger 
                    value="recent" 
                    className="px-0 py-3 bg-transparent border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-foreground rounded-none text-base font-semibold shadow-none transition-all"
                  >
                    Newest
                  </TabsTrigger>
                  <TabsTrigger 
                    value="saved" 
                    className="px-0 py-3 bg-transparent border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:text-foreground rounded-none text-base font-semibold shadow-none transition-all"
                  >
                    Saved
                  </TabsTrigger>
                </TabsList>
                <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground font-medium">
                  Sort by: <span className="text-foreground cursor-pointer hover:underline">Relevance</span>
                </div>
              </div>

              <TabsContent value="recommended" className="mt-0 space-y-4 outline-none">
                {loading ? (
                    [1,2,3].map(i => (
                        <div key={i} className="h-40 w-full bg-muted animate-pulse rounded-2xl" />
                    ))
                ) : jobs.length > 0 ? (
                    jobs.map((job) => (
                    <Card key={job.id} className="group hover:border-primary/30 transition-all duration-200 shadow-sm hover:shadow-md">
                        <CardHeader className="p-6 pb-4">
                        <div className="flex justify-between items-start">
                            <div className="flex gap-4">
                            <Avatar className="h-12 w-12 rounded-lg border bg-muted/20">
                                <AvatarImage src={job.company_logo} />
                                <AvatarFallback className="font-bold text-primary bg-primary/5">
                                    {job.company_name?.substring(0, 2).toUpperCase()}
                                </AvatarFallback>
                            </Avatar>
                            <div className="space-y-1">
                                <CardTitle className="text-xl group-hover:text-primary transition-colors leading-none">{job.title}</CardTitle>
                                <div className="flex items-center gap-3 text-sm text-muted-foreground font-medium">
                                <span className="flex items-center gap-1.5"><Building2 size={14} /> {job.company_name}</span>
                                <span>•</span>
                                <span className="flex items-center gap-1.5"><MapPin size={14} /> {job.location || "Remote"}</span>
                                </div>
                            </div>
                            </div>
                            <Badge className="bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/10 border-emerald-500/20 px-2 py-0.5 font-bold">
                            95% Match
                            </Badge>
                        </div>
                        </CardHeader>
                        <CardContent className="px-6 pb-6">
                        <div className="flex flex-wrap gap-2 mb-4">
                            {job.job_type && (
                                <Badge variant="secondary" className="font-medium text-[10px] px-2 py-0.5 rounded-md uppercase">
                                    {job.job_type}
                                </Badge>
                            )}
                            <Badge variant="outline" className="font-medium text-[10px] px-2 py-0.5 rounded-md">
                                AI Analyzed
                            </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-xs font-semibold text-muted-foreground">
                            <span className="flex items-center gap-1.5"><DollarSign size={14} /> {job.salary_min && job.salary_max ? `$${job.salary_min/1000}k - $${job.salary_max/1000}k` : "Salary Undisclosed"}</span>
                            <span className="flex items-center gap-1.5"><Briefcase size={14} /> {job.job_type || "Full-time"}</span>
                            <span className="flex items-center gap-1.5"><Clock size={14} /> {formatRelativeTime(job.created_at)}</span>
                        </div>
                        </CardContent>
                        <Separator className="opacity-50" />
                        <CardFooter className="px-6 py-3 flex justify-between items-center bg-muted/5 group-hover:bg-muted/10 transition-colors">
                        <Button variant="ghost" size="sm" className="h-8 px-2 text-muted-foreground hover:text-primary">
                            <Bookmark size={18} className="mr-2" />
                            Save
                        </Button>
                        <Button size="sm" className="h-9 px-6 font-bold">
                            Apply Now
                        </Button>
                        </CardFooter>
                    </Card>
                    ))
                ) : (
                    <div className="py-20 text-center border-2 border-dashed rounded-3xl bg-muted/5">
                        <p className="text-muted-foreground font-bold italic">No jobs found matching your profile yet.</p>
                        <Button variant="link" onClick={fetchJobs} className="mt-2 text-primary">Refresh Feed</Button>
                    </div>
                )}
                
                {jobs.length > 0 && (
                    <Button variant="ghost" className="w-full h-12 text-muted-foreground hover:text-primary font-semibold">
                    Show more results
                    </Button>
                )}
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="shadow-sm border-primary/10 bg-primary/[0.02]">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                  <TrendingUp size={18} className="text-primary" /> 
                  Career Snapshot
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-bold">
                    <span className="text-muted-foreground">Profile Strength</span>
                    <span className="text-primary">85%</span>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-[85%] rounded-full" />
                  </div>
                  <p className="text-[10px] text-muted-foreground font-medium">Add a portfolio link to reach 100%</p>
                </div>
                
                <Separator />
                
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Top Skill Gaps</h4>
                  <div className="flex flex-wrap gap-2">
                    {["Next.js", "Docker", "System Design"].map(s => (
                      <Badge key={s} variant="outline" className="text-[10px] font-bold border-primary/20 text-primary bg-primary/5">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <Button variant="outline" className="w-full text-xs font-bold h-9">
                  Enhance My Profile
                </Button>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-bold">Featured Companies</CardTitle>
                <CardDescription className="text-xs font-medium">Top recruiters hiring this week</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[280px]">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex items-center justify-between px-6 py-4 border-b last:border-none hover:bg-muted/20 transition-colors cursor-pointer group">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-9 w-9 border rounded-md">
                          <AvatarFallback className="text-xs font-bold">T{i}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-sm font-bold group-hover:text-primary transition-colors">TechNova Labs</p>
                          <p className="text-[10px] font-medium text-muted-foreground">12 Active Roles</p>
                        </div>
                      </div>
                      <ChevronRight size={16} className="text-muted-foreground group-hover:text-foreground transition-transform group-hover:translate-x-0.5" />
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
              <CardFooter className="p-4 bg-muted/10 border-t">
                <Button variant="link" className="w-full h-auto p-0 text-xs font-bold text-muted-foreground hover:text-primary group">
                  View all companies
                  <ArrowRight size={14} className="ml-1 transition-transform group-hover:translate-x-1" />
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default CandidateHome;
