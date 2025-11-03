import { Share2, Download } from 'lucide-react';

interface NavigationProps {
  activeTab: 'share' | 'access';
  onTabChange: (tab: 'share' | 'access') => void;
}

export default function Navigation({ activeTab, onTabChange }: NavigationProps) {
  return (
    <div className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center space-x-8">
          <button
            onClick={() => onTabChange('share')}
            className={`flex items-center gap-2 px-4 py-4 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'share'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Share2 className="w-5 h-5" />
            Share File
          </button>
          <button
            onClick={() => onTabChange('access')}
            className={`flex items-center gap-2 px-4 py-4 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'access'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Download className="w-5 h-5" />
            Receive File
          </button>
        </div>
      </div>
    </div>
  );
}
