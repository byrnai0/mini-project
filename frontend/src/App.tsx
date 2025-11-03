import { useState, useEffect } from 'react';
import { Share2 } from 'lucide-react';
import Navigation from './components/Navigation';
import SharePage from './components/SharePage';
import AccessPage from './components/AccessPage';

function App() {
  const [activeTab, setActiveTab] = useState<'share' | 'access'>('share');

  useEffect(() => {
    const path = window.location.pathname;
    const codeMatch = path.match(/\/access\/([A-Z0-9]{6})/);

    if (codeMatch) {
      setActiveTab('access');
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Share2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">FileShare</h1>
              <p className="text-sm text-gray-500">Share files securely with anyone</p>
            </div>
          </div>
        </div>
      </header>

      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {activeTab === 'share' ? <SharePage /> : <AccessPage />}
      </main>

      <footer className="mt-auto py-6 text-center text-sm text-gray-500">
        <p>Share files securely</p>
      </footer>
    </div>
  );
}

export default App;
