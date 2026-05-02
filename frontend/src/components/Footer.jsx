import { Sparkles, Twitter, Linkedin, Github, Mail } from "lucide-react";
import { Link } from "react-router-dom";

export const Footer = () => {
  return (
    <footer className="bg-white py-20 px-4">
      <div className="max-w-7xl mx-auto neo-brutal bg-white p-12 rounded-[3rem]">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-1 space-y-6">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="bg-primary p-2 rounded-xl border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <Sparkles className="text-white fill-white" size={20} />
              </div>
              <span className="text-2xl font-black tracking-tighter uppercase">HireLoop</span>
            </Link>
            <p className="text-black font-bold leading-tight opacity-70">
              AI-powered job portal connecting the best talent with top companies through intelligent matching.
            </p>
          </div>
          
          <div>
            <h4 className="font-black text-sm uppercase tracking-widest mb-6">Product</h4>
            <ul className="space-y-3 text-sm font-bold opacity-70">
              <li><Link to="/candidate-home" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">Find Jobs</Link></li>
              <li><Link to="/" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">Post a Job</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">AI Matching</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-black text-sm uppercase tracking-widest mb-6">Resources</h4>
            <ul className="space-y-3 text-sm font-bold opacity-70">
              <li><Link to="#" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">Career Blog</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">Interview Prep</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors underline decoration-2 underline-offset-4">Help Center</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-black text-sm uppercase tracking-widest mb-6">Connect</h4>
            <div className="flex gap-4 mb-6">
              <a href="#" className="p-3 neo-brutal bg-secondary rounded-xl"><Twitter size={20} /></a>
              <a href="#" className="p-3 neo-brutal bg-accent rounded-xl"><Linkedin size={20} /></a>
              <a href="#" className="p-3 neo-brutal bg-destructive rounded-xl text-white"><Github size={20} /></a>
            </div>
            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-widest">
              <Mail size={16} />
              <span>hello@hireloop.ai</span>
            </div>
          </div>
        </div>
        
        <div className="pt-10 border-t-4 border-black flex flex-col md:row items-center justify-between gap-6">
          <p className="text-xs font-black uppercase tracking-widest opacity-40">
            © {new Date().getFullYear()} HireLoop AI. All rights reserved.
          </p>
          <div className="flex gap-8 text-xs font-black uppercase tracking-widest opacity-40">
             <Link to="#" className="hover:text-primary transition-colors">Privacy</Link>
             <Link to="#" className="hover:text-primary transition-colors">Terms</Link>
             <Link to="#" className="hover:text-primary transition-colors">Cookies</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
