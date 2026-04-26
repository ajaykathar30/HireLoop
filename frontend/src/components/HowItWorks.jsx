import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export const HowItWorks = () => {
  const steps = [
    {
      number: "01",
      title: "Define Protocol",
      description: "Map out your technical and cultural requirements via our adaptive engine.",
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      number: "02",
      title: "Autonomous Outreach",
      description: "AI conducts end-to-end adaptive discourse with potential candidates.",
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
    {
      number: "03",
      title: "Surgical Synthesis",
      description: "Receive high-density data on your top picks for final verification.",
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
    },
  ];

  return (
    <section id="how-it-works" className="py-24 md:py-32 bg-background relative overflow-hidden">
      {/* Decorative path */}
      <div className="absolute top-1/2 left-0 w-full h-0.5 border-t-2 border-dashed border-muted-foreground/10 -translate-y-1/2 hidden lg:block" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="mb-20 space-y-4">
          <Badge variant="outline" className="px-3 py-1 border-primary/20 text-primary bg-primary/5 uppercase tracking-widest text-[10px] font-bold">
            The Process
          </Badge>
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight">Three Stages of AI-Magic.</h2>
          <p className="text-lg text-muted-foreground max-w-xl font-medium leading-relaxed italic">
            Standardizing excellence through algorithmic precision. Our process is designed to be invisible but powerful.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-16 lg:gap-24">
          {steps.map((step, index) => (
            <div key={index} className="group relative flex flex-col items-start space-y-6">
              <div className={cn(
                "h-20 w-20 rounded-2xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 shadow-sm",
                step.bgColor
              )}>
                <span className={cn("text-3xl font-black", step.color)}>{step.number}</span>
              </div>
              
              <div className="space-y-3">
                <h3 className="text-2xl font-bold tracking-tight">{step.title}</h3>
                <p className="text-base font-medium text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </div>

              {/* Step indicator for mobile/tablet */}
              <div className="h-1 w-12 bg-primary/20 rounded-full md:hidden" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
