import { useState, useEffect } from 'react';
import SymptomForm from './components/SymptomForm';
import AnalysisResults from './components/AnalysisResults';
import AuthForm from './components/AuthForm';
import UserProfile from './components/UserProfile';
import HistoryModal from './components/HistoryModal';
import { authAPI } from './services/api';
import './App.css';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [user, setUser] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      if (authAPI.isAuthenticated()) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          // Token expired or invalid
          authAPI.logout();
        }
      }
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const handleAnalysisComplete = (result) => {
    setAnalysis(result);
  };

  const handleNewAnalysis = () => {
    setAnalysis(null);
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
    setAnalysis(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthForm onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gray-50">
      <div className="container mx-auto px-4 py-12 relative z-10">
        {/* User Profile */}
        <div className="mb-8 animate-fade-in">
          <UserProfile 
            user={user} 
            onLogout={handleLogout}
            onViewHistory={() => setShowHistory(true)}
          />
        </div>

        {/* Stunning Header */}
        <header className="text-center mb-16 animate-fade-in">
          <div className="relative inline-block mb-6">
            {/* Animated logo with glow */}
            <div className="relative p-6 bg-linear-to-br from-blue-500 to-purple-600 rounded-3xl shadow-2xl animate-pulse-glow">
              <svg className="w-20 h-20 text-white relative z-10 animate-float" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            {/* Decorative rings */}
            <div className="absolute inset-0 rounded-full border-2 border-purple-200 animate-ping" style={{animationDuration: '3s'}}></div>
          </div>
          
          <h1 className="text-7xl font-extrabold mb-4 animate-slide-up">
            <span className="bg-linear-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Health Symptom Checker
            </span>
          </h1>
          
          <div className="max-w-3xl mx-auto">
            <p className="text-gray-700 text-2xl font-medium mb-4 animate-slide-up" style={{animationDelay: '0.2s'}}>
               AI-Powered Medical Analysis
            </p>
            <div className="inline-block bg-yellow-50 rounded-2xl px-8 py-4 shadow-lg border border-yellow-200 animate-slide-up" style={{animationDelay: '0.4s'}}>
              <p className="text-gray-700 text-base flex items-center justify-center">
                <svg className="w-5 h-5 mr-2 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Educational purposes only • Not a substitute for professional medical advice
              </p>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="animate-slide-up">
          {!analysis ? (
            <SymptomForm onAnalysisComplete={handleAnalysisComplete} />
          ) : (
            <div>
              <button
                onClick={handleNewAnalysis}
                className="mb-8 group flex items-center bg-linear-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-semibold shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
              >
                <svg className="w-6 h-6 mr-3 transition-transform group-hover:translate-x-[-4px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                </svg>
                <span className="text-lg">Analyze New Symptoms</span>
                <div className="ml-3 w-2 h-2 bg-green-300 rounded-full animate-pulse"></div>
              </button>
              <AnalysisResults analysis={analysis} />
            </div>
          )}
        </main>

        {/* Stunning Footer */}
        <footer className="mt-20 text-center space-y-6 animate-fade-in">
          {/* Tech Stack Badges */}
          <div className="flex justify-center gap-4 flex-wrap mb-8">
            <div className="group bg-white rounded-full px-6 py-3 shadow-lg border border-gray-200 transform hover:scale-110 transition-all duration-300">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-linear-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center animate-pulse">
                  <span className="text-white text-xs font-bold">AI</span>
                </div>
                <span className="text-gray-800 font-semibold">Google Gemini</span>
              </div>
            </div>
            
            <div className="group bg-white rounded-full px-6 py-3 shadow-lg border border-gray-200 transform hover:scale-110 transition-all duration-300">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-linear-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center animate-pulse" style={{animationDelay: '0.5s'}}>
                  <span className="text-white text-xs font-bold">DB</span>
                </div>
                <span className="text-gray-800 font-semibold">Pinecone</span>
              </div>
            </div>
            
            <div className="group bg-white rounded-full px-6 py-3 shadow-lg border border-gray-200 transform hover:scale-110 transition-all duration-300">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-linear-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center animate-pulse" style={{animationDelay: '1s'}}>
                  <span className="text-white text-xs font-bold">⚛️</span>
                </div>
                <span className="text-gray-800 font-semibold">React</span>
              </div>
            </div>
          </div>
          
          {/* Main Disclaimer Card */}
          <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-2xl border border-gray-200 p-8 transform hover:scale-105 transition-all duration-300">
            <div className="flex items-center justify-center mb-4">
              <div className="p-3 bg-linear-to-br from-yellow-400 to-orange-500 rounded-2xl shadow-lg animate-pulse">
                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-800 ml-4">Important Medical Disclaimer</h3>
            </div>
            <p className="text-gray-700 text-base leading-relaxed">
              This tool is for <strong className="text-yellow-600">educational purposes only</strong>. Always consult with a qualified healthcare provider for medical concerns. Do not use this information for self-diagnosis or treatment.
            </p>
          </div>
          
          {/* Copyright */}
          <div className="pt-6">
            <p className="text-gray-600 text-sm">
              Made with ❤️ using cutting-edge AI technology
            </p>
            <p className="text-gray-400 text-xs mt-2">
              © 2025 Health Symptom Checker • All Rights Reserved
            </p>
          </div>
        </footer>

        {/* History Modal */}
        {showHistory && <HistoryModal onClose={() => setShowHistory(false)} />}
      </div>
    </div>
  );
}

export default App;
