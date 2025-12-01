import { useState, useEffect } from "react";
import { FileUpload } from "@/components/FileUpload";
import { ShareResult } from "@/components/ShareResult";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Share2, Download, LogOut, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

// Simple AES-GCM file encryption/decryption utilities
async function deriveKey(password: string, salt: Uint8Array) {
  const enc = new TextEncoder();
  const baseKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: salt as unknown as BufferSource,
      iterations: 100_000,
      hash: "SHA-256",
    },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

export async function encryptFile(file: File, password: string): Promise<Blob> {
  const data = await file.arrayBuffer();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKey(password, salt);

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    data
  );

  const combined = new Uint8Array(salt.byteLength + iv.byteLength + ciphertext.byteLength);
  combined.set(salt, 0);
  combined.set(iv, salt.byteLength);
  combined.set(new Uint8Array(ciphertext), salt.byteLength + iv.byteLength);

  return new Blob([combined], { type: "application/octet-stream" });
}

export async function decryptFile(blob: Blob, password: string): Promise<Blob> {
  const combined = new Uint8Array(await blob.arrayBuffer());

  if (combined.byteLength < 28) {
    throw new Error("Invalid encrypted file format");
  }

  const salt = combined.slice(0, 16);
  const iv = combined.slice(16, 28);
  const ciphertext = combined.slice(28);

  const key = await deriveKey(password, salt);

  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    ciphertext
  );

  return new Blob([plaintext], { type: "application/octet-stream" });
}

const Index = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{
    accessCode: string;
    shareLink: string;
  } | null>(null);
  const [user, setUser] = useState<{ id: string; email: string; role: string } | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [selectedRole, setSelectedRole] = useState("employee");
  const [authLoading, setAuthLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [authCooldown, setAuthCooldown] = useState(0);

  const roles = ["Manager", "HR", "Employee"];
  const allowedRoles = ["manager", "hr"];

  // Check user session on mount
  useEffect(() => {
    const checkSession = async () => {
      try {
        setLoading(true);
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("Session error:", sessionError);
          setLoading(false);
          return;
        }

        if (session?.user) {
          const { data: userData, error: userError } = await supabase
            .from("users")
            .select("role")
            .eq("id", session.user.id)
            .single();

          if (userError && userError.code !== "PGRST116") {
            console.error("User fetch error:", userError);
          }

          const role = (userData as any)?.role ?? "employee";
          setUser({
            id: session.user.id,
            email: session.user.email || "",
            role,
          });
        }
      } catch (error) {
        console.error("Error checking session:", error);
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "SIGNED_OUT") {
        setUser(null);
      } else if (event === "SIGNED_IN" || event === "USER_UPDATED") {
        if (session?.user) {
          try {
            const { data: userData, error: userError } = await supabase
              .from("users")
              .select("role")
              .eq("id", session.user.id)
              .single();

            const role = (userData as any)?.role ?? "employee";
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
              role: "employee",
            });
          }
        }
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

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
    const code = Math.random().toString(36).substring(2, 8).toUpperCase();
    return code;
  };

  const handleSignup = async () => {
    if (!email.trim()) {
      toast.error("Please enter an email");
      return;
    }
    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setAuthLoading(true);
    try {
      // Map role names to lowercase
      const roleMapping: { [key: string]: string } = {
        "manager": "manager",
        "hr": "hr",
        "employee": "user"
      };
      
      const mappedRole = roleMapping[selectedRole.toLowerCase()] || "user";

      const { data: authData, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            role: mappedRole,
          },
          emailRedirectTo: `${window.location.origin}`,
        },
      });

      if (authError) {
        console.error("Auth error:", authError);
        
        if (authError.message.includes("only request this after")) {
          const match = authError.message.match(/after (\d+) seconds/);
          const seconds = match ? parseInt(match[1]) : 60;
          setAuthCooldown(seconds);
          
          let countdown = seconds;
          const interval = setInterval(() => {
            countdown--;
            setAuthCooldown(countdown);
            if (countdown <= 0) clearInterval(interval);
          }, 1000);
          
          toast.error(`Please wait ${seconds} seconds before trying again`);
          setAuthLoading(false);
          return;
        }
        
        throw authError;
      }

      if (authData.user) {
        // Insert user into users table with correct role
        const { error: insertError } = await supabase
          .from("users")
          .insert([
            {
              id: authData.user.id,
              email: email,
              role: mappedRole,
              created_at: new Date().toISOString(),
            }
          ]);

        if (insertError && insertError.code !== "23505") { // Ignore duplicate key errors
          console.error("Insert error:", insertError);
        }

        setUser({
          id: authData.user.id,
          email,
          role: mappedRole,
        });
      }

      setShowAuthModal(false);
      resetAuthForm();
      toast.success("Account created successfully! You can now login.");
    } catch (err: any) {
      console.error("Signup error:", err);
      toast.error(err?.message || "Failed to create account");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogin = async () => {
    if (!email.trim()) {
      toast.error("Please enter an email");
      return;
    }
    if (!password) {
      toast.error("Please enter a password");
      return;
    }

    setAuthLoading(true);
    try {
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) {
        console.error("Login error:", authError);
        
        if (authError.message.includes("only request this after")) {
          const match = authError.message.match(/after (\d+) seconds/);
          const seconds = match ? parseInt(match[1]) : 60;
          setAuthCooldown(seconds);
          
          let countdown = seconds;
          const interval = setInterval(() => {
            countdown--;
            setAuthCooldown(countdown);
            if (countdown <= 0) clearInterval(interval);
          }, 1000);
          
          toast.error(`Please wait ${seconds} seconds before trying again`);
          setAuthLoading(false);
          return;
        }
        
        throw authError;
      }

      if (authData.user) {
        try {
          const { data: userData, error: userError } = await supabase
            .from("users")
            .select("role")
            .eq("id", authData.user.id)
            .single();

          if (userError && userError.code !== "PGRST116") {
            console.error("User fetch error:", userError);
          }

          // FIX: Ensure role is correctly retrieved and defaults to 'user' if not found
          const role = (userData as any)?.role ?? "user";
          
          console.log(`✅ Login successful - User role: ${role}`);

          setUser({
            id: authData.user.id,
            email: authData.user.email || "",
            role,
          });
        } catch (error) {
          console.error("Error fetching user role:", error);
          setUser({
            id: authData.user.id,
            email: authData.user.email || "",
            role: "user",
          });
        }
      }

      setShowAuthModal(false);
      resetAuthForm();
      toast.success("Logged in successfully!");
    } catch (err: any) {
      console.error("Login error:", err);
      toast.error(err?.message || "Failed to login");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      setUser(null);
      setSelectedFile(null);
      setUploadResult(null);
      toast.success("Logged out successfully");
    } catch (err) {
      console.error("Logout error:", err);
      toast.error("Failed to logout");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    if (!user) {
      toast.error("Please login first");
      return;
    }

    if (!allowedRoles.includes(user.role)) {
      toast.error(`Only HR and Managers can upload files. Your role: ${user.role}`);
      return;
    }

    setUploading(true);
    try {
      const accessCode = await generateAccessCode();

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('user_id', user.id);
      formData.append('access_code', accessCode);
      formData.append('user_role', user.role);
      formData.append('department', 'general');

      toast.loading("📤 Sending file to backend for encryption...");

      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Backend error response:", data);
        throw new Error(data.error || 'Upload failed');
      }

      const shareLink = `${window.location.origin}/download?code=${data.access_code}`;

      setUploadResult({
        accessCode: data.access_code,
        shareLink,
      });

      toast.dismiss();
      toast.success("✅ File encrypted and uploaded successfully!");

    } catch (err: any) {
      console.error("Upload error:", err);
      toast.dismiss();
      
      if (err.message.includes("Failed to fetch")) {
        toast.error("❌ Cannot connect to backend. Make sure http://localhost:5000 is running");
      } else {
        toast.error(err?.message || "Failed to upload file");
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async () => {
    if (!uploadResult?.accessCode) {
      toast.error("No file to download");
      return;
    }

    try {
      console.log("\n" + "=".repeat(60));
      console.log("📥 FILE DOWNLOAD & DECRYPTION PROCESS (FRONTEND)");
      console.log("=".repeat(60));
      
      toast.loading("📥 Connecting to backend...");
      console.log(`\n🎯 Access Code: ${uploadResult.accessCode}`);

      // FIX: Make sure user role is correctly passed
      const userRole = user?.role || 'user';
      console.log(`👤 User ID: ${user?.id}`);
      console.log(`👥 User Role: ${userRole}`);

      const userAttributes = {
        role: userRole,
        department: 'general'
      };

      console.log(`📋 User Attributes: ${JSON.stringify(userAttributes)}`);

      console.log("\n[STEP 1] Requesting decrypted file from backend...");
      
      const startTime = performance.now();
      
      const response = await fetch(
        `http://localhost:5000/api/download/${uploadResult.accessCode}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user?.id,
            attributes: userAttributes,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        console.error("❌ Backend error:", error);
        throw new Error(error.error || 'Failed to download file');
      }

      console.log("\n[STEP 2] Processing decrypted file...");
      
      const blob = await response.blob();
      const downloadTime = performance.now() - startTime;
      
      console.log(`✅ File received from backend in ${downloadTime.toFixed(2)}ms`);
      console.log(`📦 File size: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);

      console.log("\n[STEP 3] Initiating browser download...");
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `decrypted_file`;
      link.click();
      window.URL.revokeObjectURL(url);
      
      console.log(`✅ Download started`);

      console.log("\n" + "=".repeat(60));
      console.log("✅ FILE DOWNLOAD COMPLETED SUCCESSFULLY");
      console.log("=".repeat(60));
      console.log(`\n📊 Summary:`);
      console.log(`   ├─ Access Code: ${uploadResult.accessCode}`);
      console.log(`   ├─ User ID: ${user?.id}`);
      console.log(`   ├─ User Role: ${userRole}`);
      console.log(`   ├─ File Size: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);
      console.log(`   ├─ Download Time: ${downloadTime.toFixed(2)}ms`);
      console.log(`   ├─ Decryption: ABE (Backend)`);
      console.log(`   └─ Status: Success\n`);

      toast.dismiss();
      toast.success("✅ File downloaded successfully!");

    } catch (err: any) {
      console.error("\n❌ DOWNLOAD ERROR:", err);
      console.log("=".repeat(60) + "\n");
      toast.dismiss();
      
      if (err.message.includes("Failed to fetch")) {
        toast.error("❌ Cannot connect to backend. Make sure http://localhost:5000 is running");
      } else {
        toast.error(err?.message || "Failed to download file");
      }
    }
  };

  const handleNewUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
  };

  const resetAuthForm = () => {
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setSelectedRole("employee");
    setIsSignup(false);
  };

  const isUserAllowedToUpload = user && allowedRoles.includes(user.role);

  if (loading) {
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
      <header className="border-b border-border bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Share2 className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-foreground">FileShare</h1>
            </div>
            <div className="flex items-center gap-3">
              {user ? (
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-foreground font-medium">{user.email}</p>
                    <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={handleLogout}
                    className="gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </Button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <Button
                    onClick={() => {
                      setIsSignup(false);
                      setShowAuthModal(true);
                    }}
                    className="bg-gradient-primary"
                  >
                    Login
                  </Button>
                  <Button
                    onClick={() => {
                      setIsSignup(true);
                      setShowAuthModal(true);
                    }}
                    variant="outline"
                  >
                    Sign Up
                  </Button>
                </div>
              )}
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
        </div>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg shadow-2xl p-8 max-w-md w-full mx-4 border border-border">
            <h2 className="text-2xl font-bold text-foreground mb-6">
              {isSignup ? "Create Account" : "Login"}
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={authLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={authLoading}
                />
              </div>

              {isSignup && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={authLoading}
                  />
                </div>
              )}

              {isSignup && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Select Your Role
                  </label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={authLoading}
                  >
                    {roles.map((role) => (
                      <option key={role} value={role.toLowerCase()}>
                        {role}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAuthModal(false);
                  resetAuthForm();
                }}
                className="flex-1"
                disabled={authLoading}
              >
                Cancel
              </Button>
              <Button
                onClick={isSignup ? handleSignup : handleLogin}
                disabled={authLoading || authCooldown > 0}
                className="flex-1 bg-gradient-primary"
              >
                {authCooldown > 0
                  ? `Wait ${authCooldown}s`
                  : authLoading
                  ? isSignup
                    ? "Creating Account..."
                    : "Logging in..."
                  : isSignup
                  ? "Sign Up"
                  : "Login"}
              </Button>
            </div>

            <div className="mt-4 text-center">
              <p className="text-sm text-muted-foreground">
                {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
                <button
                  onClick={() => setIsSignup(!isSignup)}
                  className="text-primary hover:underline font-medium"
                  disabled={authLoading}
                >
                  {isSignup ? "Login" : "Sign Up"}
                </button>
              </p>
            </div>
          </div>
        </div>
      )}

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

            {user ? (
              <>
                {!isUserAllowedToUpload && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-yellow-900">
                        Upload Access Restricted
                      </h3>
                      <p className="text-sm text-yellow-800">
                        Only HR and Manager roles can upload files. Your current role is{" "}
                        <span className="font-semibold capitalize">{user.role}</span>.
                      </p>
                    </div>
                  </div>
                )}

                {isUserAllowedToUpload && (
                  <>
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      selectedFile={selectedFile}
                      onClear={handleClear}
                    />

                    {selectedFile && (
                      <div className="space-y-4">
                        <div className="flex justify-center">
                          <Button
                            onClick={handleUpload}
                            disabled={uploading}
                            size="lg"
                            className="bg-gradient-primary shadow-custom-lg hover:shadow-custom-xl transition-all px-12"
                          >
                            {uploading ? "Uploading & Encrypting..." : "Upload & Encrypt"}
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-lg text-muted-foreground mb-4">
                  Please login or create an account to upload files
                </p>
                <div className="flex gap-3 justify-center">
                  <Button
                    onClick={() => {
                      setIsSignup(false);
                      setShowAuthModal(true);
                    }}
                    size="lg"
                    className="bg-gradient-primary"
                  >
                    Login
                  </Button>
                  <Button
                    onClick={() => {
                      setIsSignup(true);
                      setShowAuthModal(true);
                    }}
                    size="lg"
                    variant="outline"
                  >
                    Sign Up
                  </Button>
                </div>
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
                <h3 className="font-semibold text-foreground">Encrypt</h3>
                <p className="text-sm text-muted-foreground">
                  Files are encrypted with ABE
                </p>
              </div>
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold text-foreground">Share</h3>
                <p className="text-sm text-muted-foreground">
                  Share code & password securely
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

        {uploadResult && (
          <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-green-900">✅ Upload Successful!</h3>
            
            <div className="space-y-2">
              <p className="text-sm text-green-800">
                <strong>Access Code:</strong> {uploadResult.accessCode}
              </p>
              <p className="text-sm text-green-800 break-all">
                <strong>Share Link:</strong> {uploadResult.shareLink}
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => {
                  navigator.clipboard.writeText(uploadResult.shareLink);
                  toast.success("Link copied to clipboard!");
                }}
                variant="outline"
                className="flex-1"
              >
                📋 Copy Link
              </Button>
              
              <Button
                onClick={handleDownload}
                className="flex-1 bg-gradient-primary"
              >
                📥 Download File
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
