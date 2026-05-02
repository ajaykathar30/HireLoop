import React, { useState } from 'react';
import { 
  Mail, 
  Lock, 
  User, 
  ArrowLeft, 
  Sparkles, 
  Building2,
  ChevronRight,
  ShieldCheck,
  Zap
} from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../lib/api';
import toast from 'react-hot-toast';

const Signup = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState('candidate');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (role === 'candidate') {
        await authApi.signupCandidate({
          full_name: formData.name,
          email: formData.email,
          password: formData.password,
        });
      } else {
        await authApi.signupCompany({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        });
      }
      toast.success('Account created successfully!');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Signup failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Left side */}
      <div className="hidden lg:flex w-1/2 bg-black items-center justify-center p-16 relative overflow-hidden border-r-8 border-black">
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        
        <div className="relative z-10 max-w-lg">
          <Link to="/" className="flex items-center gap-3 mb-16 group">
            <div className="bg-primary p-3 rounded-2xl neo-brutal">
              <Sparkles className="text-white fill-white" size={32} />
            </div>
            <span className="text-3xl font-black tracking-tighter text-white uppercase">HireLoop</span>
          </Link>
          
          <div className="space-y-10">
            <h1 className="text-6xl font-black text-white leading-[0.9] uppercase tracking-tighter">
              Start your <br />
              <span className="text-accent underline decoration-white decoration-8 underline-offset-8 italic">Journey</span> <br />
              with us.
            </h1>
            
            <div className="grid gap-6">
              <div className="neo-brutal bg-white p-6 rounded-2xl flex gap-4 items-center">
                <div className="h-12 w-12 rounded-xl bg-primary border-2 border-black flex items-center justify-center text-white shrink-0 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  <Zap size={24} />
                </div>
                <div>
                  <h4 className="text-black font-black uppercase tracking-tight text-sm">Instant Matching</h4>
                  <p className="text-black/60 text-xs font-bold">Find the perfect fit in seconds.</p>
                </div>
              </div>

              <div className="neo-brutal bg-accent p-6 rounded-2xl flex gap-4 items-center">
                <div className="h-12 w-12 rounded-xl bg-black border-2 border-white flex items-center justify-center text-white shrink-0 shadow-[2px_2px_0px_0px_rgba(255,255,255,1)]">
                  <ShieldCheck size={24} />
                </div>
                <div>
                  <h4 className="text-black font-black uppercase tracking-tight text-sm">Bias-Free evaluation</h4>
                  <p className="text-black/60 text-xs font-bold">Standardized, data-driven assessments.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <div className="w-full max-w-md space-y-12">
          <div className="space-y-4">
            <button 
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-black/40 font-black uppercase tracking-widest text-[10px] hover:text-black transition-colors"
            >
              <ArrowLeft size={14} /> Home
            </button>
            <h2 className="text-5xl font-black uppercase tracking-tighter leading-none">Create Account</h2>
          </div>

          <form onSubmit={handleSignup} className="space-y-8">
            <div className="space-y-6">
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">I am a...</label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setRole('candidate')}
                    className={`h-16 neo-brutal rounded-2xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-2 transition-all ${role === 'candidate' ? 'bg-primary text-white' : 'bg-white text-black'}`}
                  >
                    <User size={18} /> Candidate
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('company')}
                    className={`h-16 neo-brutal rounded-2xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-2 transition-all ${role === 'company' ? 'bg-secondary text-black' : 'bg-white text-black'}`}
                  >
                    <Building2 size={18} /> Company
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">
                  {role === 'candidate' ? 'Full Name' : 'Company Name'}
                </label>
                <div className="relative">
                  {role === 'candidate' ? (
                    <User className="absolute left-6 top-1/2 -translate-y-1/2 text-black/40" size={20} />
                  ) : (
                    <Building2 className="absolute left-6 top-1/2 -translate-y-1/2 text-black/40" size={20} />
                  )}
                  <input 
                    required
                    placeholder={role === 'candidate' ? "John Doe" : "Tech Corp"}
                    className="w-full h-16 pl-14 pr-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Email address</label>
                <div className="relative">
                  <Mail className="absolute left-6 top-1/2 -translate-y-1/2 text-black/40" size={20} />
                  <input 
                    type="email"
                    required
                    placeholder="name@example.com"
                    className="w-full h-16 pl-14 pr-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="space-y-3">
                <label className="text-[10px] font-black uppercase tracking-widest text-black/40">Password</label>
                <div className="relative">
                  <Lock className="absolute left-6 top-1/2 -translate-y-1/2 text-black/40" size={20} />
                  <input 
                    type="password"
                    required
                    placeholder="••••••••"
                    className="w-full h-16 pl-14 pr-6 neo-brutal bg-white rounded-2xl outline-none font-bold focus:border-primary transition-all"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                  />
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full h-16 neo-brutal bg-black text-white font-black uppercase tracking-widest text-sm rounded-2xl hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:bg-primary transition-all flex items-center justify-center gap-3"
            >
              {loading ? "Creating..." : "Create Account"}
              {!loading && <ChevronRight size={20} />}
            </button>
          </form>

          <div className="text-center">
            <p className="text-sm font-black uppercase tracking-widest text-black/40">
              Already have an account?{" "}
              <Link to="/login" className="text-primary hover:underline italic">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
