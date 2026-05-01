import { Button } from "./ui/button";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, LogOut, Bell } from "lucide-react";
import { useSelector, useDispatch } from 'react-redux';
import { setLogout } from '../redux/authSlice';
import { authApi } from "../lib/api";
import toast from 'react-hot-toast';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export const Navbar = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, role, user } = useSelector((state) => state.auth);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      dispatch(setLogout());
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (err) {
      toast.error("Logout failed");
    }
  };

  return (
    <nav className="sticky top-4 z-50 px-4 mb-10">
      <div className="max-w-6xl mx-auto neo-brutal bg-white rounded-[2rem] px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-10">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-secondary p-2 rounded-xl border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] group-hover:translate-x-[-1px] group-hover:translate-y-[-1px] transition-all">
              <Sparkles className="text-black fill-black" size={20} />
            </div>
            <span className="text-2xl font-black tracking-tighter text-black uppercase">HireLoop</span>
          </Link>
          
          <div className="hidden lg:flex items-center gap-8">
            {role === 'company' ? (
              <Link to="/company/jobs" className="text-sm font-black uppercase tracking-widest text-black/60 hover:text-primary transition-colors">
                Jobs
              </Link>
            ) : (
              <>
                <Link to="/candidate-home" className="text-sm font-black uppercase tracking-widest text-black/60 hover:text-primary transition-colors">
                  Find Jobs
                </Link>
                <Link to="/" className="text-sm font-black uppercase tracking-widest text-black/60 hover:text-primary transition-colors">
                  For Recruiters
                </Link>
              </>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {!isAuthenticated ? (
            <div className="flex items-center gap-4">
              <button 
                className="text-sm font-black uppercase tracking-widest px-4 hover:text-primary transition-colors"
                onClick={() => navigate('/login')}
              >
                Login
              </button>
              <button 
                className="neo-pill bg-primary text-white text-sm uppercase tracking-widest"
                onClick={() => navigate('/signup')}
              >
                Post Job →
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <button 
                onClick={handleLogout}
                className="text-sm font-black uppercase tracking-widest text-black/60 hover:text-destructive transition-colors hidden sm:block"
              >
                Logout
              </button>

              <button 
                className="neo-pill bg-accent text-black text-sm uppercase tracking-widest"
                onClick={() => navigate('/profile')}
              >
                {user?.name?.split(' ')[0] || 'Profile'}
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
