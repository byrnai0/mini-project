import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import Index from "./pages/Index";
import Download from "./pages/Download";
import NotFound from "./pages/NotFound";
import ReceiveFile from "./pages/ReceiveFile";

const queryClient = new QueryClient();

const App = () => {
  useEffect(() => {
    console.log("\n" + "=".repeat(60));
    console.log("🚀 APP INITIALIZED");
    console.log("=".repeat(60));
    console.log("📍 Frontend running at:", window.location.origin);
    console.log("🔗 Backend API at: http://localhost:5000");
    console.log("🗄️ Supabase initialized");
    console.log("=".repeat(60) + "\n");

    // Setup global auth listener
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      console.log(`\n🔄 Global auth event: ${event}`);
      if (session?.user) {
        console.log(`👤 User: ${session.user.email}`);
      } else {
        console.log("🚪 No user session");
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/receive" element={<ReceiveFile />} />
            <Route path="/download" element={<Download />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
