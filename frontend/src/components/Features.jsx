import { FileText, Target, Mic2, FileCheck } from "lucide-react";
import { cn } from "../lib/utils";

const features = [
  {
    title: "Parsing Protocol",
    description: "Deep-learning extraction engine that maps talent trajectories, not just keywords.",
    icon: FileText,
    color: "bg-accent",
    id: "01"
  },
  {
    title: "Bias-Elimination",
    description: "Architectural neural networks designed for pure meritocratic evaluation.",
    icon: Target,
    color: "bg-secondary",
    id: "02"
  },
  {
    title: "Adaptive Discourse",
    description: "Async text-based interviews that evolve based on candidate responses.",
    icon: Mic2,
    color: "bg-tertiary",
    id: "03"
  },
  {
    title: "Synthesis Engine",
    description: "Data-dense intelligence reports providing surgical insights on every candidate.",
    icon: FileCheck,
    color: "bg-quaternary",
    id: "04"
  }
];

export const Features = () => {
  return (
    <section id="features" className="py-24 md:py-32 bg-[#FFFDF5]">
      <div className="max-w-6xl mx-auto px-6">
        <div className="mb-20 text-center">
          <h2 className="text-5xl md:text-7xl font-black mb-6 tracking-tighter">Capabilities.</h2>
          <p className="text-xl font-bold opacity-60 max-w-2xl mx-auto">
            Everything you need to automate your hiring pipeline and find the perfect fit.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className={cn(
                "group relative p-10 bg-white border-2 border-[#1E293B] rounded-3xl shadow-pop-lg transition-all duration-300 hover:rotate-[-1deg] hover:scale-[1.02]"
              )}
            >
              {/* Half-in/half-out icon */}
              <div className={cn(
                "absolute -top-10 left-10 h-20 w-20 rounded-full border-2 border-[#1E293B] shadow-pop flex items-center justify-center group-hover:rotate-12 transition-transform",
                feature.color
              )}>
                <feature.icon className="text-white h-10 w-10" strokeWidth={3} />
              </div>
              
              <div className="mt-8">
                <span className="font-black text-6xl opacity-10 absolute top-8 right-10 leading-none">{feature.id}</span>
                <h3 className="text-3xl font-black mb-6 mt-4">{feature.title}</h3>
                <p className="text-xl font-medium leading-relaxed opacity-80">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
