import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ClaimDetail from './pages/ClaimDetail';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard'); // 'dashboard' | 'detail'
  const [selectedClaimId, setSelectedClaimId] = useState(null);

  const handleViewClaim = (id) => {
    setSelectedClaimId(id);
    setCurrentPage('detail');
  };

  const handleBackToDashboard = () => {
    setSelectedClaimId(null);
    setCurrentPage('dashboard');
  };

  const handleNavigation = (page) => {
    setCurrentPage(page);
    if (page === 'dashboard') {
      setSelectedClaimId(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar onNavigate={handleNavigation} currentPage={currentPage} />
      
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentPage === 'dashboard' ? (
          <Dashboard onViewClaim={handleViewClaim} />
        ) : (
          <ClaimDetail claimId={selectedClaimId} onBack={handleBackToDashboard} />
        )}
      </main>

      <footer className="py-6 border-t border-slate-900 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p>© {new Date().getFullYear()} ClaimGuard AI Platform. Portfolio Demo System.</p>
        </div>
      </footer>
    </div>
  );
}
