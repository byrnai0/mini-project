import { useState } from "react";
import { FileUpload } from "@/components/FileUpload";
import { ShareResult } from "@/components/ShareResult";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Share2, Download } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{
    accessCode: string;
    shareLink: string;
  } | null>(null);

  const handleFileSelect = (file: File) => {
    if (file.size > 100 * 1024 * 1024) {
      toast.error("File size must be less than 100 MB");
      return;
    }
    setSelectedFile(file);
  };

  const handleClear = () => {
    setSelectedFile(null);
  };

  const generateAccessCode = async (): Promise<string> => {
    const { data, error } = await supabase.rpc("generate_access_code");
    if (error || !data) {
      throw new Error("Failed to generate access code");
    }
    return data;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      // Generate unique access code
      const accessCode = await generateAccessCode();
      const fileId = crypto.randomUUID();
      const filePath = `${fileId}/${selectedFile.name}`;

      // Upload file to storage
      const { error: uploadError } = await supabase.storage
        .from("shared-files")
        .upload(filePath, selectedFile);

      if (uploadError) throw uploadError;

      // Create file share record
      const { error: dbError } = await supabase.from("file_shares").insert({
        file_path: filePath,
        file_name: selectedFile.name,
        file_size: selectedFile.size,
        access_code: accessCode,
      });

      if (dbError) throw dbError;

      // Generate share link
      const shareLink = `${window.location.origin}/download?code=${accessCode}`;

      setUploadResult({
        accessCode,
        shareLink,
      });

      toast.success("File uploaded successfully!");
    } catch (err) {
      console.error("Upload error:", err);
      toast.error("Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  const handleNewUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <header className="border-b border-border bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Share2 className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-foreground">FileShare</h1>
            </div>
            <Button
              variant="outline"
              onClick={() => navigate("/download")}
              className="gap-2"
            >
              <Download className="w-4 h-4" />
              Receive File
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {!uploadResult ? (
          <div className="max-w-2xl mx-auto space-y-8">
            <div className="text-center space-y-2">
              <h2 className="text-4xl font-bold text-foreground">
                Share Files Securely
              </h2>
              <p className="text-lg text-muted-foreground">
                Upload a file and get a unique code to share with anyone
              </p>
            </div>

            <FileUpload
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClear={handleClear}
            />

            {selectedFile && (
              <div className="flex justify-center">
                <Button
                  onClick={handleUpload}
                  disabled={uploading}
                  size="lg"
                  className="bg-gradient-primary shadow-custom-lg hover:shadow-custom-xl transition-all px-12"
                >
                  {uploading ? "Uploading..." : "Upload & Generate Code"}
                </Button>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-primary">1</span>
                </div>
                <h3 className="font-semibold text-foreground">Upload File</h3>
                <p className="text-sm text-muted-foreground">
                  Choose any file up to 100 MB
                </p>
              </div>
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-primary">2</span>
                </div>
                <h3 className="font-semibold text-foreground">Get Code</h3>
                <p className="text-sm text-muted-foreground">
                  Receive a unique access code & QR
                </p>
              </div>
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold text-foreground">Share</h3>
                <p className="text-sm text-muted-foreground">
                  Share code, link, or QR to anyone
                </p>
              </div>
            </div>
          </div>
        ) : (
          <ShareResult
            accessCode={uploadResult.accessCode}
            shareLink={uploadResult.shareLink}
            onNewUpload={handleNewUpload}
          />
        )}
      </main>
    </div>
  );
};

export default Index;
