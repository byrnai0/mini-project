import { Copy, Check, Download } from "lucide-react";
import { useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";

interface ShareResultProps {
  accessCode: string;
  shareLink: string;
  onNewUpload: () => void;
}

export const ShareResult = ({ accessCode, shareLink, onNewUpload }: ShareResultProps) => {
  const [copiedCode, setCopiedCode] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const copyToClipboard = async (text: string, type: "code" | "link") => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === "code") {
        setCopiedCode(true);
        setTimeout(() => setCopiedCode(false), 2000);
      } else {
        setCopiedLink(true);
        setTimeout(() => setCopiedLink(false), 2000);
      }
      toast.success("Copied to clipboard!");
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
          <Check className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold mb-2 text-foreground">File Uploaded!</h2>
        <p className="text-muted-foreground">
          Share the code or link below to let others download your file
        </p>
      </div>

      <Card className="p-8 shadow-custom-xl border-border">
        <div className="space-y-6">
          {/* Access Code */}
          <div>
            <label className="text-sm font-medium text-muted-foreground block mb-2">
              Access Code
            </label>
            <div className="flex gap-2">
              <div className="flex-1 bg-muted rounded-lg px-4 py-3 font-mono text-2xl font-bold text-center tracking-wider text-foreground">
                {accessCode}
              </div>
              <Button
                onClick={() => copyToClipboard(accessCode, "code")}
                size="icon"
                variant="outline"
                className="h-auto"
              >
                {copiedCode ? (
                  <Check className="w-5 h-5 text-primary" />
                ) : (
                  <Copy className="w-5 h-5" />
                )}
              </Button>
            </div>
          </div>

          {/* Share Link */}
          <div>
            <label className="text-sm font-medium text-muted-foreground block mb-2">
              Share Link
            </label>
            <div className="flex gap-2">
              <div className="flex-1 bg-muted rounded-lg px-4 py-3 text-sm truncate text-foreground">
                {shareLink}
              </div>
              <Button
                onClick={() => copyToClipboard(shareLink, "link")}
                size="icon"
                variant="outline"
                className="h-auto"
              >
                {copiedLink ? (
                  <Check className="w-5 h-5 text-primary" />
                ) : (
                  <Copy className="w-5 h-5" />
                )}
              </Button>
            </div>
          </div>

          {/* QR Code */}
          <div>
            <label className="text-sm font-medium text-muted-foreground block mb-3">
              QR Code
            </label>
            <div className="flex justify-center p-6 bg-white rounded-lg">
              <QRCodeSVG value={shareLink} size={200} level="H" />
            </div>
            <p className="text-xs text-center text-muted-foreground mt-2">
              Scan this QR code to access the file
            </p>
          </div>

          <div className="pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground text-center mb-4">
              This link will expire in 7 days
            </p>
            <Button
              onClick={onNewUpload}
              variant="outline"
              className="w-full"
            >
              <Download className="w-4 h-4 mr-2" />
              Upload Another File
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
