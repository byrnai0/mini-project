export function generateShareCode(): string {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function getShareLink(shareCode: string): string {
  return `${window.location.origin}/access/${shareCode}`;
}
