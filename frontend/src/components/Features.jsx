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
    iconColor: "text-blue-500",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/20"
  },
  {
    title: "Bias-Elimination",
    description: "Architectural neural networks designed for pure meritocratic evaluation.",
    icon: Target,
    iconColor: "text-purple-500",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/20"
  },
  {
    title: "Adaptive Discourse",
    description: "Async text-based interviews that evolve based on candidate responses.",
    icon: Mic2,
    iconColor: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20"
  },
  {
    title: "Synthesis Engine",
    description: "Data-dense intelligence reports providing surgical insights on every candidate.",
    icon: FileCheck,
    iconColor: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/20"
  }
];

export const Features = () => {
  return (
    <section id="features" className="py-24 md:py-32 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-16 text-center space-y-4">
          <Badge variant="outline" className="px-3 py-1 border-primary/20 text-primary bg-primary/5 uppercase tracking-widest text-[10px] font-bold">
            Features & Capabilities
          </Badge>
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight">The Next-Gen Hiring Stack.</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-medium leading-relaxed">
            Everything you need to automate your hiring pipeline, eliminate bias, and find the perfect fit for your team.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className={cn(
                "group relative overflow-hidden border-none shadow-sm hover:shadow-md transition-all duration-300 bg-background",
              )}
            >
              <div className={cn("absolute top-0 left-0 w-1 h-full opacity-50", feature.iconColor.replace('text-', 'bg-'))} />
              <CardHeader className="pb-4">
                <div className={cn(
                  "h-12 w-12 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110 duration-300",
                  feature.bgColor
                )}>
                  <feature.icon className={cn("h-6 w-6", feature.iconColor)} />
                </div>
                <CardTitle className="text-xl font-bold">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm font-medium leading-relaxed text-muted-foreground">
                  {feature.description}
                </CardDescription>
                
                <ul className="mt-6 space-y-2">
                  {["Enterprise ready", "99.9% accuracy"].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-[11px] font-bold text-muted-foreground/70 uppercase tracking-tight">
                      <CheckCircle2 size={12} className={feature.iconColor} />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
