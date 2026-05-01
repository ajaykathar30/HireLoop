import { Button } from "./ui/button";
import { Sparkles, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export const FinalCTA = () => {
  return (
    <section className="py-24 md:py-40 bg-white px-4 relative">
      <div className="max-w-5xl mx-auto neo-brutal bg-primary p-12 md:p-20 rounded-[3rem] text-center relative overflow-hidden">
        {/* Decorative Circles */}
        <div className="absolute top-[-50px] right-[-50px] w-40 h-40 bg-secondary rounded-full border-4 border-black -rotate-12"></div>
        <div className="absolute bottom-[-50px] left-[-50px] w-60 h-60 bg-accent rounded-full border-4 border-black rotate-12"></div>

        <div className="relative z-10">
          <div className="neo-pill bg-white text-black text-xs uppercase tracking-widest mb-10 inline-block">
             Join 500+ teams
          </div>
          
          <h2 className="text-5xl md:text-7xl font-black text-white uppercase tracking-tighter mb-10 leading-[0.9]">
            Ready to build your <br /> <span className="text-secondary">dream team?</span>
          </h2>
          
          <p className="text-xl md:text-2xl font-bold text-white/80 mb-12 max-w-2xl mx-auto leading-tight">
            Automate your hiring, eliminate bias, and find the talent you've been searching for. It's time to level up.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button className="neo-brutal bg-white text-black px-12 h-20 rounded-[2rem] font-black uppercase tracking-widest text-lg flex items-center gap-3 group">
              Get Started Now
              <ArrowRight className="group-hover:translate-x-2 transition-transform" />
            </button>
            <button className="neo-brutal bg-black text-white px-12 h-20 rounded-[2rem] font-black uppercase tracking-widest text-lg">
              Schedule a Demo
            </button>
          </div>
          
          <p className="mt-10 text-sm font-black uppercase tracking-widest text-white/40">
            No credit card required • 14-day free trial
          </p>
        </div>
      </div>
    </section>
  );
};
