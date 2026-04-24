import { Button } from "./ui/button";
import { Sparkles, ArrowRight, Play, CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

export const Hero = () => {
  return (
    <section className="relative overflow-hidden pt-16 pb-24 md:pt-24 md:pb-32 bg-background">
      {/* Background decoration */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-blue-500/5 rounded-full blur-[100px]" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <Sparkles size={14} className="text-primary fill-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-primary">AI-Powered Recruitment 2.0</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tight text-foreground mb-8 max-w-4xl leading-[1.1] animate-in fade-in slide-in-from-bottom-6 duration-700">
          Hire smarter. Let AI <br />
          do the <span className="text-primary relative italic">
            heavy lifting.
            <svg className="absolute -bottom-2 left-0 w-full h-3 text-primary/30" viewBox="0 0 100 10" preserveAspectRatio="none">
              <path d="M0 5 Q 25 0, 50 5 T 100 5" stroke="currentColor" strokeWidth="4" fill="transparent" />
            </svg>
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000">
          From intelligent resume parsing to adaptive AI interviews—build your dream team autonomously. HireLoop is the future of talent acquisition.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-16 animate-in fade-in slide-in-from-bottom-10 duration-1000">
          <Button size="lg" className="h-12 px-8 text-base font-bold shadow-lg shadow-primary/20 group">
            Start Hiring Now
            <ArrowRight size={18} className="ml-2 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button variant="outline" size="lg" className="h-12 px-8 text-base font-bold bg-background border-muted-foreground/20">
            <Play size={18} className="mr-2 fill-current" />
            Watch Demo
          </Button>
        </div>

        {/* Trust markers */}
        <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale animate-in fade-in duration-1000 delay-500">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tighter">
            <div className="w-8 h-8 bg-foreground rounded-lg" /> TechFlow
          </div>
          <div className="flex items-center gap-2 font-bold text-xl tracking-tighter">
             <div className="w-8 h-8 bg-foreground rounded-full" /> DesignCo
          </div>
          <div className="flex items-center gap-2 font-bold text-xl tracking-tighter">
             <div className="w-8 h-8 bg-foreground rounded-md" /> GrowthKit
          </div>
          <div className="flex items-center gap-2 font-bold text-xl tracking-tighter">
             <div className="w-8 h-8 bg-foreground rounded-sm" /> TechNova
          </div>
        </div>
      </div>
    </section>
  );
};
