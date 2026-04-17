import { Button } from "./Button";
import { Circle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const Navbar = () => {
  const navigate = useNavigate();

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      <nav className="bg-white border-2 border-[#1E293B] rounded-full px-8 py-3 flex items-center justify-between shadow-pop">
        <div className="flex items-center gap-2 group cursor-pointer" onClick={() => navigate('/')}>
          <div className="bg-tertiary p-1.5 rounded-lg border-2 border-[#1E293B] group-hover:rotate-12 transition-transform">
            <Circle className="text-[#1E293B] h-6 w-6 fill-white" strokeWidth={3} />
          </div>
          <span className="text-2xl font-black tracking-tight font-heading">HireLoop</span>
        </div>
        
        <div className="hidden md:flex items-center gap-10 font-bold text-fg">
          <a href="#features" className="hover:text-accent hover:scale-110 transition-all">Features</a>
          <a href="#how-it-works" className="hover:text-secondary hover:scale-110 transition-all">Process</a>
        </div>

        <div className="flex items-center gap-4">
          <Button variant="ghost" className="hidden sm:flex" showIcon={false} onClick={() => navigate('/login')}>Login</Button>
          <Button variant="primary" size="sm">Post Job</Button>
        </div>
      </nav>
    </div>
  );
};
