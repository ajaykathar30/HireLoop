import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Mic, 
  Square, 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertCircle,
  Volume2,
  BrainCircuit,
  Timer,
  LogOut,
  Send,
  Trash2,
  ShieldCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { interviewApi } from '../lib/api';
import toast from 'react-hot-toast';

const InterviewSession = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [status, setStatus] = useState('entry'); // entry, loading, ready, speaking, listening, processing, finished
  const [timeLeft, setTimeLeft] = useState(30);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [ending, setEnding] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioPlayerRef = useRef(new Audio());
  const isTimeoutRef = useRef(false);

  const handleStartInterview = async () => {
    try {
      setStatus('loading');
      const response = await interviewApi.start(sessionId);
      setCurrentQuestion(response.data);
      setStatus('ready');
      
      // Now that user has clicked 'Start', we can safely play audio
      playQuestionAudio(response.data.audio_base64);
    } catch (err) {
      toast.error("Failed to join interview room");
      navigate('/profile');
    }
  };

  const playQuestionAudio = (base64) => {
    setRecordedBlob(null);
    if (!base64) {
        setStatus('listening');
        return;
    }
    setStatus('speaking');
    audioPlayerRef.current.src = `data:audio/wav;base64,${base64}`;
    
    // This play() will now succeed because of the 'Start' button click
    audioPlayerRef.current.play().catch(err => {
        console.error("Audio playback blocked:", err);
        setStatus('listening');
    });

    audioPlayerRef.current.onended = () => {
      setStatus('listening');
    };
  };

  const startTimer = () => {
    setTimeLeft(30);
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          toast.error("Time limit reached! Recording saved.");
          handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleTimeout = () => {
    if (isRecording) {
        stopRecording(true);
    } else {
        submitAnswer(null, true);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => audioChunksRef.current.push(event.data);
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedBlob(audioBlob);
        if (isTimeoutRef.current) {
            submitAnswer(null, true);
        }
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      startTimer();
    } catch (err) {
      toast.error("Microphone access required");
    }
  };

  const stopRecording = (timeout = false) => {
    isTimeoutRef.current = timeout;
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    setIsRecording(false);
    clearInterval(timerRef.current);
  };

  const handleSubmit = () => {
    if (recordedBlob) {
        submitAnswer(recordedBlob, false);
    }
  };

  const submitAnswer = async (blob, timeout) => {
    setStatus('processing');
    try {
      const response = await interviewApi.submitAnswer(sessionId, blob, timeout);
      if (response.data.status === 'completed') {
        setStatus('finished');
      } else {
        setCurrentQuestion(response.data);
        playQuestionAudio(response.data.audio_base64);
      }
    } catch (err) {
      toast.error("Submission failed");
      setStatus('listening');
    }
  };

  const handleEndEarly = async () => {
    if (!window.confirm("End interview now? Your progress will be saved.")) return;
    setEnding(true);
    try {
        if (isRecording) stopRecording(false);
        await interviewApi.submitAnswer(sessionId, null, false, true);
        setStatus('finished');
    } catch (err) {
        toast.error("Failed to end session");
    } finally {
        setEnding(false);
    }
  };

  // --- RENDERING LOADING ---
  if (status === 'loading') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white">
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <p className="text-lg font-bold tracking-widest uppercase animate-pulse">Syncing with AI...</p>
      </div>
    );
  }

  // --- RENDERING ENTRY SCREEN (FIX FOR AUTOPLAY ERROR) ---
  if (status === 'entry') {
    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
            <Card className="max-w-xl w-full bg-white/5 border-white/10 backdrop-blur-xl rounded-[40px] shadow-2xl z-10">
                <CardHeader className="text-center pt-10 pb-2">
                    <div className="bg-primary h-16 w-16 rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20 mx-auto mb-6">
                        <BrainCircuit className="text-white" size={36} />
                    </div>
                    <CardTitle className="text-3xl font-black text-white">Ready to begin?</CardTitle>
                    <CardDescription className="text-slate-400 text-lg mt-2">
                        You're about to start your AI-powered interview.
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-8 space-y-8">
                    <div className="grid gap-4">
                        <div className="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/5">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary"><ShieldCheck size={20} /></div>
                            <p className="text-sm font-bold text-slate-300">Ensure you're in a quiet environment</p>
                        </div>
                        <div className="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/5">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary"><Volume2 size={20} /></div>
                            <p className="text-sm font-bold text-slate-300">Turn up your volume to hear the AI</p>
                        </div>
                        <div className="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/5">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary"><Mic size={20} /></div>
                            <p className="text-sm font-bold text-slate-300">Allow microphone access when prompted</p>
                        </div>
                    </div>
                    <Button 
                        size="lg" 
                        className="w-full h-16 text-xl font-black rounded-2xl shadow-xl shadow-primary/40 hover:scale-[1.02] transition-transform"
                        onClick={handleStartInterview}
                    >
                        Start Interview Now
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
  }

  // --- RENDERING FINISHED ---
  if (status === 'finished') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 p-6">
        <div className="max-w-md w-full text-center space-y-8 animate-in fade-in zoom-in duration-500">
          <div className="h-24 w-24 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto border-2 border-emerald-500/50">
            <CheckCircle2 className="h-12 w-12 text-emerald-500" />
          </div>
          <div className="space-y-2">
            <h1 className="text-4xl font-black text-white tracking-tight">Interview Ended</h1>
            <p className="text-slate-400 text-lg">Your responses have been saved and your report is being generated.</p>
          </div>
          <Button size="lg" className="w-full h-14 text-lg font-bold rounded-2xl shadow-xl shadow-primary/20" onClick={() => navigate('/profile')}>
            View My Applications
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <header className="p-6 flex items-center justify-between border-b border-white/5 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-4">
            <div className="bg-primary h-10 w-10 rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
                <BrainCircuit className="text-white" size={24} />
            </div>
            <h2 className="text-white font-bold leading-none hidden md:block tracking-tight">AI Interview Room</h2>
        </div>

        <div className="flex items-center gap-6 w-full max-w-md mx-8">
            <div className="flex-1 space-y-2">
                <div className="flex justify-between text-[10px] font-black uppercase text-slate-500 tracking-tighter">
                    <span>Question {currentQuestion?.question_number || 1} / 5</span>
                </div>
                <Progress value={(currentQuestion?.question_number || 1) * 20} className="h-1.5 bg-slate-800" />
            </div>
        </div>

        <div className="flex items-center gap-4">
            {isRecording && (
                <div className="flex items-center gap-3 bg-red-500/10 px-4 py-2 rounded-2xl border border-red-500/20">
                    <Timer className="h-4 w-4 text-red-500 animate-pulse" />
                    <span className="font-mono font-bold text-sm text-red-500">00:{timeLeft.toString().padStart(2, '0')}</span>
                </div>
            )}
            <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white" onClick={handleEndEarly} disabled={ending}>
                <LogOut size={18} />
            </Button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-6 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="max-w-3xl w-full z-10 space-y-12">
          {/* AI Character */}
          <div className="flex flex-col items-center gap-6">
            <div className="relative">
              <div className={`absolute inset-0 bg-primary rounded-full blur-2xl transition-opacity duration-1000 ${status === 'speaking' ? 'opacity-40 animate-pulse' : 'opacity-0'}`} />
              <Avatar className={`h-32 w-32 border-4 bg-slate-900 shadow-2xl transition-all duration-500 ${status === 'speaking' ? 'scale-110 border-primary' : 'border-white/10'}`}>
                <AvatarFallback className="bg-slate-800 text-primary text-3xl font-black italic underline underline-offset-4 decoration-primary">AI</AvatarFallback>
              </Avatar>
            </div>

            <Card className="w-full bg-white/5 border-white/10 backdrop-blur-xl rounded-[32px] overflow-hidden shadow-2xl">
              <CardContent className="p-10 text-center">
                <p className="text-2xl md:text-3xl font-bold text-white leading-relaxed tracking-tight">
                  {status === 'processing' ? 'Thinking...' : currentQuestion?.text}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Interaction Zone */}
          <div className="flex flex-col items-center gap-8">
            {!recordedBlob ? (
                <div className="flex flex-col items-center gap-4">
                    <Button 
                        size="icon" 
                        className={`h-24 w-24 rounded-full shadow-2xl transition-all duration-300 ${isRecording ? 'bg-red-500 scale-110' : 'bg-primary'}`}
                        disabled={status !== 'listening' && !isRecording}
                        onClick={isRecording ? () => stopRecording(false) : startRecording}
                    >
                        {isRecording ? <Square size={32} fill="currentColor" /> : <Mic size={32} />}
                    </Button>
                    <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">
                        {isRecording ? "Click to stop" : "Click to start recording"}
                    </p>
                </div>
            ) : (
                <div className="flex flex-col items-center gap-6 animate-in fade-in slide-in-from-bottom-4">
                    <div className="flex items-center gap-4">
                        <Button 
                            variant="outline" 
                            size="lg" 
                            className="rounded-2xl border-white/10 h-14 px-8 text-slate-300"
                            onClick={() => setRecordedBlob(null)}
                        >
                            <Trash2 size={18} className="mr-2" /> Redo
                        </Button>
                        <Button 
                            size="lg" 
                            className="rounded-2xl h-14 px-10 font-black text-lg shadow-xl shadow-primary/40"
                            onClick={handleSubmit}
                        >
                            <Send size={18} className="mr-2" /> Send Answer
                        </Button>
                    </div>
                    <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 py-1 px-4 rounded-full">
                        Recording Ready
                    </Badge>
                </div>
            )}

            {status === 'processing' && (
                <div className="flex items-center gap-2 text-primary font-bold uppercase tracking-widest text-xs animate-pulse">
                    <Loader2 className="h-4 w-4 animate-spin" /> Analyzing your response...
                </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default InterviewSession;
