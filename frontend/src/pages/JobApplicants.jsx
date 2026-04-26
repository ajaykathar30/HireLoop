import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Button } from "@/components/ui/button";
import { 
  ArrowLeft, 
  Search, 
  Sparkles, 
  Filter, 
  User, 
  Mail, 
  Calendar,
  ChevronRight,
  TrendingUp,
  Brain,
  FileText
} from "lucide-react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { applicationApi, jobApi, interviewApi } from "../lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import toast from 'react-hot-toast';

const JobApplicants = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [applicants, setApplicants] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  const isPipelineTriggered = applicants.some(a => a.fit_score > 0);
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
      setApplicants(response.data);

      try {
        const reportRes = await interviewApi.getJobReports(jobId);
        setReports(reportRes.data.reports || []);
      } catch (err) {
        console.error("Failed to load reports", err);
      }
    } catch (err) {
      toast.error("Failed to load applicants");
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerPipeline = async () => {
    setTriggering(true);
    try {
      await jobApi.triggerPipeline(jobId);
      toast.success("AI Pipeline triggered! Shortlisting in progress...");
      // Refresh after a delay to see status changes
      setTimeout(fetchApplicants, 2000);
    } catch (err) {
      toast.error("Failed to trigger pipeline");
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div className="space-y-1">
            <Button 
                variant="ghost" 
                size="sm" 
                className="pl-0 text-muted-foreground hover:text-primary transition-colors"
                onClick={() => navigate("/company/jobs")}
            >
                <ArrowLeft size={16} className="mr-2" />
                Back to Jobs
            </Button>
            <h1 className="text-3xl font-black tracking-tight text-foreground flex items-center gap-3">
              Applicants Dashboard
              <Badge variant="outline" className="text-xs uppercase font-bold tracking-widest px-2 py-0.5 rounded-md">
                {applicants.length} Total
              </Badge>
            </h1>
          </div>
          
          {!isPipelineTriggered && (
            <Button 
              className="h-12 px-8 font-black shadow-lg shadow-primary/20 bg-primary hover:bg-primary/90 rounded-2xl"
              disabled={triggering || applicants.length === 0}
              onClick={handleTriggerPipeline}
            >
              {triggering ? (
                  <Sparkles className="mr-2 animate-spin" size={18} />
              ) : (
                  <Sparkles className="mr-2 fill-current" size={18} />
              )}
              Trigger AI Screening
            </Button>
          )}
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <Card className="border-muted-foreground/10 bg-muted/5 shadow-none">
                <CardContent className="p-6 flex items-center gap-4">
                    <div className="h-12 w-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-600">
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Average Fit</p>
                        <p className="text-2xl font-black">{averageFit}%</p>
                    </div>
                </CardContent>
            </Card>
            <Card className="border-muted-foreground/10 bg-muted/5 shadow-none">
                <CardContent className="p-6 flex items-center gap-4">
                    <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-600">
                        <Sparkles size={24} />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Shortlisted</p>
                        <p className="text-2xl font-black">
                            {applicants.filter(a => a.status === 'shortlisted').length}
                        </p>
                    </div>
                </CardContent>
            </Card>
            <Card className="border-muted-foreground/10 bg-muted/5 shadow-none">
                <CardContent className="p-6 flex items-center gap-4">
                    <div className="h-12 w-12 rounded-2xl bg-purple-500/10 flex items-center justify-center text-purple-600">
                        <Brain size={24} />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">AI Screened</p>
                        <p className="text-2xl font-black">
                            {applicants.filter(a => a.fit_score > 0).length}
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>

        {/* Applicants Table */}
        <Card className="border-muted-foreground/10 shadow-sm overflow-hidden rounded-[24px]">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="font-black uppercase tracking-widest text-[10px] py-4 pl-8">Candidate</TableHead>
                <TableHead className="font-black uppercase tracking-widest text-[10px] py-4">AI Fit Score</TableHead>
                <TableHead className="font-black uppercase tracking-widest text-[10px] py-4">Experience</TableHead>
                <TableHead className="font-black uppercase tracking-widest text-[10px] py-4">Status</TableHead>
                <TableHead className="text-right font-black uppercase tracking-widest text-[10px] py-4 pr-8">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-32 text-center">
                    <div className="flex items-center justify-center gap-2 text-muted-foreground">
                      <div className="h-4 w-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                      Fetching candidates...
                    </div>
                  </TableCell>
                </TableRow>
              ) : applicants.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-64 text-center">
                    <div className="flex flex-col items-center justify-center gap-4">
                      <div className="bg-muted p-4 rounded-full">
                        <User size={32} className="text-muted-foreground" />
                      </div>
                      <p className="text-muted-foreground font-bold italic">No candidates have applied for this position yet.</p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                applicants.map((app) => {
                  const appReport = reports.find(r => r.application_id === app.id);
                  const hasCompletedInterview = appReport && appReport.status === 'completed';

                  return (
                  <TableRow key={app.id} className="group hover:bg-muted/30 transition-colors">
                    <TableCell className="pl-8 py-5">
                      <div className="flex items-center gap-4">
                        <Avatar className="h-10 w-10 border rounded-xl bg-background">
                          <AvatarFallback className="font-bold text-xs bg-primary/5 text-primary">
                            {app.candidate_name?.substring(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-bold text-foreground">{app.candidate_name}</div>
                          <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">Applied {new Date(app.applied_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="w-full max-w-[120px] space-y-1.5">
                        <div className="flex justify-between text-[10px] font-black uppercase tracking-tighter">
                            <span className="text-primary">{app.fit_score || 0}%</span>
                        </div>
                        <Progress value={app.fit_score || 0} className="h-1.5 bg-muted" />
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px] font-bold uppercase tracking-tight border-muted-foreground/20">
                        {app.candidate_experience || 0} Years
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md ${
                        app.status === 'shortlisted' 
                        ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' 
                        : app.status === 'rejected'
                        ? 'bg-red-500/10 text-red-600 border-red-500/20'
                        : 'bg-muted text-muted-foreground border-muted-foreground/20'
                      }`}>
                        {app.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right pr-8">
                      <div className="flex items-center justify-end gap-2">
                        <Button 
                            variant="outline" 
                            size="sm" 
                            className={`h-9 px-3 font-bold text-xs rounded-xl ${hasCompletedInterview ? 'hover:text-primary' : 'opacity-50 cursor-not-allowed'}`}
                            onClick={() => {
                                if (hasCompletedInterview) {
                                    setSelectedReport(appReport);
                                    setIsReportOpen(true);
                                } else {
                                    toast.error("Interview has not been taken yet.");
                                }
                            }}
                        >
                            <FileText size={14} className="mr-2" />
                            View Report
                        </Button>
                        <Button variant="ghost" size="sm" className="h-9 px-4 font-bold text-xs hover:text-primary rounded-xl">
                            View Resume
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );})
              )}
            </TableBody>
          </Table>
        </Card>
        
        {/* Report Dialog */}
        <Dialog open={isReportOpen} onOpenChange={setIsReportOpen}>
          <DialogContent className="max-w-[50vw] lg:max-w-[800px] max-h-[85vh] p-0 overflow-hidden flex flex-col rounded-[24px]">
            <DialogHeader className="p-6 bg-muted/50 border-b shrink-0">
              <DialogTitle className="text-2xl font-black flex items-center gap-2">
                <Brain className="text-purple-600" />
                AI Interview Report
              </DialogTitle>
              {selectedReport && (
                <div className="text-sm text-muted-foreground mt-2">
                  Candidate: <span className="font-bold text-foreground">{selectedReport.candidate_name}</span>
                </div>
              )}
            </DialogHeader>
            <div className="flex-1 overflow-y-auto p-6">
              {selectedReport && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
                    <div>
                      <h3 className="font-bold text-purple-900 dark:text-purple-300">Total Score</h3>
                      <p className="text-sm text-purple-700 dark:text-purple-400">Aggregated AI evaluation</p>
                    </div>
                    <div className="text-3xl font-black text-purple-600">
                      {selectedReport.total_score || 0}<span className="text-lg text-muted-foreground">/100</span>
                    </div>
                  </div>
                  
                  {selectedReport.report_summary && (
                    <div className="space-y-2">
                      <h3 className="font-black text-lg tracking-tight">Executive Summary</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap p-4 bg-muted/50 rounded-xl">
                        {selectedReport.report_summary}
                      </p>
                    </div>
                  )}

                  <div className="space-y-4">
                    <h3 className="font-black text-lg tracking-tight">Detailed Responses</h3>
                    {selectedReport.questions.map((q, i) => (
                      <Card key={i} className="border-muted-foreground/10 shadow-none">
                        <CardHeader className="p-4 pb-2">
                          <CardTitle className="text-sm font-bold flex justify-between gap-4">
                            <span>{i + 1}. {q.question}</span>
                            <Badge variant="outline" className="shrink-0">{q.score || 0}/20</Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 pt-0 space-y-3 text-sm">
                          <div>
                            <span className="font-bold text-xs uppercase tracking-widest text-muted-foreground block mb-1">Answer</span>
                            <p className="text-foreground bg-muted/30 p-3 rounded-lg">{q.answer || "No answer provided"}</p>
                          </div>
                          {q.feedback && (
                            <div>
                              <span className="font-bold text-xs uppercase tracking-widest text-emerald-600 block mb-1">AI Feedback</span>
                              <p className="text-muted-foreground p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">{q.feedback}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
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
