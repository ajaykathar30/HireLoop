import { Button } from "./Button";
import { Star } from "lucide-react";

export const FinalCTA = () => {
  return (
    <section className="py-24 md:py-32 bg-[#FFFDF5] overflow-hidden relative border-b-2 border-[#1E293B]">
      <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
        <div className="inline-block bg-tertiary p-4 rounded-full border-2 border-[#1E293B] shadow-pop mb-8 rotate-[-12deg] animate-pulse">
           <Star className="text-white fill-white h-8 w-8" />
        </div>
        
        <h2 className="text-6xl md:text-8xl font-black text-[#1E293B] mb-10 leading-none tracking-tighter">
          Ready to build your <br /> dream team?
        </h2>
        
        <p className="text-2xl font-bold text-slate-500 mb-12 max-w-2xl mx-auto italic">
          Join hundreds of companies using HireLoop to automate their hiring. It's time to level up!
        </p>
        
        <Button size="lg" className="px-16 text-2xl h-20 shadow-pop-lg" variant="candy">
          Get Started Now
        </Button>
      </div>

      {/* Decorative floating shapes */}
      <div className="absolute top-0 left-0 w-64 h-64 bg-accent/10 rounded-full -translate-x-1/2 -translate-y-1/2 -z-0" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-secondary/10 rounded-[80px] rotate-45 translate-x-1/3 translate-y-1/3 -z-0" />
      <div className="absolute top-1/2 right-10 w-12 h-12 bg-quaternary border-2 border-[#1E293B] shadow-pop rotate-12 hidden lg:block" />
      <div className="absolute top-1/3 left-20 w-16 h-16 bg-tertiary rounded-full border-2 border-[#1E293B] shadow-pop hidden lg:block" />
    </section>
  );
};
