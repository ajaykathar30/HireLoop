import React, { useState } from 'react';
import { 
  Mail, 
  Lock, 
  ArrowLeft, 
  Sparkles, 
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setLogin } from '../redux/authSlice';
import { authApi } from '../lib/api';
import toast from 'react-hot-toast';

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await authApi.login(formData);
      const { role, user } = response.data;
      dispatch(setLogin({ role, user }));
      toast.success('Welcome back to HireLoop!');
      if (role === 'candidate') {
        navigate('/candidate-home');
      } else {
        navigate('/company/jobs');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Left side */}
      <div className="hidden lg:flex w-1/2 bg-primary items-center justify-center p-16 relative overflow-hidden border-r-8 border-black">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle, #000 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
        
        <div className="relative z-10 max-w-lg">
          <Link to="/" className="flex items-center gap-3 mb-16 group">
            <div className="bg-white p-3 rounded-2xl neo-brutal">
              <Sparkles className="text-primary fill-primary" size={32} />
            </div>
            <span className="text-3xl font-black tracking-tighter text-white uppercase">HireLoop</span>
          </Link>
          
          <h1 className="text-7xl font-black text-white leading-[0.9] uppercase tracking-tighter mb-10">
            Find your <br />
            <span className="text-secondary underline decoration-white decoration-8 underline-offset-8 italic">Next Edge.</span>
          </h1>
          <p className="text-white font-bold text-xl mb-12 opacity-80 leading-tight">
            Log in to access your AI-powered career dashboard and discover opportunities tailored to your unique skill set.
          </p>
          
          <div className="space-y-6">
            {[
              "AI-driven job matching",
              "Direct connection with top companies"
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-4 text-white font-black uppercase tracking-widest text-xs">
                <CheckCircle2 className="text-accent fill-accent text-black" size={24} />
                <span>{feature}</span>
              </div>
            ))}
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
            <h2 className="text-5xl font-black uppercase tracking-tighter leading-none">Welcome back</h2>
          </div>

          <form onSubmit={handleLogin} className="space-y-8">
            <div className="space-y-6">
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
              className="w-full h-16 neo-brutal bg-primary text-white font-black uppercase tracking-widest text-sm rounded-2xl hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center justify-center gap-3"
            >
              {loading ? "Signing in..." : "Sign in"}
              {!loading && <ChevronRight size={20} />}
            </button>
          </form>

          <div className="text-center">
            <p className="text-sm font-black uppercase tracking-widest text-black/40">
              Don't have an account?{" "}
              <Link to="/signup" className="text-primary hover:underline italic">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
