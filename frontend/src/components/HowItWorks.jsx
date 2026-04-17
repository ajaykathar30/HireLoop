import { cn } from "../lib/utils";

export const HowItWorks = () => {
  const steps = [
    {
      number: "01",
      title: "Protocol Definition",
      description: "Map out your technical and cultural requirements via our adaptive engine.",
      color: "bg-accent",
      shape: "rounded-tr-[80px]"
    },
    {
      number: "02",
      title: "Autonomous Outreach",
      description: "AI conducts end-to-end adaptive discourse with potential candidates.",
      color: "bg-secondary",
      shape: "rounded-full"
    },
    {
      number: "03",
      title: "Surgical Synthesis",
      description: "Receive high-density data on your top picks for final verification.",
      color: "bg-tertiary",
      shape: "rounded-bl-[80px]"
    },
  ];

  return (
    <section id="how-it-works" className="py-24 md:py-32 bg-slate-50 border-y-2 border-[#1E293B]">
      <div className="max-w-6xl mx-auto px-6">
        <div className="mb-20">
          <h2 className="text-5xl md:text-7xl font-black mb-6 tracking-tighter">The Process.</h2>
          <p className="text-xl font-bold text-slate-500 max-w-xl italic">
            Standardizing excellence through algorithmic precision. Three stages of autonomous intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {steps.map((step, index) => (
            <div key={index} className="group relative">
              <div className={cn(
                "h-24 w-24 border-2 border-[#1E293B] shadow-pop flex items-center justify-center mb-8 transition-transform group-hover:rotate-12",
                step.color,
                step.shape
              )}>
                <span className="text-4xl font-black text-white">{step.number}</span>
              </div>
              <h3 className="text-2xl font-black mb-4 uppercase">{step.title}</h3>
              <p className="text-lg font-medium text-slate-500 leading-relaxed">
                {step.description}
              </p>
              
              {index < 2 && (
                 <div className="hidden md:block absolute top-12 left-full w-full h-0.5 border-t-4 border-dashed border-slate-300 -z-10 -ml-6" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
