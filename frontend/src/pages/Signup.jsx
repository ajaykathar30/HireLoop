import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
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
      toast.success('Account created successfully! Please login to continue.');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left side - Visual/Branding */}
      <div className="hidden lg:flex w-1/2 bg-slate-900 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80')] bg-cover bg-center opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/90 via-slate-900 to-primary/20" />
        
        <div className="relative z-10 max-w-lg">
          <Link to="/" className="flex items-center gap-2 mb-12 transition-opacity hover:opacity-90">
            <div className="bg-primary p-2 rounded-xl">
              <Sparkles className="text-primary-foreground fill-primary-foreground" size={24} />
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">HireLoop</span>
          </Link>
          
          <div className="space-y-8">
            <h1 className="text-5xl font-extrabold text-white leading-tight">
              Start your journey with <span className="text-primary underline decoration-wavy underline-offset-8">HireLoop.</span>
            </h1>
            
            <div className="grid gap-6">
              <div className="flex gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                  <Zap className="text-primary" size={20} />
                </div>
                <div>
                  <h4 className="text-white font-bold mb-1 text-sm">Instant Matching</h4>
                  <p className="text-white/60 text-xs leading-relaxed">Our AI algorithms find the perfect fit between candidates and companies in seconds.</p>
                </div>
              </div>

              <div className="flex gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="h-10 w-10 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                  <ShieldCheck className="text-blue-400" size={20} />
                </div>
                <div>
                  <h4 className="text-white font-bold mb-1 text-sm">Bias-Free Evaluation</h4>
                  <p className="text-white/60 text-xs leading-relaxed">Focusing on skills and potential through standardized, data-driven assessment tools.</p>
                </div>
              </div>
            </div>

            <div className="pt-8 border-t border-white/10">
              <p className="text-white/60 italic text-sm leading-relaxed">
                "HireLoop completely changed how we hire. The AI-interviews are efficient and help us identify top talent faster than ever."
              </p>
              <div className="mt-4 flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-slate-700" />
                <div>
                  <p className="text-white text-xs font-bold">Sarah Chen</p>
                  <p className="text-white/40 text-[10px]">Head of Talent @ TechFlow</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Signup Form */}
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
            <h2 className="text-3xl font-extrabold tracking-tight">Create an account</h2>
            <p className="text-muted-foreground font-medium">
              Join thousands of professionals and companies today
            </p>
          </div>

          <form onSubmit={handleSignup} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-3">
                <Label>I am a...</Label>
                <RadioGroup 
                  defaultValue="candidate" 
                  value={role} 
                  onValueChange={setRole}
                  className="grid grid-cols-2 gap-4"
                >
                  <div>
                    <RadioGroupItem value="candidate" id="candidate" className="peer sr-only" />
                    <Label
                      htmlFor="candidate"
                      className="flex flex-col items-center justify-between rounded-xl border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer transition-all"
                    >
                      <User className="mb-2 h-6 w-6" />
                      <span className="text-xs font-bold uppercase tracking-tight">Candidate</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem value="company" id="company" className="peer sr-only" />
                    <Label
                      htmlFor="company"
                      className="flex flex-col items-center justify-between rounded-xl border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer transition-all"
                    >
                      <Building2 className="mb-2 h-6 w-6" />
                      <span className="text-xs font-bold uppercase tracking-tight">Company</span>
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">
                  {role === 'candidate' ? 'Full Name' : 'Company Name'}
                </Label>
                <div className="relative group">
                  {role === 'candidate' ? (
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
                  ) : (
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" size={18} />
                  )}
                  <Input 
                    id="name"
                    placeholder={role === 'candidate' ? "John Doe" : "Tech Corp"}
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="pl-10 h-11 border-muted-foreground/20 focus-visible:ring-primary/20"
                  />
                </div>
              </div>

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
                <Label htmlFor="password">Password</Label>
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
                <p className="text-[10px] text-muted-foreground font-medium">Must be at least 8 characters long</p>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full h-11 font-bold text-base shadow-sm group mt-2"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  Create account
                  <ChevronRight size={18} className="transition-transform group-hover:translate-x-0.5" />
                </div>
              )}
            </Button>
          </form>

          <div className="text-center pt-2">
            <p className="text-sm font-medium text-muted-foreground">
              Already have an account?{" "}
              <Link to="/login" className="text-primary hover:underline font-bold">
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
