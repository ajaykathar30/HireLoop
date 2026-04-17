import { Button } from "./Button";
import { Sparkles } from "lucide-react";

export const Hero = () => {
  return (
    <section className="relative overflow-hidden pt-6 pb-20 md:pt-10 md:pb-32 dot-grid">
      <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div className="z-10 relative">
          <div className="inline-flex items-center gap-2 bg-quaternary/20 text-fg px-4 py-1.5 rounded-full border-2 border-[#1E293B] mb-4 font-bold shadow-pop animate-bounce text-sm">
            <Sparkles size={14} className="text-quaternary fill-quaternary" />
            <span>AI-Powered Recruitment Protocol</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black leading-[0.9] tracking-tighter text-fg mb-6 pop-in">
            Hire Smarter. <br />
            Let AI Do the <span className="text-accent underline decoration-tertiary decoration-wavy underline-offset-8">Lifting.</span>
          </h1>
          
          <p className="text-xl md:text-2xl font-medium text-slate-600 mb-8 max-w-lg leading-relaxed">
            From parsing to adaptive interviews—build your dream team autonomously. It's like magic, but for hiring!
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6">
            <Button size="lg" className="px-12">Start Hiring</Button>
            <Button variant="secondary" size="lg" className="px-12" showIcon={false}>Apply as Candidate</Button>
          </div>
          
          {/* Decorative massive circle */}
          <div className="absolute -top-10 -left-10 w-32 h-32 bg-tertiary/20 rounded-full -z-10" />
        </div>

        <div className="relative h-[400px] md:h-[500px] flex items-center justify-center">
          <div className="relative w-full h-full p-8 border-2 border-[#1E293B] bg-white rounded-3xl shadow-pop-lg rotate-3 flex items-center justify-center overflow-hidden group hover:rotate-0 transition-transform duration-500">
             <div className="absolute inset-0 bg-secondary/10 opacity-50 dot-grid" />
             <div className="grid grid-cols-2 gap-6 relative z-10">
               <div className="w-24 h-24 bg-accent rounded-2xl border-2 border-[#1E293B] shadow-pop group-hover:scale-110 transition-transform" />
               <div className="w-24 h-24 bg-tertiary rounded-full border-2 border-[#1E293B] shadow-pop group-hover:scale-110 transition-transform delay-75" />
               <div className="w-24 h-24 bg-quaternary rounded-full border-2 border-[#1E293B] shadow-pop group-hover:scale-110 transition-transform delay-150" />
               <div className="w-24 h-24 bg-secondary rounded-2xl border-2 border-[#1E293B] shadow-pop group-hover:scale-110 transition-transform delay-200" />
             </div>
          </div>
          
          {/* Floating squiggles and shapes */}
          <div className="absolute -top-10 right-0 w-24 h-24 bg-secondary/20 rounded-full blur-xl" />
          <div className="absolute bottom-0 -left-10 w-32 h-32 bg-accent/20 rounded-3xl blur-xl" />
        </div>
      </div>
    </section>
  );
};
