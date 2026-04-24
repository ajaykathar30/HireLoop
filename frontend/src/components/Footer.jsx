import { Sparkles, Twitter, Linkedin, Github, Mail } from "lucide-react";
import { Link } from "react-router-dom";

export const Footer = () => {
  return (
    <footer className="border-t bg-muted/30 py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-1 space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="bg-primary p-1 rounded-lg">
                <Sparkles className="text-primary-foreground fill-primary-foreground" size={16} />
              </div>
              <span className="text-lg font-bold tracking-tight">HireLoop</span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered job portal connecting the best talent with top companies through intelligent matching and seamless interviews.
            </p>
          </div>
          
          <div>
            <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/candidate-home" className="hover:text-primary transition-colors">Find Jobs</Link></li>
              <li><Link to="/" className="hover:text-primary transition-colors">Post a Job</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">AI Matching</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">Pricing</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="#" className="hover:text-primary transition-colors">Career Blog</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">Interview Prep</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">Help Center</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">API Docs</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-sm uppercase tracking-wider mb-4">Connect</h4>
            <div className="flex gap-4 mb-4">
              <a href="#" className="p-2 bg-background rounded-full border hover:bg-muted transition-all"><Twitter size={18} /></a>
              <a href="#" className="p-2 bg-background rounded-full border hover:bg-muted transition-all"><Linkedin size={18} /></a>
              <a href="#" className="p-2 bg-background rounded-full border hover:bg-muted transition-all"><Github size={18} /></a>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Mail size={16} />
              <span>hello@hireloop.ai</span>
            </div>
          </div>
        </div>
        
        <div className="pt-8 border-t flex flex-col md:row items-center justify-between gap-4">
          <p className="text-xs text-muted-foreground font-medium">
            © {new Date().getFullYear()} HireLoop AI. All rights reserved.
          </p>
          <div className="flex gap-6 text-xs text-muted-foreground font-medium">
             <Link to="#" className="hover:text-primary transition-colors">Privacy Policy</Link>
             <Link to="#" className="hover:text-primary transition-colors">Terms of Service</Link>
             <Link to="#" className="hover:text-primary transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
