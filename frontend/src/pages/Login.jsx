import React from 'react';
import { Button } from '../components/Button';
import { Circle, Mail, Lock, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#FFFDF5] dot-grid flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Decorative floating shapes */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-accent/10 rounded-full -z-0 animate-pulse" />
      <div className="absolute bottom-20 right-20 w-48 h-48 bg-secondary/10 rounded-[40px] rotate-12 -z-0" />
      <div className="absolute top-1/3 right-10 w-16 h-16 bg-tertiary/20 rounded-full border-2 border-[#1E293B] shadow-pop -z-0 hidden md:block" />

      {/* Back to Home */}
      <button 
        onClick={() => navigate('/')}
        className="absolute top-8 left-8 flex items-center gap-2 font-bold text-fg hover:text-accent transition-colors group"
      >
        <div className="bg-white p-2 rounded-full border-2 border-[#1E293B] shadow-pop group-hover:translate-x-[-2px] group-hover:translate-y-[-2px] transition-all">
          <ArrowLeft size={20} strokeWidth={3} />
        </div>
        <span>Back to Home</span>
      </button>

      <div className="w-full max-w-md relative z-10">
        {/* Login Card */}
        <div className="bg-white border-2 border-[#1E293B] rounded-[32px] p-8 md:p-10 shadow-pop-lg relative">
          {/* Accent decoration */}
          <div className="absolute -top-4 -right-4 w-12 h-12 bg-secondary border-2 border-[#1E293B] rounded-xl shadow-pop rotate-12 flex items-center justify-center">
            <Lock className="text-white" size={20} strokeWidth={3} />
          </div>

          <h2 className="text-3xl font-black mb-2 text-fg">Welcome Back!</h2>
          <p className="font-bold text-slate-500 mb-8 italic">Ready to find some magic?</p>

          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-2">
              <label className="block text-sm font-black uppercase tracking-widest text-fg ml-1">Email Address</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-accent transition-colors">
                  <Mail size={20} strokeWidth={3} />
                </div>
                <input 
                  type="email" 
                  placeholder="hello@hireloop.io"
                  className="w-full bg-white border-2 border-[#1E293B] rounded-2xl py-4 pl-12 pr-4 font-bold text-fg placeholder:text-slate-300 focus:outline-none focus:shadow-pop transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-end ml-1">
                <label className="text-sm font-black uppercase tracking-widest text-fg">Password</label>
                <a href="#" className="text-xs font-bold text-accent hover:underline">Forgot?</a>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-secondary transition-colors">
                  <Lock size={20} strokeWidth={3} />
                </div>
                <input 
                  type="password" 
                  placeholder="••••••••"
                  className="w-full bg-white border-2 border-[#1E293B] rounded-2xl py-4 pl-12 pr-4 font-bold text-fg placeholder:text-slate-300 focus:outline-none focus:shadow-[4px_4px_0px_0px_#F472B6] transition-all"
                />
              </div>
            </div>

            <Button className="w-full h-16 text-xl shadow-pop-lg mt-4" variant="primary">
              Login
            </Button>
          </form>

          <div className="mt-8 pt-8 border-t-2 border-slate-100 text-center">
            <p className="font-bold text-slate-500">
              New here? <button onClick={() => navigate('/signup')} className="text-secondary hover:underline cursor-pointer">Sign up</button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
