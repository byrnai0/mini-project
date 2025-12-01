import { Button } from "@/components/ui/button";

interface ShareResultProps {
  accessCode: string;
  shareLink: string;
  onNewUpload: () => void;
}

export const ShareResult = ({
  accessCode,
  shareLink,
  onNewUpload,
}: ShareResultProps) => {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-4xl font-bold text-foreground">
          Share Files Securely
        </h2>
        <p className="text-lg text-muted-foreground">
          Your file has been successfully encrypted and uploaded
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-semibold text-green-900">✅ Upload Successful!</h3>
        
        <div className="space-y-2">
          <p className="text-sm text-green-800">
            <strong>Access Code:</strong> <span className="font-mono">{accessCode}</span>
          </p>
          <p className="text-sm text-green-800 break-all">
            <strong>Share Link:</strong> <span className="font-mono text-xs">{shareLink}</span>
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={() => {
              navigator.clipboard.writeText(shareLink);
              alert("Link copied to clipboard!");
            }}
            variant="outline"
            className="flex-1"
          >
            📋 Copy Link
          </Button>
          
          <Button
            onClick={onNewUpload}
            className="flex-1 bg-gradient-primary"
          >
            📤 Upload Another File
          </Button>
        </div>
      </div>
    </div>
  );
};
