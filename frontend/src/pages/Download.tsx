import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Download, ArrowLeft, File } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export default function DownloadPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [accessCode, setAccessCode] = useState(searchParams.get("code") || "");
  const [loading, setLoading] = useState(false);
  const [fileInfo, setFileInfo] = useState<any>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const code = searchParams.get("code");
    if (code) {
      setAccessCode(code);
      fetchFileInfo(code);
    }
  }, [searchParams]);

  const fetchFileInfo = async (code: string) => {
    if (!code || code.length !== 6) return;

    setLoading(true);
    try {
      const { data, error } = await supabase
        .from("file_shares")
        .select("*")
        .eq("access_code", code.toUpperCase())
        .single();

      if (error) {
        toast.error("Invalid access code");
        setFileInfo(null);
      } else if (new Date(data.expires_at) < new Date()) {
        toast.error("This file has expired");
        setFileInfo(null);
      } else {
        setFileInfo(data);
      }
    } catch (err) {
      toast.error("Failed to fetch file information");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!fileInfo) return;

    setDownloading(true);
    try {
      const { data, error } = await supabase.storage
        .from("shared-files")
        .download(fileInfo.file_path);

      if (error) throw error;

      // Create download link
      const url = window.URL.createObjectURL(data);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileInfo.file_name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      // Update download count
      await supabase
        .from("file_shares")
        .update({ download_count: fileInfo.download_count + 1 })
        .eq("id", fileInfo.id);

      toast.success("File downloaded successfully!");
    } catch (err) {
      toast.error("Failed to download file");
    } finally {
      setDownloading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-subtle flex flex-col">
      <header className="border-b border-border bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Upload
          </Button>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-12 flex items-center justify-center">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2 text-foreground">
              Receive File
            </h1>
            <p className="text-muted-foreground">
              Enter the access code to Receive your file
            </p>
          </div>

          <Card className="p-6 shadow-custom-lg border-border">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-foreground block mb-2">
                  Access Code
                </label>
                <Input
                  placeholder="Enter 6-digit code"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                  maxLength={6}
                  className="font-mono text-center text-lg tracking-wider"
                />
              </div>

              {!fileInfo && (
                <Button
                  onClick={() => fetchFileInfo(accessCode)}
                  disabled={accessCode.length !== 6 || loading}
                  className="w-full bg-gradient-primary shadow-custom-lg hover:shadow-custom-xl transition-all"
                >
                  {loading ? "Verifying..." : "Verify Code"}
                </Button>
              )}

              {fileInfo && (
                <div className="space-y-4 pt-4 border-t border-border">
                  <div className="flex items-center gap-3 p-4 rounded-lg bg-muted">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <File className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-foreground truncate">
                        {fileInfo.file_name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(fileInfo.file_size)}
                      </p>
                    </div>
                  </div>

                  <Button
                    onClick={handleDownload}
                    disabled={downloading}
                    className="w-full bg-gradient-primary shadow-custom-lg hover:shadow-custom-xl transition-all"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {downloading ? "Downloading..." : "Download File"}
                  </Button>

                  <p className="text-xs text-center text-muted-foreground">
                    Downloaded {fileInfo.download_count} time
                    {fileInfo.download_count !== 1 ? "s" : ""}
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
