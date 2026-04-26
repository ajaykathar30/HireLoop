import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useSelector } from "react-redux";
import Home from "./pages/Home";
import CandidateHome from "./pages/CandidateHome";
import CompanyJobs from "./pages/CompanyJobs";
import PostJob from "./pages/PostJob";
import JobApplicants from "./pages/JobApplicants";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import InterviewSession from "./pages/InterviewSession";

function App() {
  // Ensure we're selecting from state.auth correctly
  const { isAuthenticated, role } = useSelector((state) => state.auth);

  return (
    <BrowserRouter>
      <Toaster 
        position="top-center"
        toastOptions={{
          className: 'rounded-lg border bg-background text-foreground shadow-lg font-medium',
          duration: 3000,
        }}
      />
      <Routes>
        <Route 
          path="/" 
          element={
            isAuthenticated && role === 'candidate' 
              ? <Navigate to="/candidate-home" replace /> 
              : <Home />
          } 
        />
        <Route path="/candidate-home" element={<CandidateHome />} />
        
        {/* Recruiter Routes */}
        <Route path="/company/jobs" element={<CompanyJobs />} />
        <Route path="/company/jobs/create" element={<PostJob />} />
        <Route path="/company/jobs/:jobId/applicants" element={<JobApplicants />} />

        {/* Interview Room */}
        <Route path="/interview/:sessionId" element={<InterviewSession />} />

        {/* Common Routes */}
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
