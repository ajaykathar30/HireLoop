import { Button } from "./ui/button";
import { Sparkles, ArrowRight, Play, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

export const Hero = () => {
  return (
    <section className="relative pt-10 pb-32 overflow-hidden px-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left Side */}
        <div className="flex flex-col items-start text-left">
          <div className="neo-pill bg-accent text-black text-xs uppercase tracking-widest mb-10 flex items-center gap-2">
            <Sparkles size={14} className="fill-current" />
            AI-Powered Recruitment Protocol
          </div>
          
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-black tracking-tighter text-black leading-[0.85] mb-8 uppercase">
            Hire <br />
            Smarter. <br />
            Let AI Do the <br />
            <span className="text-primary relative inline-block">
              Lifting.
              <svg className="absolute -bottom-6 left-0 w-full h-8 text-secondary" viewBox="0 0 100 20" preserveAspectRatio="none">
                <path d="M0 10 Q 12.5 0, 25 10 T 50 10 T 75 10 T 100 10" stroke="currentColor" strokeWidth="8" fill="transparent" strokeLinecap="round" />
              </svg>
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-black font-bold max-w-xl mb-12 leading-tight opacity-70">
            From parsing to adaptive interviews—build your dream team autonomously. It's like magic, but for hiring!
          </p>
          
          <div className="flex flex-wrap gap-6">
            <button className="neo-brutal bg-primary text-white px-10 h-20 rounded-[2rem] font-black uppercase tracking-widest text-lg flex items-center gap-3 group">
              Start Hiring
              <ArrowRight className="group-hover:translate-x-2 transition-transform" />
            </button>
            <button className="neo-brutal bg-white text-black px-10 h-20 rounded-[2rem] font-black uppercase tracking-widest text-lg">
              Apply as Candidate
            </button>
          </div>
        </div>

        {/* Right Side - Neo Brutalist Card Illustration */}
        <div className="relative flex items-center justify-center">
          {/* Main Card */}
          <div className="w-[450px] h-[550px] neo-brutal bg-white rounded-[3rem] p-10 flex flex-col items-center justify-center gap-8 relative z-10">
             <div className="grid grid-cols-2 gap-6 w-full">
                <div className="aspect-square bg-primary rounded-3xl border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"></div>
                <div className="aspect-square bg-secondary rounded-full border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"></div>
                <div className="aspect-square bg-accent rounded-full border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"></div>
                <div className="aspect-square bg-destructive rounded-3xl border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"></div>
             </div>
             
             {/* Decorative Blobs */}
             <div className="absolute -top-10 -right-10 w-40 h-40 bg-secondary/30 blur-3xl rounded-full -z-10"></div>
             <div className="absolute -bottom-10 -left-10 w-60 h-60 bg-primary/20 blur-3xl rounded-full -z-10"></div>
          </div>
          
          {/* Floating Element 1 */}
          <div className="absolute -top-12 -left-12 neo-brutal bg-white p-6 rounded-2xl animate-bounce duration-[3000ms]">
             <div className="h-4 w-24 bg-black/10 rounded-full mb-3"></div>
             <div className="h-4 w-16 bg-black/10 rounded-full"></div>
          </div>

          {/* Floating Element 2 */}
          <div className="absolute -bottom-8 -right-8 neo-brutal bg-accent p-6 rounded-2xl rotate-6 animate-pulse">
             <CheckCircle2 size={32} className="text-black" />
          </div>
        </div>
      </div>
    </section>
  );
};
