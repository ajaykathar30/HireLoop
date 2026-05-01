
import React, { useState, useEffect, useRef } from 'react';
import { 
  BrainCircuit, 
  Send, 
  CheckCircle2, 
  Loader2,
  ArrowRight,
  MessageSquareText,
  Mic,
  Square,
  Volume2,
  Trash2,
  Timer
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const TestInterview = () => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [status, setStatus] = useState('entry'); // entry, loading, speaking, listening, processing, finished
  const [sessionId, setSessionId] = useState(`test-${Math.random().toString(36).substring(7)}`);
  const [history, setHistory] = useState([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [timeLeft, setTimeLeft] = useState(30);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioPlayerRef = useRef(new Audio());

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  const handleStart = async () => {
    setStatus('loading');
    try {
      const response = await axios.post(`${API_BASE_URL}/test-interview/start?session_id=${sessionId}`);
      setCurrentQuestion(response.data);
      playQuestionAudio(response.data.question_number);
    } catch (err) {
      console.error("Failed to start test interview:", err);
      toast.error("Failed to start. Make sure backend is running.");
      setStatus('entry');
    }
  };

  const playQuestionAudio = (questionNumber) => {
    setRecordedBlob(null);
    setStatus('speaking');
    const idx = questionNumber - 1;
    audioPlayerRef.current.src = `${API_BASE_URL}/test-interview/${sessionId}/stream-audio/${idx}?t=${Date.now()}`;
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
          stopRecording();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => audioChunksRef.current.push(event.data);
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(audioBlob);
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      startTimer();
    } catch (err) {
      toast.error("Microphone access required");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    setIsRecording(false);
    clearInterval(timerRef.current);
  };

  const handleSubmit = async () => {
    if (!recordedBlob) return;
    
    setStatus('processing');
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('audio_file', recordedBlob);
      
      const response = await axios.post(`${API_BASE_URL}/test-interview/submit-answer`, formData);
      
      setHistory([...history, { question: currentQuestion.text, answer: "Audio Submitted" }]);
      
      if (response.data.status === 'completed') {
        setStatus('finished');
      } else {
        setCurrentQuestion(response.data);
        playQuestionAudio(response.data.question_number);
      }
    } catch (err) {
      console.error("Submission failed:", err);
      toast.error("Submission failed.");
      setStatus('listening');
    }
  };

  if (status === 'entry') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6 font-sans">
        <div className="max-w-2xl w-full bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-12 rounded-3xl text-center space-y-8">
            <div className="bg-purple-600 h-20 w-20 rounded-2xl border-4 border-black flex items-center justify-center mx-auto text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <BrainCircuit size={40} />
            </div>
            <h1 className="text-4xl font-black uppercase tracking-tighter">STS Pipeline Test</h1>
            <p className="text-gray-500 font-bold uppercase tracking-widest text-xs">Test Audio Streaming & Voice Recognition</p>
            
            <div className="grid gap-4 py-4 text-left">
                {[
                   { icon: <Volume2 size={20} />, text: "You will HEAR the AI question" },
                   { icon: <Mic size={20} />, text: "You must SPEAK your answer" }
                ].map((item, i) => (
                   <div key={i} className="flex items-center gap-4 bg-gray-100 p-5 border-2 border-black rounded-2xl font-bold uppercase tracking-tight text-sm">
                     <div className="text-purple-600">{item.icon}</div>
                     {item.text}
                   </div>
                ))}
            </div>

            <button 
              className="w-full py-6 bg-purple-600 text-white font-black uppercase tracking-widest text-lg rounded-2xl border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:bg-black transition-all"
              onClick={handleStart}
            >
              Start STS Test
            </button>
        </div>
      </div>
    );
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white">
        <Loader2 className="h-20 w-20 text-purple-600 animate-spin mb-8" />
        <p className="text-2xl font-black uppercase tracking-tighter animate-pulse">Waking up AI...</p>
      </div>
    );
  }

  if (status === 'finished') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6">
        <div className="max-w-2xl w-full bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-12 rounded-3xl text-center space-y-8">
          <CheckCircle2 size={80} className="mx-auto text-green-500" />
          <h1 className="text-5xl font-black uppercase tracking-tighter">Test Complete</h1>
          <button 
            className="w-full py-4 bg-black text-white font-black uppercase tracking-widest text-sm rounded-xl"
            onClick={() => window.location.reload()}
          >
            Restart Test
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <header className="p-6 flex items-center justify-between border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="flex items-center gap-4">
            <div className="bg-purple-600 h-10 w-10 rounded-lg border-2 border-black flex items-center justify-center text-white">
                <BrainCircuit size={24} />
            </div>
            <p className="font-black uppercase tracking-tighter leading-none">STS Test Bench</p>
        </div>

        <div className="text-[10px] font-black uppercase tracking-widest px-4 py-2 bg-yellow-100 border-2 border-black rounded-full">
            Question {currentQuestion?.question_number || 1} of 1
        </div>
        
        {isRecording && (
            <div className="flex items-center gap-3 bg-red-100 px-6 py-2 rounded-2xl border-2 border-black">
                <Timer className="h-5 w-5 text-red-600 animate-pulse" />
                <span className="font-black text-sm">00:{timeLeft.toString().padStart(2, '0')}</span>
            </div>
        )}
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="max-w-4xl w-full space-y-16">
          <div className="flex flex-col items-center gap-10">
            <div className={`h-40 w-40 border-4 border-black rounded-full flex items-center justify-center transition-all duration-500 ${status === 'speaking' ? 'scale-110 bg-purple-100 shadow-[8px_8px_0px_0px_rgba(168,85,247,1)]' : 'bg-white'}`}>
                <div className={`text-4xl font-black ${status === 'speaking' ? 'animate-pulse text-purple-600' : 'text-gray-300'}`}>AI</div>
            </div>

            <div className="bg-white border-4 border-black p-12 rounded-[3rem] w-full text-center shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
              <p className="text-3xl md:text-4xl font-black uppercase tracking-tighter leading-tight">
                {status === 'processing' ? 'Processing Voice...' : currentQuestion?.text}
              </p>
            </div>
          </div>

          <div className="flex flex-col items-center gap-8">
            {!recordedBlob ? (
                <div className="flex flex-col items-center gap-4">
                    <button 
                        className={`h-28 w-28 rounded-full border-4 border-black flex items-center justify-center transition-all ${isRecording ? 'bg-red-500 text-white scale-110 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-purple-600 text-white hover:scale-105 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'}`}
                        disabled={status !== 'listening' && !isRecording}
                        onClick={isRecording ? stopRecording : startRecording}
                    >
                        {isRecording ? <Square size={36} fill="currentColor" /> : <Mic size={36} />}
                    </button>
                    <p className="font-black uppercase tracking-widest text-[10px] text-gray-500">
                        {isRecording ? "Stop Recording" : status === 'speaking' ? "Wait for AI to finish" : "Speak Now"}
                    </p>
                </div>
            ) : (
                <div className="flex items-center gap-6">
                    <button 
                        className="h-16 px-10 border-4 border-black bg-white font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-gray-100 flex items-center gap-3"
                        onClick={() => setRecordedBlob(null)}
                    >
                        <Trash2 size={18} /> Redo
                    </button>
                    <button 
                        className="h-16 px-12 border-4 border-black bg-purple-600 text-white font-black uppercase tracking-widest text-xs rounded-2xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[-2px] transition-all flex items-center gap-3"
                        onClick={handleSubmit}
                    >
                        <Send size={18} /> Submit Voice
                    </button>
                </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default TestInterview;
