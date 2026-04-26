import React, { useEffect, useState } from 'react';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Button } from "@/components/ui/button";
import { 
  Plus, 
  Search, 
  MoreHorizontal, 
  MapPin, 
  Briefcase, 
  Clock, 
  Users,
  Eye
} from "lucide-react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
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
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Manage Jobs</h1>
            <p className="text-muted-foreground font-medium">Post and manage your company's open positions</p>
          </div>
          <Button 
            className="font-bold shadow-lg shadow-primary/20"
            onClick={() => navigate("/company/jobs/create")}
          >
            <Plus size={18} className="mr-2" />
            Post Jobs
          </Button>
        </div>

        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
            <Input 
              placeholder="Search jobs..." 
              className="pl-10 h-10 border-muted-foreground/20 focus-visible:ring-primary/20"
            />
          </div>
        </div>

        <Card className="border-muted-foreground/10 shadow-sm overflow-hidden">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="font-bold uppercase tracking-wider text-[11px]">Role Title</TableHead>
                <TableHead className="font-bold uppercase tracking-wider text-[11px]">Type</TableHead>
                <TableHead className="font-bold uppercase tracking-wider text-[11px]">Location</TableHead>
                <TableHead className="font-bold uppercase tracking-wider text-[11px]">Status</TableHead>
                <TableHead className="font-bold uppercase tracking-wider text-[11px]">Date Posted</TableHead>
                <TableHead className="text-right font-bold uppercase tracking-wider text-[11px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-32 text-center">
                    <div className="flex items-center justify-center gap-2 text-muted-foreground">
                      <div className="h-4 w-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                      Loading jobs...
                    </div>
                  </TableCell>
                </TableRow>
              ) : jobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-64 text-center">
                    <div className="flex flex-col items-center justify-center gap-4">
                      <div className="bg-muted p-4 rounded-full">
                        <Briefcase size={32} className="text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-lg font-bold">No jobs posted yet</p>
                        <p className="text-sm text-muted-foreground font-medium">Create your first job listing to start hiring.</p>
                      </div>
                      <Button variant="outline" size="sm" className="font-bold">
                        Learn how to post
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                jobs.map((job) => (
                  <TableRow key={job.id} className="group hover:bg-muted/30 transition-colors">
                    <TableCell>
                      <div className="font-bold text-foreground group-hover:text-primary transition-colors">{job.title}</div>
                      <div className="text-[11px] text-muted-foreground font-medium uppercase">ID: {job.id.substring(0, 8)}</div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-[10px] font-bold uppercase tracking-tight">
                        {job.job_type}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm font-medium text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <MapPin size={14} />
                        {job.location}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-[10px] font-bold uppercase tracking-tight ${
                        job.status === 'open' 
                        ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' 
                        : 'bg-muted text-muted-foreground border-muted-foreground/20'
                      }`}>
                        {job.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm font-medium text-muted-foreground italic">
                      {new Date(job.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="icon-sm" 
                          className="h-8 w-8 hover:text-primary"
                          onClick={() => navigate(`/company/jobs/${job.id}/applicants`)}
                        >
                          <Eye size={16} />
                        </Button>
                        <Button variant="ghost" size="icon-sm" className="h-8 w-8 hover:text-primary">
                          <MoreHorizontal size={16} />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default CompanyJobs;
