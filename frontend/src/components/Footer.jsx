import { Circle } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-white py-16 md:py-24">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-12 mb-16">
          <div className="flex items-center gap-2 group cursor-pointer">
            <div className="bg-tertiary p-1.5 rounded-lg border-2 border-[#1E293B] group-hover:rotate-12 transition-transform">
              <Circle className="text-[#1E293B] h-6 w-6 fill-white" strokeWidth={3} />
            </div>
            <span className="text-2xl font-black tracking-tight font-heading text-[#1E293B]">HireLoop</span>
          </div>
          
          <div className="flex flex-wrap justify-center gap-8 md:gap-12 font-bold text-[#1E293B]">
             <a href="#" className="hover:text-accent transition-colors">Twitter</a>
             <a href="#" className="hover:text-secondary transition-colors">LinkedIn</a>
             <a href="#" className="hover:text-quaternary transition-colors">Privacy</a>
             <a href="#" className="hover:text-tertiary transition-colors">Terms</a>
          </div>
        </div>
        
        <div className="pt-12 border-t-2 border-[#1E293B] flex flex-col md:flex-row items-center justify-between gap-6 opacity-60 font-bold text-sm">
          <p>© {new Date().getFullYear()} HireLoop AI. All systems go! 🚀</p>
          <div className="flex gap-4">
             <div className="w-3 h-3 rounded-full bg-accent" />
             <div className="w-3 h-3 rounded-full bg-secondary" />
             <div className="w-3 h-3 rounded-full bg-tertiary" />
          </div>
        </div>
      </div>
    </footer>
  );
};
