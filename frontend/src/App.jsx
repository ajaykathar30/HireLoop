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
import TestInterview from "./mock_interview_test/TestInterview";

// Route guard component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, role } = useSelector((state) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

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
              : isAuthenticated && role === 'company'
              ? <Navigate to="/company/jobs" replace />
              : <Home />
          } 
        />
        <Route path="/candidate-home" element={
          <ProtectedRoute allowedRoles={['candidate']}>
            <CandidateHome />
          </ProtectedRoute>
        } />
        
        {/* Recruiter Routes */}
        <Route path="/company/jobs" element={
          <ProtectedRoute allowedRoles={['company']}>
            <CompanyJobs />
          </ProtectedRoute>
        } />
        <Route path="/company/jobs/create" element={
          <ProtectedRoute allowedRoles={['company']}>
            <PostJob />
          </ProtectedRoute>
        } />
        <Route path="/company/jobs/:jobId/applicants" element={
          <ProtectedRoute allowedRoles={['company']}>
            <JobApplicants />
          </ProtectedRoute>
        } />

        {/* Interview Room */}
        <Route path="/interview/:sessionId" element={
          <ProtectedRoute allowedRoles={['candidate']}>
            <InterviewSession />
          </ProtectedRoute>
        } />

        {/* Common Routes */}
        <Route path="/profile" element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Logic Test Route */}
        <Route path="/test-logic" element={<TestInterview />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
