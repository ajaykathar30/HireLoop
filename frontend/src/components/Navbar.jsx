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
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-2 transition-opacity hover:opacity-90">
            <div className="bg-primary p-1.5 rounded-lg">
              <Sparkles className="text-primary-foreground fill-primary-foreground" size={18} />
            </div>
            <span className="text-xl font-bold tracking-tight text-foreground">HireLoop</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-6">
            {role === 'company' ? (
              <Link to="/company/jobs" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Jobs
              </Link>
            ) : (
              <>
                <Link to="/candidate-home" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                  Find Jobs
                </Link>
                <Link to="/" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                  For Recruiters
                </Link>
              </>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {!isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>
                Login
              </Button>
              <Button size="sm" onClick={() => navigate('/signup')}>
                Signup
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon-sm" className="text-muted-foreground hidden sm:flex">
                <Bell size={18} />
              </Button>
              
              <div className="flex items-center gap-4">
                {/* Logout Button */}
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleLogout}
                  className="text-muted-foreground hover:text-destructive transition-colors font-medium hidden sm:flex"
                >
                  <LogOut size={16} className="mr-2" />
                  Logout
                </Button>

                {/* Profile Icon (Direct Link) */}
                <Button 
                  variant="ghost" 
                  className="relative h-9 w-9 rounded-full p-0 overflow-hidden border hover:opacity-80 transition-opacity"
                  onClick={() => navigate('/profile')}
                  title="View Profile"
                >
                  <Avatar className="h-full w-full">
                    <AvatarImage src="" alt="Profile" />
                    <AvatarFallback className="bg-primary/10 text-primary text-sm font-bold">
                      {role?.[0]?.toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
