import { FileText, Target, Mic2, FileCheck, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const features = [
  {
    title: "Parsing Protocol",
    description: "Deep-learning extraction engine that maps talent trajectories, not just keywords.",
    icon: FileText,
    color: "bg-primary",
  },
  {
    title: "Bias-Elimination",
    description: "Architectural neural networks designed for pure meritocratic evaluation.",
    icon: Target,
    color: "bg-secondary",
  },
  {
    title: "Adaptive Discourse",
    description: "Async text-based interviews that evolve based on candidate responses.",
    icon: Mic2,
    color: "bg-accent",
  },
  {
    title: "Synthesis Engine",
    description: "Data-dense intelligence reports providing surgical insights on every candidate.",
    icon: FileCheck,
    color: "bg-destructive",
  }
];

export const Features = () => {
  return (
    <section id="features" className="py-24 md:py-32 bg-white px-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-20 text-center flex flex-col items-center">
          <div className="neo-pill bg-secondary text-black text-xs uppercase tracking-widest mb-6">
            Features & Capabilities
          </div>
          <h2 className="text-5xl md:text-7xl font-black uppercase tracking-tighter mb-6">The Next-Gen Hiring Stack.</h2>
          <p className="text-xl text-black/60 max-w-2xl font-bold leading-tight">
            Everything you need to automate your hiring pipeline, eliminate bias, and find the perfect fit for your team.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="neo-brutal bg-white p-8 rounded-[2rem] flex flex-col group"
            >
              <div className={cn(
                "h-16 w-16 rounded-2xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center mb-8 group-hover:translate-x-[-2px] group-hover:translate-y-[-2px] transition-all",
                feature.color
              )}>
                <feature.icon className="h-8 w-8 text-black" />
              </div>
              <h3 className="text-2xl font-black uppercase tracking-tighter mb-4">{feature.title}</h3>
              <p className="text-black/60 font-bold leading-tight mb-8">
                {feature.description}
              </p>
              
              <div className="mt-auto space-y-3">
                {["Enterprise ready", "99.9% accuracy"].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-black/40">
                    <CheckCircle2 size={14} className="text-black" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
