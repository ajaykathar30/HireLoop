import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Mic,
  CheckCircle2,
  Volume2,
  BrainCircuit,
  Timer,
  LogOut,
  ShieldCheck,
  Loader2,
} from 'lucide-react';
import { interviewApi } from '../lib/api';
import api from '../lib/api';
import toast from 'react-hot-toast';

/* ─── Constants ─────────────────────────────────────────── */
const MAX_RECORDING_MS   = 30_000; // hard cap per answer
const SILENCE_THRESHOLD  = 12;     // RMS amplitude below this = silence
const SILENCE_DURATION_MS = 2500;  // how long silence must persist to auto-stop

/* ─── Animated waveform bars ────────────────────────────── */
const WaveformBars = ({ active, analyserRef }) => {
  const canvasRef = useRef(null);
  const rafRef    = useRef(null);

  useEffect(() => {
    if (!active || !analyserRef?.current) return;
    const canvas  = canvasRef.current;
    const ctx     = canvas.getContext('2d');
    const analyser = analyserRef.current;
    const bufLen   = analyser.frequencyBinCount;
    const dataArr  = new Uint8Array(bufLen);

    const draw = () => {
      rafRef.current = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArr);

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const barCount = 40;
      const barW     = canvas.width / barCount;
      const step     = Math.floor(bufLen / barCount);

      for (let i = 0; i < barCount; i++) {
        const val    = dataArr[i * step] / 255;
        const barH   = Math.max(4, val * canvas.height);
        const x      = i * barW + barW * 0.1;
        const y      = (canvas.height - barH) / 2;
        const alpha  = 0.5 + val * 0.5;
        ctx.fillStyle = `rgba(110,86,207,${alpha})`;
        ctx.beginPath();
        ctx.roundRect(x, y, barW * 0.8, barH, 3);
        ctx.fill();
      }
    };

    draw();
    return () => cancelAnimationFrame(rafRef.current);
  }, [active, analyserRef]);

  if (!active) return null;
  return (
    <canvas
      ref={canvasRef}
      width={280}
      height={60}
      className="rounded-2xl"
    />
  );
};

/* ─── Pulsing mic bars (user recording visual) ───────────── */
const MicBars = () => (
  <div className="flex items-end justify-center gap-1 h-10">
    {[0.4, 0.7, 1.0, 0.7, 0.5, 0.9, 0.6, 1.0, 0.4, 0.8].map((h, i) => (
      <div
        key={i}
        className="w-1.5 bg-primary rounded-full"
        style={{
          height: `${h * 100}%`,
          animation: `bounce 0.8s ease-in-out ${i * 0.08}s infinite alternate`,
        }}
      />
    ))}
  </div>
);

/* ══════════════════════════════════════════════════════════ */
const InterviewSession = () => {
  const { sessionId } = useParams();
  const navigate      = useNavigate();

  const [currentQuestion, setCurrentQuestion] = useState(null);
  /* status flow:
     entry → loading → speaking → listening → processing → finished */
  const [status,    setStatus]    = useState('entry');
  const [timeLeft,  setTimeLeft]  = useState(MAX_RECORDING_MS / 1000);
  const [countdown, setCountdown] = useState(null); // 3-2-1 before recording
  const [ending,    setEnding]    = useState(false);

  /* refs */
  const mediaRecorderRef  = useRef(null);
  const audioChunksRef    = useRef([]);
  const timerRef          = useRef(null);
  const silenceRef        = useRef(null);   // silence timer
  const audioPlayerRef    = useRef(new Audio());
  const audioCtxRef       = useRef(null);
  const analyserRef       = useRef(null);   // for AI waveform
  const micAnalyserRef    = useRef(null);   // for silence detection
  const micSourceRef      = useRef(null);
  const silenceStartRef   = useRef(null);
  const statusRef         = useRef('entry');
  const audioSrcConnectedRef = useRef(false);  // guard: createMediaElementSource once only


  // Keep statusRef in sync so callbacks always see fresh value
  const updateStatus = useCallback((s) => {
    statusRef.current = s;
    setStatus(s);
  }, []);

  /* ── cleanup on unmount ──────────────────────────────────── */
  useEffect(() => {
    return () => {
      clearInterval(timerRef.current);
      clearInterval(silenceRef.current);
      audioCtxRef.current?.close();
      if (audioPlayerRef.current._blobUrl) {
        URL.revokeObjectURL(audioPlayerRef.current._blobUrl);
      }
      audioPlayerRef.current.pause();
    };
  }, []);

  /* ── status effect: auto-start recording after speaking ends ─ */
  useEffect(() => {
    if (status === 'listening') {
      startCountdownThenRecord();
    }
  }, [status]);

  /* ─── 1. Start Interview ─────────────────────────────────── */
  const handleStartInterview = async () => {
    try {
      updateStatus('loading');
      // Request mic permission up-front before any audio context
      await navigator.mediaDevices.getUserMedia({ audio: true });
      const response = await interviewApi.start(sessionId);
      setCurrentQuestion(response.data);
      await playQuestionAudio(response.data.question_number);
    } catch (err) {
      const detail = err?.message || String(err);
      console.error('Start interview failed:', detail);
      toast.error('Failed to join interview room');
      navigate('/profile');
    }
  };

  /* ─── 2. Play AI question audio ─────────────────────────── */
  const playQuestionAudio = async (questionNumber) => {
    if (!questionNumber) { updateStatus('listening'); return; }

    updateStatus('speaking');
    const idx = questionNumber - 1;

    try {
      const response = await api.get(
        `/interviews/${sessionId}/stream-audio/${idx}`,
        { responseType: 'blob' }
      );

      if (!response.data || response.data.size === 0) {
        console.error('Audio blob empty — TTS failed');
        toast('Could not load audio. Read the question on screen.', { icon: '🔇' });
        updateStatus('listening');
        return;
      }

      if (audioPlayerRef.current._blobUrl) {
        URL.revokeObjectURL(audioPlayerRef.current._blobUrl);
      }

      const blobUrl = URL.createObjectURL(response.data);
      audioPlayerRef.current._blobUrl = blobUrl;
      audioPlayerRef.current.src      = blobUrl;

      /* hook AudioContext → analyser for waveform animation (first time only) */
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioCtxRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
      }
      if (audioCtxRef.current.state === 'suspended') {
        await audioCtxRef.current.resume();
      }
      // createMediaElementSource must only be called ONCE per Audio element
      if (!audioSrcConnectedRef.current) {
        const src = audioCtxRef.current.createMediaElementSource(audioPlayerRef.current);
        src.connect(analyserRef.current);
        analyserRef.current.connect(audioCtxRef.current.destination);
        audioSrcConnectedRef.current = true;
      }

      audioPlayerRef.current.onended = () => updateStatus('listening');
      audioPlayerRef.current.onerror = () => {
        toast('Audio playback error. Read question on screen.', { icon: '⚠️' });
        updateStatus('listening');
      };

      await audioPlayerRef.current.play();
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || String(err);
      console.error('playQuestionAudio failed:', detail);
      toast('Could not load audio. Read question on screen.', { icon: '🔇' });
      updateStatus('listening');
    }
  };

  /* ─── 3. 3-2-1 Countdown then auto-record ───────────────── */
  const startCountdownThenRecord = () => {
    let count = 8;
    setCountdown(count);
    const iv = setInterval(() => {
      count -= 1;
      if (count <= 0) {
        clearInterval(iv);
        setCountdown(null);
        startRecording();
      } else {
        setCountdown(count);
      }
    }, 1000);
  };

  /* ─── 4. Auto-recording with silence detection ───────────── */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      /* build mic analyser for silence detection */
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtxRef.current.state === 'suspended') {
        await audioCtxRef.current.resume();
      }
      micAnalyserRef.current = audioCtxRef.current.createAnalyser();
      micAnalyserRef.current.fftSize = 256;
      micSourceRef.current = audioCtxRef.current.createMediaStreamSource(stream);
      micSourceRef.current.connect(micAnalyserRef.current);

      /* MediaRecorder */
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current   = [];
      mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
      mediaRecorderRef.current.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        submitAnswer(blob);
      };
      mediaRecorderRef.current.start(100); // collect chunks every 100ms
      updateStatus('listening'); // keep listening state, recording underway

      /* Hard max-time timer */
      setTimeLeft(MAX_RECORDING_MS / 1000);
      clearInterval(timerRef.current);
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(timerRef.current);
            stopRecording();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      /* Silence detection loop */
      silenceStartRef.current = null;
      const silenceBuf = new Uint8Array(micAnalyserRef.current.frequencyBinCount);
      silenceRef.current = setInterval(() => {
        if (!micAnalyserRef.current) return;
        micAnalyserRef.current.getByteTimeDomainData(silenceBuf);
        // compute RMS
        let sum = 0;
        for (let i = 0; i < silenceBuf.length; i++) {
          const v = (silenceBuf[i] - 128) / 128;
          sum += v * v;
        }
        const rms = Math.sqrt(sum / silenceBuf.length) * 256;

        if (rms < SILENCE_THRESHOLD) {
          if (!silenceStartRef.current) silenceStartRef.current = Date.now();
          else if (Date.now() - silenceStartRef.current > SILENCE_DURATION_MS) {
            clearInterval(silenceRef.current);
            stopRecording();
          }
        } else {
          silenceStartRef.current = null; // reset on sound
        }
      }, 100);

    } catch (err) {
      toast.error('Microphone access required for the interview');
      updateStatus('listening');
    }
  };

  const stopRecording = () => {
    clearInterval(timerRef.current);
    clearInterval(silenceRef.current);
    micSourceRef.current?.disconnect();
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    updateStatus('processing');
  };

  /* ─── 5. Submit answer & loop ────────────────────────────── */
  const submitAnswer = async (blob) => {
    updateStatus('processing');
    try {
      const response = await interviewApi.submitAnswer(sessionId, blob, false);
      if (response.data.status === 'completed') {
        updateStatus('finished');
      } else {
        setCurrentQuestion(response.data);
        await playQuestionAudio(response.data.question_number);
      }
    } catch (err) {
      console.error('Submit answer failed:', err);
      toast.error('Answer submission failed. Retrying…');
      // Retry after 2s
      setTimeout(() => updateStatus('listening'), 2000);
    }
  };

  /* ─── 6. End Early ───────────────────────────────────────── */
  const handleEndEarly = async () => {
    if (!window.confirm('End interview now? This will finalise your session.')) return;
    setEnding(true);
    try {
      stopRecording();
      await interviewApi.submitAnswer(sessionId, null, false, true);
      updateStatus('finished');
    } catch (err) {
      toast.error('Failed to end session');
    } finally {
      setEnding(false);
    }
  };

  /* ══════ RENDER ══════════════════════════════════════════ */

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-white">
        <div className="h-20 w-20 border-8 border-black border-t-primary rounded-full animate-spin mb-8" />
        <p className="text-2xl font-black uppercase tracking-tighter animate-pulse">Syncing with AI…</p>
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
              <p className="text-black/40 font-bold uppercase tracking-widest text-xs">AI-Powered Voice Interview — Fully Automatic</p>
            </div>

            <div className="grid gap-4 py-4">
              {[
                { icon: <ShieldCheck size={20} />, text: 'Quiet environment is best' },
                { icon: <Volume2 size={20} />,     text: 'Turn up your volume' },
                { icon: <Mic size={20} />,         text: 'Allow microphone access' },
                { icon: <Timer size={20} />,        text: 'Speak your answer — AI detects silence & moves on' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4 bg-black/5 p-5 rounded-2xl font-bold uppercase tracking-tight text-sm">
                  <div className="text-primary">{item.icon}</div>
                  {item.text}
                </div>
              ))}
            </div>

            <button
              className="w-full py-6 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-lg rounded-2xl hover:bg-black transition-all"
              onClick={handleStartInterview}
            >
              Start AI Interview
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
            <h1 className="text-5xl font-black uppercase tracking-tighter leading-none">Session<br />Complete</h1>
            <p className="text-black/40 font-bold uppercase tracking-widest text-xs">Your responses are being analysed by AI</p>
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

  /* ── Main interview UI ───────────────────────────────────── */
  const isSpeaking    = status === 'speaking';
  const isListening   = status === 'listening';
  const isProcessing  = status === 'processing';
  const isRecording   = isListening && !countdown;

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans" style={{ '--primary': '110 86 207' }}>
      {/* ── Header ── */}
      <header className="p-6 flex items-center justify-between border-b-4 border-black bg-white sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="bg-primary h-12 w-12 rounded-xl neo-brutal flex items-center justify-center text-white">
            <BrainCircuit size={28} />
          </div>
          <div>
            <p className="font-black uppercase tracking-tighter leading-none">Interview Room</p>
            <p className="text-[10px] font-bold text-black/40 uppercase tracking-widest mt-1">
              Session #{sessionId.substring(0, 8)}
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="flex-1 max-w-sm mx-10 space-y-1">
          <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-black/40">
            <span>Question {currentQuestion?.question_number || 1} of 5</span>
            <span>{(currentQuestion?.question_number || 1) * 20}%</span>
          </div>
          <div className="h-3 w-full bg-black/5 rounded-full border-2 border-black overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-700 rounded-full"
              style={{ width: `${(currentQuestion?.question_number || 1) * 20}%` }}
            />
          </div>
        </div>

        {/* Timer + exit */}
        <div className="flex items-center gap-3">
          {isRecording && (
            <div className="flex items-center gap-2 bg-red-50 border-2 border-red-400 px-4 py-2 rounded-2xl">
              <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
              <span className="font-black text-sm text-red-600">
                {String(Math.floor(timeLeft / 60)).padStart(2, '0')}:{String(timeLeft % 60).padStart(2, '0')}
              </span>
            </div>
          )}
          <button
            className="h-12 w-12 neo-brutal bg-white flex items-center justify-center hover:bg-black hover:text-white transition-all rounded-xl"
            onClick={handleEndEarly}
            disabled={ending}
            title="End interview early"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col items-center justify-center p-8 gap-12">
        {/* AI Avatar + Waveform */}
        <div className="flex flex-col items-center gap-6">
          <div className="relative">
            {/* Glow rings */}
            <div className={`absolute -inset-10 rounded-full transition-all duration-1000 ${
              isSpeaking ? 'bg-primary/15 blur-3xl opacity-100' : 'opacity-0'
            }`} />
            <div className={`absolute -inset-6 rounded-full border-2 border-primary/30 transition-all duration-500 ${
              isSpeaking ? 'scale-110 opacity-100 animate-ping' : 'opacity-0'
            }`} />

            {/* Avatar circle */}
            <div className={`relative h-36 w-36 neo-brutal rounded-full flex items-center justify-center border-4 border-black transition-all duration-500 ${
              isSpeaking ? 'bg-primary scale-110' :
              isProcessing ? 'bg-secondary' :
              isRecording  ? 'bg-accent' : 'bg-white'
            }`}>
              {isProcessing ? (
                <Loader2 size={48} className="text-black animate-spin" />
              ) : (
                <span className={`font-black text-4xl uppercase tracking-tighter ${
                  isSpeaking ? 'text-white' : 'text-black/30'
                }`}>
                  AI
                </span>
              )}
            </div>
          </div>

          {/* Waveform canvas — only during AI speaking */}
          <div className="h-16 flex items-center justify-center">
            {isSpeaking ? (
              <WaveformBars active={true} analyserRef={analyserRef} />
            ) : isRecording ? (
              <MicBars />
            ) : (
              <div className="h-10 w-64 rounded-2xl bg-black/5 flex items-center justify-center">
                <span className="text-[10px] font-black uppercase tracking-widest text-black/30">
                  {isProcessing ? 'Processing your answer…' :
                   countdown   ? `Recording in ${countdown}…` :
                                 'Initialising…'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Question card */}
        <div className="w-full max-w-3xl neo-brutal bg-white p-10 rounded-[2.5rem] min-h-[160px] flex items-center justify-center text-center">
          {isProcessing ? (
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-3 text-primary">
                <Loader2 className="h-6 w-6 animate-spin" />
                <span className="font-black uppercase tracking-widest text-sm">Analysing your answer…</span>
              </div>
            </div>
          ) : (
            <p className="text-2xl md:text-4xl font-black uppercase tracking-tighter leading-tight">
              {currentQuestion?.text || '…'}
            </p>
          )}
        </div>

        {/* Status label */}
        <div className="flex flex-col items-center gap-2">
          {isSpeaking && (
            <div className="flex items-center gap-2 text-primary font-black uppercase tracking-widest text-xs animate-pulse">
              <Volume2 size={14} />
              AI is speaking — listen carefully
            </div>
          )}
          {countdown && (
            <div className="flex flex-col items-center gap-1">
              <div className="h-16 w-16 neo-brutal bg-primary text-white rounded-full flex items-center justify-center text-3xl font-black animate-pulse">
                {countdown}
              </div>
              <p className="text-xs font-black uppercase tracking-widest text-black/40">Speak in…</p>
            </div>
          )}
          {isRecording && (
            <div className="flex items-center gap-2 bg-red-50 border-2 border-red-300 px-6 py-3 rounded-2xl">
              <Mic size={16} className="text-red-500 animate-pulse" />
              <span className="text-red-600 font-black uppercase tracking-widest text-xs">
                Listening — speak your answer, AI will detect when you stop
              </span>
            </div>
          )}
        </div>
      </main>

      {/* CSS for mic bars bounce */}
      <style>{`
        @keyframes bounce {
          from { transform: scaleY(0.4); }
          to   { transform: scaleY(1); }
        }
      `}</style>
    </div>
  );
};

export default InterviewSession;
