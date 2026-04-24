import { Button } from "./ui/button";
import { Sparkles, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export const FinalCTA = () => {
  return (
    <section className="py-24 md:py-32 bg-slate-900 overflow-hidden relative border-b">
      {/* Background gradients */}
      <div className="absolute top-0 left-0 w-full h-full -z-0">
        <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] translate-x-1/2 -translate-y-1/2" />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm">
           <Sparkles className="text-primary fill-primary" size={14} />
           <span className="text-[10px] font-bold uppercase tracking-widest text-white/80">Join 500+ teams</span>
        </div>
        
        <h2 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-white mb-8 leading-[1.1] tracking-tight">
          Ready to build your <br /> <span className="text-primary">dream team?</span>
        </h2>
        
        <p className="text-lg md:text-xl font-medium text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
          Automate your hiring, eliminate bias, and find the talent you've been searching for. It's time to level up your recruitment process.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" className="h-14 px-10 text-lg font-bold shadow-xl shadow-primary/20 group">
            Get Started Now
            <ArrowRight size={20} className="ml-2 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button variant="outline" size="lg" className="h-14 px-10 text-lg font-bold text-white border-white/20 hover:bg-white/5 bg-transparent">
            Schedule a Demo
          </Button>
        </div>
        
        <p className="mt-8 text-sm font-medium text-slate-500">
          No credit card required • 14-day free trial • Cancel anytime
        </p>
      </div>
    </section>
  );
};
