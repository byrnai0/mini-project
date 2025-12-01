import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Download as DownloadIcon, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

export default function DownloadPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [accessCode, setAccessCode] = useState<string>(
    searchParams.get("code") || ""
  );
  const [downloading, setDownloading] = useState(false);
  const [user, setUser] = useState<{ id: string; email: string; role: string } | null>(null);
  const [pageLoading, setPageLoading] = useState(true);

  // Check user session on mount
  useEffect(() => {
    const checkSession = async () => {
      try {
        console.log("\n" + "=".repeat(60));
        console.log("🔐 CHECKING AUTH SESSION (Download Page)");
        console.log("=".repeat(60));

        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("❌ Session error:", sessionError);
          setPageLoading(false);
          return;
        }

        if (session?.user) {
          console.log(`✅ Session found for user: ${session.user.email}`);

          try {
            const { data: userData, error: userError } = await supabase
              .from("users")
              .select("role")
              .eq("id", session.user.id)
              .single();

            if (userError && userError.code !== "PGRST116") {
              console.error("User fetch error:", userError);
            }

            const role = (userData as any)?.role ?? "user";
            console.log(`👥 User role: ${role}`);

            setUser({
              id: session.user.id,
              email: session.user.email || "",
              role,
            });
          } catch (error) {
            console.error("Error fetching user data:", error);
            // Set default user even if fetch fails
            setUser({
              id: session.user.id,
              email: session.user.email || "",
              role: "user",
            });
          }
        } else {
          console.log("⚠️ No active session - proceeding as guest");
          setUser(null);
        }
      } catch (error) {
        console.error("Error checking session:", error);
      } finally {
        setPageLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log(`\n🔄 Auth state changed: ${event}`);

      if (event === "SIGNED_OUT") {
        console.log("🚪 User signed out");
        setUser(null);
      } else if (event === "SIGNED_IN" || event === "USER_UPDATED") {
        if (session?.user) {
          try {
            const { data: userData, error: userError } = await supabase
              .from("users")
              .select("role")
              .eq("id", session.user.id)
              .single();

            const role = (userData as any)?.role ?? "user";
            console.log(`✅ Auth updated - User role: ${role}`);

            setUser({
              id: session.user.id,
              email: session.user.email || "",
              role,
            });
          } catch (error) {
            console.error("Error fetching user data:", error);
            setUser({
              id: session.user.id,
              email: session.user.email || "",
              role: "user",
            });
          }
        }
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

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
      
      const userRole = user?.role || "user";
      const userId = user?.id || "guest_user";
      
      console.log(`\n🎯 Access Code: ${accessCode}`);
      console.log(`👤 User ID: ${userId}`);
      console.log(`👥 User Role: ${userRole}`);

      toast.loading("📥 Connecting to backend...");

      const userAttributes = {
        role: userRole,
        department: "general",
      };

      console.log(`📋 User Attributes: ${JSON.stringify(userAttributes)}`);
      console.log("\n[STEP 1] Sending download request to backend...");

      const startTime = performance.now();

      const response = await fetch(
        `http://localhost:5000/api/download/${accessCode.toUpperCase()}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            attributes: userAttributes,
          }),
        }
      );

      if (!response.ok) {
        let errorMessage = "Failed to download file";
        try {
          const error = await response.json();
          errorMessage = error.error || errorMessage;
        } catch {
          errorMessage = `Server error: ${response.status}`;
        }
        console.error(`❌ Backend error (${response.status}):`, errorMessage);
        throw new Error(errorMessage);
      }

      console.log("\n[STEP 2] File received from backend");
      const blob = await response.blob();
      const downloadTime = performance.now() - startTime;

      console.log(`✅ Download completed in ${downloadTime.toFixed(2)}ms`);
      console.log(`📦 File size: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);

      console.log("\n[STEP 3] Initiating browser download...");
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `downloaded_file`;
      link.click();
      window.URL.revokeObjectURL(url);

      console.log(`✅ Download started`);

      console.log("\n" + "=".repeat(60));
      console.log("✅ FILE DOWNLOAD COMPLETED SUCCESSFULLY");
      console.log("=".repeat(60));
      console.log(`\n📊 Summary:`);
      console.log(`   ├─ Access Code: ${accessCode}`);
      console.log(`   ├─ User ID: ${userId}`);
      console.log(`   ├─ User Role: ${userRole}`);
      console.log(`   ├─ File Size: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);
      console.log(`   ├─ Download Time: ${downloadTime.toFixed(2)}ms`);
      console.log(`   ├─ Decryption: ABE (Backend)`);
      console.log(`   └─ Status: Success\n`);

      toast.dismiss();
      toast.success("✅ File downloaded successfully!");
      setAccessCode("");
    } catch (err: any) {
      console.error("\n❌ DOWNLOAD ERROR:", err);
      console.log("=".repeat(60) + "\n");
      toast.dismiss();

      if (err.message.includes("Failed to fetch")) {
        toast.error(
          "❌ Cannot connect to backend. Make sure http://localhost:5000 is running"
        );
      } else {
        toast.error(err?.message || "Failed to download file");
      }
    } finally {
      setDownloading(false);
    }
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-foreground font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <header className="border-b border-border bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-primary hover:text-primary/80 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Upload
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Receive File</h1>
              <p className="text-muted-foreground mt-2">
                Enter the access code to download a file
              </p>
            </div>
            {user && (
              <div className="text-right">
                <p className="text-sm text-foreground font-medium">{user.email}</p>
                <p className="text-xs text-muted-foreground capitalize">
                  Role: {user.role}
                </p>
              </div>
            )}
          </div>
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
                <strong>ℹ️ Note:</strong> Your file will be automatically
                decrypted by the backend before download.
                {user ? (
                  <span className="block mt-2">
                    <strong>Your role ({user.role}):</strong> Will be used for
                    access control
                  </span>
                ) : (
                  <span className="block mt-2">
                    <strong>Downloading as:</strong> Guest user
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
