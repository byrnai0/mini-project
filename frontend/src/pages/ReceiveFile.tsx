import { useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Download as DownloadIcon, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const ReceiveFile = () => {
  const navigate = useNavigate();
  const [accessCode, setAccessCode] = useState("");
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (!accessCode.trim()) {
      toast.error("Please enter access code");
      return;
    }

    setDownloading(true);
    try {
      console.log("\n" + "=".repeat(60));
      console.log("📥 FILE DOWNLOAD & DECRYPTION PROCESS");
      console.log("=".repeat(60));
      console.log(`\n🎯 Access Code: ${accessCode}`);

      toast.loading("📥 Connecting to backend...");

      const response = await fetch(
        `http://localhost:5000/api/download/${accessCode}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: "guest_user",
            attributes: {
              role: 'user',
              department: 'general'
            },
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        console.error("❌ Backend error:", error);
        throw new Error(error.error || 'Failed to download file');
      }

      console.log("\n[STEP 1] File received from backend");
      const blob = await response.blob();
      console.log(`✅ File size: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);

      console.log("\n[STEP 2] Initiating download...");
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `downloaded_file`;
      link.click();
      window.URL.revokeObjectURL(url);

      console.log("✅ Download complete\n");
      console.log("=".repeat(60) + "\n");

      toast.dismiss();
      toast.success("✅ File downloaded successfully!");
      setAccessCode("");

    } catch (err: any) {
      console.error("❌ Download error:", err);
      console.log("=".repeat(60) + "\n");
      toast.dismiss();
      
      if (err.message.includes("Failed to fetch")) {
        toast.error("❌ Cannot connect to backend. Make sure http://localhost:5000 is running");
      } else {
        toast.error(err?.message || "Failed to download file");
      }
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <header className="border-b border-border bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-primary hover:text-primary/80 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </button>
          <h1 className="text-3xl font-bold text-foreground">Receive File</h1>
          <p className="text-muted-foreground mt-2">Enter the access code to download a file</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-md w-full mx-auto">
          <div className="bg-background rounded-lg shadow-lg p-8 border border-border space-y-6">
            <div className="flex justify-center">
              <div className="p-3 rounded-lg bg-primary/10">
                <DownloadIcon className="w-8 h-8 text-primary" />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Access Code
                </label>
                <input
                  type="text"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                  placeholder="e.g., ABC123"
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={downloading}
                  maxLength={6}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Ask the file sender for the access code
                </p>
              </div>

              <Button
                onClick={handleDownload}
                disabled={downloading || !accessCode.trim()}
                className="w-full bg-gradient-primary shadow-custom-lg hover:shadow-custom-xl transition-all"
                size="lg"
              >
                {downloading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Downloading...
                  </>
                ) : (
                  <>
                    <DownloadIcon className="w-4 h-4 mr-2" />
                    Download File
                  </>
                )}
              </Button>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-xs text-blue-800">
                <strong>ℹ️ Note:</strong> Your file will be automatically decrypted by the backend before download.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ReceiveFile;