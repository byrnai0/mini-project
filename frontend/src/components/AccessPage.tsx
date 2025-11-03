import { useState } from 'react';
import { Download, Loader2, Lock, FileText } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { FileShare } from '../types';
import { formatFileSize } from '../utils/fileUtils';

export default function AccessPage() {
  const [shareCode, setShareCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [fileShare, setFileShare] = useState<FileShare | null>(null);
  const [error, setError] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);

  const handleAccessFile = async () => {
    if (!shareCode.trim()) {
      setError('Please enter a share code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const { data, error: fetchError } = await supabase
        .from('file_shares')
        .select('*')
        .eq('share_code', shareCode.toUpperCase())
        .maybeSingle();

      if (fetchError) throw fetchError;

      if (!data) {
        setError('Invalid share code. Please check and try again.');
        return;
      }

      if (data.expires_at && new Date(data.expires_at) < new Date()) {
        setError('This file share has expired.');
        return;
      }

      if (data.max_downloads && data.downloads >= data.max_downloads) {
        setError('This file has reached its maximum download limit.');
        return;
      }

      setFileShare(data);
    } catch (err) {
      console.error('Access error:', err);
      setError('Failed to access file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!fileShare) return;

    setIsDownloading(true);
    try {
      const response = await fetch(fileShare.file_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileShare.file_name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      const { error: updateError } = await supabase
        .from('file_shares')
        .update({ downloads: fileShare.downloads + 1 })
        .eq('id', fileShare.id);

      if (updateError) throw updateError;

      setFileShare({ ...fileShare, downloads: fileShare.downloads + 1 });
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download file. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAccessFile();
    }
  };

  if (fileShare) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              File Ready to Download
            </h2>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">File Name:</span>
                <span className="font-medium text-gray-800">{fileShare.file_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">File Size:</span>
                <span className="font-medium text-gray-800">{formatFileSize(fileShare.file_size)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shared By:</span>
                <span className="font-medium text-gray-800">{fileShare.sender_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Downloads:</span>
                <span className="font-medium text-gray-800">
                  {fileShare.downloads}
                  {fileShare.max_downloads && ` / ${fileShare.max_downloads}`}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Download File
              </>
            )}
          </button>

          <button
            onClick={() => {
              setFileShare(null);
              setShareCode('');
            }}
            className="w-full mt-4 px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Receive Another File
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Receive Shared File
          </h2>
          <p className="text-gray-600">
            Enter the share code to Receive your file
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Share Code
            </label>
            <input
              type="text"
              value={shareCode}
              onChange={(e) => {
                setShareCode(e.target.value.toUpperCase());
                setError('');
              }}
              onKeyPress={handleKeyPress}
              placeholder="Enter 6-character code"
              maxLength={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl font-mono font-bold tracking-wider uppercase focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={handleAccessFile}
            disabled={isLoading || !shareCode.trim()}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                receiving...
              </>
            ) : (
              'Receive File'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
