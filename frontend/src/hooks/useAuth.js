import { useState, useEffect } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';
import { useToast } from '@chakra-ui/react';
import { API_URL } from '../config';

const useAuth = () => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  
  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('authToken');
        
        if (storedToken) {
          // Verify token isn't expired
          const decodedToken = jwt_decode(storedToken);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            // Token expired
            localStorage.removeItem('authToken');
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
          } else {
            // Valid token, fetch user info
            setToken(storedToken);
            
            // Configure axios headers
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
            
            try {
              const { data } = await axios.get(`${API_URL}/auth/me`);
              setUser(data);
              setIsAuthenticated(true);
            } catch (error) {
              console.error('Error fetching user data:', error);
              localStorage.removeItem('authToken');
              setToken(null);
              setUser(null);
              setIsAuthenticated(false);
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  const login = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const { data } = await axios.post(`${API_URL}/auth/login`, formData);
      
      // Set token in localStorage and state
      localStorage.setItem('authToken', data.access_token);
      setToken(data.access_token);
      
      // Configure axios headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      
      // Fetch user data
      const { data: userData } = await axios.get(`${API_URL}/auth/me`);
      setUser(userData);
      setIsAuthenticated(true);
      
      toast({
        title: 'Login successful',
        description: `Welcome back, ${userData.username}!`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Could not authenticate. Please check your credentials.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      return false;
    }
  };
  
  const register = async (userData) => {
    try {
      const { data } = await axios.post(`${API_URL}/auth/register`, userData);
      
      toast({
        title: 'Registration successful',
        description: 'You can now log in with your credentials.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      
      toast({
        title: 'Registration failed',
        description: error.response?.data?.detail || 'Could not register. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      return false;
    }
  };
  
  const logout = () => {
    localStorage.removeItem('authToken');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    
    toast({
      title: 'Logged out',
      description: 'You have been successfully logged out.',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    register,
    loading,
  };
};

export default useAuth; 
