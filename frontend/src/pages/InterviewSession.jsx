import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Mic, 
  Square, 
  Loader2, 
  CheckCircle2, 
  Volume2,
  BrainCircuit,
  Timer,
  LogOut,
  Send,
  Trash2,
  ShieldCheck
} from 'lucide-react';
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
      playQuestionAudio(response.data.question_number);
    } catch (err) {
      toast.error("Failed to join interview room");
      navigate('/profile');
    }
  };

  const playQuestionAudio = (questionNumber) => {
    setRecordedBlob(null);
    if (!questionNumber) {
        setStatus('listening');
        return;
    }
    setStatus('speaking');
    const idx = questionNumber - 1;
    audioPlayerRef.current.src = `http://127.0.0.1:8000/interviews/${sessionId}/stream-audio/${idx}?t=${Date.now()}`;
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
          toast.error("Time limit reached!");
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
        playQuestionAudio(response.data.question_number);
      }
    } catch (err) {
      toast.error("Submission failed");
      setStatus('listening');
    }
  };

  const handleEndEarly = async () => {
    if (!window.confirm("End interview now?")) return;
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

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white">
        <div className="h-20 w-20 border-8 border-black border-t-primary rounded-full animate-spin mb-8" />
        <p className="text-2xl font-black uppercase tracking-tighter animate-pulse">Syncing with AI...</p>
      </div>
    );
  }

  if (status === 'entry') {
    return (
        <div className="min-h-screen bg-white flex items-center justify-center p-6">
            <div className="max-w-xl w-full neo-brutal bg-white p-12 rounded-[3rem]">
                <div className="text-center space-y-8">
                    <div className="bg-primary h-20 w-20 rounded-2xl neo-brutal flex items-center justify-center mx-auto text-white">
                        <BrainCircuit size={40} />
                    </div>
                    <div className="space-y-2">
                        <h1 className="text-4xl font-black uppercase tracking-tighter leading-none">Ready to Begin?</h1>
                        <p className="text-black/40 font-bold uppercase tracking-widest text-xs">AI-Powered Skill Assessment</p>
                    </div>

                    <div className="grid gap-4 py-4">
                        {[
                           { icon: <ShieldCheck size={20} />, text: "Quiet environment is best" },
                           { icon: <Volume2 size={20} />, text: "Turn up your volume" },
                           { icon: <Mic size={20} />, text: "Allow microphone access" }
                        ].map((item, i) => (
                           <div key={i} className="flex items-center gap-4 bg-black/5 p-5 rounded-2xl font-bold uppercase tracking-tight text-sm">
                             <div className="text-primary">{item.icon}</div>
                             {item.text}
                           </div>
                        ))}
                    </div>

                    <button 
                        className="w-full h-18 py-6 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-lg rounded-2xl hover:bg-black transition-all"
                        onClick={handleStartInterview}
                    >
                        Enter Interview Room
                    </button>
                </div>
            </div>
        </div>
    );
  }

  if (status === 'finished') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white p-6">
        <div className="max-w-md w-full text-center space-y-10">
          <div className="h-24 w-24 bg-accent neo-brutal rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="h-12 w-12 text-black" />
          </div>
          <div className="space-y-4">
            <h1 className="text-5xl font-black uppercase tracking-tighter leading-none">Session <br /> Complete</h1>
            <p className="text-black/40 font-bold uppercase tracking-widest text-xs">Your responses are being analyzed</p>
          </div>
          <button 
            className="w-full h-16 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-sm rounded-2xl"
            onClick={() => navigate('/profile')}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans">
      <header className="p-8 flex items-center justify-between border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="flex items-center gap-4">
            <div className="bg-primary h-12 w-12 rounded-xl neo-brutal flex items-center justify-center text-white">
                <BrainCircuit size={28} />
            </div>
            <div>
              <p className="font-black uppercase tracking-tighter leading-none">Interview Room</p>
              <p className="text-[10px] font-bold text-black/40 uppercase tracking-widest mt-1">Session: #{sessionId.substring(0, 8)}</p>
            </div>
        </div>

        <div className="flex items-center gap-8 w-full max-w-md mx-12">
            <div className="flex-1 space-y-2">
                <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-black/40">
                    <span>Question {currentQuestion?.question_number || 1} of 5</span>
                </div>
                <div className="h-4 w-full bg-black/5 rounded-full border-2 border-black overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-500" 
                      style={{ width: `${(currentQuestion?.question_number || 1) * 20}%` }}
                    />
                </div>
            </div>
        </div>

        <div className="flex items-center gap-4">
            {isRecording && (
                <div className="flex items-center gap-3 bg-secondary px-6 py-3 rounded-2xl neo-brutal border-2 border-black">
                    <Timer className="h-5 w-5 text-black animate-pulse" />
                    <span className="font-black text-sm text-black">00:{timeLeft.toString().padStart(2, '0')}</span>
                </div>
            )}
            <button 
              className="h-12 w-12 neo-brutal bg-white flex items-center justify-center hover:bg-black hover:text-white transition-all rounded-xl"
              onClick={handleEndEarly} 
              disabled={ending}
            >
                <LogOut size={20} />
            </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-8 relative">
        <div className="max-w-4xl w-full z-10 space-y-16">
          <div className="flex flex-col items-center gap-10">
            <div className="relative">
              <div className={`absolute -inset-8 bg-primary/20 rounded-full blur-3xl transition-opacity duration-1000 ${status === 'speaking' ? 'opacity-100' : 'opacity-0'}`} />
              <div className={`h-40 w-40 neo-brutal bg-white rounded-full flex items-center justify-center border-4 border-black transition-all duration-500 ${status === 'speaking' ? 'scale-110 shadow-[8px_8px_0px_0px_rgba(110,86,207,1)]' : ''}`}>
                <div className={`h-32 w-32 rounded-full bg-black/5 flex items-center justify-center font-black text-4xl uppercase tracking-tighter ${status === 'speaking' ? 'animate-pulse text-primary' : 'text-black/20'}`}>
                  AI
                </div>
              </div>
            </div>

            <div className="neo-brutal bg-white p-12 rounded-[3rem] w-full min-h-[200px] flex items-center justify-center text-center">
              <p className="text-3xl md:text-5xl font-black uppercase tracking-tighter leading-tight">
                {status === 'processing' ? 'Thinking...' : currentQuestion?.text}
              </p>
            </div>
          </div>

          <div className="flex flex-col items-center gap-8">
            {!recordedBlob ? (
                <div className="flex flex-col items-center gap-6">
                    <button 
                        className={`h-28 w-28 rounded-full neo-brutal flex items-center justify-center transition-all duration-300 ${isRecording ? 'bg-primary text-white scale-110' : 'bg-accent text-black hover:scale-105'}`}
                        disabled={status !== 'listening' && !isRecording}
                        onClick={isRecording ? () => stopRecording(false) : startRecording}
                    >
                        {isRecording ? <Square size={36} fill="currentColor" /> : <Mic size={36} />}
                    </button>
                    <p className="text-black/40 font-black uppercase tracking-widest text-[10px]">
                        {isRecording ? "Stop Recording" : "Speak your answer"}
                    </p>
                </div>
            ) : (
                <div className="flex flex-col items-center gap-8">
                    <div className="flex items-center gap-6">
                        <button 
                            className="h-16 px-10 neo-brutal bg-white text-black font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-black/5 flex items-center gap-3"
                            onClick={() => setRecordedBlob(null)}
                        >
                            <Trash2 size={18} /> Redo
                        </button>
                        <button 
                            className="h-16 px-12 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-xs rounded-2xl hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center gap-3"
                            onClick={handleSubmit}
                        >
                            <Send size={18} /> Submit
                        </button>
                    </div>
                </div>
            )}

            {status === 'processing' && (
                <div className="flex items-center gap-3 text-primary font-black uppercase tracking-widest text-[10px] animate-pulse">
                    <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    AI is analyzing...
                </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default InterviewSession;
