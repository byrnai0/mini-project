import { useState } from 'react';
import { Copy, Check, Link2, Loader2 } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { generateShareCode, formatFileSize, getShareLink } from '../utils/fileUtils';
import FileUpload from './FileUpload';

interface ShareResult {
  shareCode: string;
  shareLink: string;
  fileName: string;
}

export default function SharePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [senderName, setSenderName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [shareResult, setShareResult] = useState<ShareResult | null>(null);
  const [copiedCode, setCopiedCode] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setShareResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const shareCode = generateShareCode();
      const fileName = `${shareCode}-${selectedFile.name}`;

      const { error: uploadError } = await supabase.storage
        .from('file-shares')
        .upload(fileName, selectedFile);

      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage
        .from('file-shares')
        .getPublicUrl(fileName);

      const { error: dbError } = await supabase
        .from('file_shares')
        .insert({
          file_name: selectedFile.name,
          file_url: urlData.publicUrl,
          file_size: selectedFile.size,
          file_type: selectedFile.type,
          share_code: shareCode,
          sender_name: senderName || 'Anonymous',
        });

      if (dbError) throw dbError;

      setShareResult({
        shareCode,
        shareLink: getShareLink(shareCode),
        fileName: selectedFile.name,
      });

      setSelectedFile(null);
      setSenderName('');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const copyToClipboard = async (text: string, type: 'code' | 'link') => {
    await navigator.clipboard.writeText(text);
    if (type === 'code') {
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    } else {
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  if (shareResult) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              File Shared Successfully!
            </h2>
            <p className="text-gray-600">
              {shareResult.fileName}
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Share Code
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={shareResult.shareCode}
                  readOnly
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl font-mono font-bold tracking-wider"
                />
                <button
                  onClick={() => copyToClipboard(shareResult.shareCode, 'code')}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  {copiedCode ? (
                    <Check className="w-5 h-5 text-green-600" />
                  ) : (
                    <Copy className="w-5 h-5 text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Share Link
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={shareResult.shareLink}
                  readOnly
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-sm"
                />
                <button
                  onClick={() => copyToClipboard(shareResult.shareLink, 'link')}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  {copiedLink ? (
                    <Check className="w-5 h-5 text-green-600" />
                  ) : (
                    <Link2 className="w-5 h-5 text-gray-600" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <button
            onClick={() => setShareResult(null)}
            className="w-full mt-8 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Share Another File
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Share a File</h2>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Name (Optional)
          </label>
          <input
            type="text"
            value={senderName}
            onChange={(e) => setSenderName(e.target.value)}
            placeholder="Enter your name"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <FileUpload onFileSelect={handleFileSelect} />

        {selectedFile && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-800">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-red-600 hover:text-red-700 text-sm font-medium"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className="w-full mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Uploading...
            </>
          ) : (
            'Upload & Generate Code'
          )}
        </button>
      </div>
    </div>
  );
}
