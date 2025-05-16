import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, useToast } from '@chakra-ui/react';

// Auth-related components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import useAuth from './hooks/useAuth';
import AuthContext from './context/AuthContext';

// Layout components
import PublicLayout from './components/Layout/PublicLayout';
import DashboardLayout from './components/Layout/DashboardLayout';

// Dashboard components
import Dashboard from './components/Dashboard/Dashboard';
import PredictionForm from './components/Prediction/PredictionForm';
import PredictionResults from './components/Prediction/PredictionResults';
import PredictionHistory from './components/Prediction/PredictionHistory';
import Account from './components/Dashboard/Account';

// Landing components
import LandingPage from './components/Landing/LandingPage';

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  const auth = useAuth();
  const toast = useToast();
  
  // Global error handling
  React.useEffect(() => {
    const handleError = (event) => {
      if (event.error && event.error.message) {
        toast({
          title: 'Application Error',
          description: event.error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };
    
    window.addEventListener('error', handleError);
    
    return () => {
      window.removeEventListener('error', handleError);
    };
  }, [toast]);
  
  return (
    <AuthContext.Provider value={auth}>
      <Router>
        <Box minH="100vh">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<PublicLayout />}>
              <Route index element={<LandingPage />} />
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
            </Route>
            
            {/* Protected routes */}
            <Route path="/app" element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="predict" element={<PredictionForm />} />
              <Route path="predictions/:id" element={<PredictionResults />} />
              <Route path="history" element={<PredictionHistory />} />
              <Route path="account" element={<Account />} />
            </Route>
          </Routes>
        </Box>
      </Router>
    </AuthContext.Provider>
  );
}

export default App; 
