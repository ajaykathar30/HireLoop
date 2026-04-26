import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
        navigate('/');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left side - Visual/Branding */}
      <div className="hidden lg:flex w-1/2 bg-primary items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.05] [mask-image:linear-gradient(to_bottom,transparent,black)]" />
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary via-primary to-primary/80" />
        
        <div className="relative z-10 max-w-lg">
          <Link to="/" className="flex items-center gap-2 mb-12 transition-opacity hover:opacity-90">
            <div className="bg-white p-2 rounded-xl">
              <Sparkles className="text-primary fill-primary" size={24} />
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">HireLoop</span>
          </Link>
          
          <h1 className="text-5xl font-extrabold text-white leading-tight mb-6">
            Connecting the next generation of <span className="text-primary-foreground/60 underline decoration-wavy underline-offset-8">talent.</span>
          </h1>
          <p className="text-primary-foreground/80 text-lg mb-10 leading-relaxed">
            Log in to access your AI-powered career dashboard and discover opportunities tailored specifically to your unique skill set.
          </p>
          
          <div className="space-y-4">
            {[
              "AI-driven job matching",
              "Seamless text-based interviews",
              "Real-time application tracking",
              "Direct connection with top companies"
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3 text-white/90 font-medium">
                <CheckCircle2 className="text-primary-foreground/60" size={20} />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -top-24 -left-24 w-72 h-72 bg-white/5 rounded-full blur-2xl" />
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 md:p-16 lg:p-20 relative">
        <div className="absolute top-8 left-8 lg:hidden">
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-primary p-1 rounded-lg">
              <Sparkles className="text-primary-foreground fill-primary-foreground" size={16} />
            </div>
            <span className="text-lg font-bold tracking-tight">HireLoop</span>
          </Link>
        </div>

        <div className="w-full max-w-sm space-y-8">
          <div className="space-y-2">
            <Button 
              variant="ghost" 
              className="px-0 text-muted-foreground hover:text-foreground transition-colors -ml-1 mb-2"
              onClick={() => navigate('/')}
            >
              <ArrowLeft size={16} className="mr-2" />
              Home
            </Button>
            <h2 className="text-3xl font-extrabold tracking-tight">Welcome back</h2>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
                  <Input 
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="pl-10 h-11 border-muted-foreground/20 focus-visible:ring-primary/20"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                </div>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
                  <Input 
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="pl-10 h-11 border-muted-foreground/20 focus-visible:ring-primary/20"
                  />
                </div>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full h-11 font-bold text-base shadow-sm group"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Logging in...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  Sign in
                  <ChevronRight size={18} className="transition-transform group-hover:translate-x-0.5" />
                </div>
              )}
            </Button>
          </form>

          <div className="text-center pt-2">
            <p className="text-sm font-medium text-muted-foreground">
              Don't have an account?{" "}
              <Link to="/signup" className="text-primary hover:underline font-bold">
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
