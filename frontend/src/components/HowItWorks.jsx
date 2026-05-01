import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export const HowItWorks = () => {
  const steps = [
    {
      number: "01",
      title: "Define Protocol",
      description: "Map out your technical and cultural requirements via our adaptive engine.",
      color: "bg-primary",
    },
    {
      number: "02",
      title: "Autonomous Outreach",
      description: "AI conducts end-to-end adaptive discourse with potential candidates.",
      color: "bg-secondary",
    },
    {
      number: "03",
      title: "Surgical Synthesis",
      description: "Receive high-density data on your top picks for final verification.",
      color: "bg-accent",
    },
  ];

  return (
    <section id="how-it-works" className="py-24 md:py-32 bg-white px-4 relative overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="mb-20 text-left flex flex-col items-start">
          <div className="neo-pill bg-accent text-black text-xs uppercase tracking-widest mb-6">
            The Process
          </div>
          <h2 className="text-5xl md:text-7xl font-black uppercase tracking-tighter mb-6">Three Stages of AI-Magic.</h2>
          <p className="text-xl text-black/60 max-w-xl font-bold leading-tight">
            Standardizing excellence through algorithmic precision. Our process is designed to be invisible but powerful.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
          {steps.map((step, index) => (
            <div key={index} className="group relative flex flex-col items-start gap-8">
              <div className={cn(
                "h-24 w-24 rounded-3xl neo-brutal flex items-center justify-center transition-all duration-300 group-hover:rotate-6",
                step.color
              )}>
                <span className="text-4xl font-black text-black">{step.number}</span>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-3xl font-black uppercase tracking-tighter">{step.title}</h3>
                <p className="text-lg font-bold text-black/60 leading-tight">
                  {step.description}
                </p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 left-32 w-32 h-2 border-t-4 border-dashed border-black" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
