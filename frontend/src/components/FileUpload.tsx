import React, { useState, useCallback } from "react";
import { Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { uploadFile } from "../lib/api";
import { supabase } from "../integrations/supabase/client";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  onUploadSuccess?: (result: any) => void;
  onUploadError?: (error: string) => void;
}

type UploadResponse = {
  cid: string;
  filename?: string;
  file_size?: number;
};

export const FileUpload = ({
  onFileSelect,
  selectedFile,
  onClear,
  onUploadSuccess,
  onUploadError,
}: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        onFileSelect(files[0]);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const genAccessCode = () => {
    return Math.random().toString(36).slice(2, 10).toUpperCase();
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError("");
    setUploadStatus("Preparing upload...");

    try {
      // Get user info from localStorage
      const bcid = localStorage.getItem("bcid");
      const userAttributes = localStorage.getItem("userAttributes");

      if (!bcid) {
        throw new Error("User not authenticated. Please register first.");
      }

      const accessCode = genAccessCode();
      
      // Parse access policy from user attributes
      let accessPolicy = {};
      if (userAttributes) {
        try {
          const attrs = JSON.parse(userAttributes);
          // Create access policy from user's own attributes
          accessPolicy = {
            role: attrs.role || "user",
            department: attrs.department || "general",
          };
        } catch (e) {
          console.warn("Could not parse user attributes");
        }
      }

      setUploadStatus("Encrypting file...");

      // Call backend upload endpoint
      const resJson = await uploadFile({
        file: selectedFile,
        bcid,
        accessPolicy,
        accessCode,
      });

      const { cid, filename, file_size } = resJson as UploadResponse;
      const fileName = filename ?? selectedFile.name;
      const fileSize = file_size ?? selectedFile.size;

      setUploadStatus("Storing metadata...");

      // Store mapping in Supabase file_shares table
      const { error: dbError } = await supabase
        .from("file_shares")
        .insert(
          [
            {
              file_path: cid,
              file_name: fileName,
              file_size: fileSize,
              access_code: accessCode,
              owner_bcid: bcid,
              access_policy: JSON.stringify(accessPolicy),
            },
          ] as any
        );

      if (dbError) {
        console.error("Database error:", dbError);
      }

      setUploadStatus("Upload complete!");

      const shareLink = `${window.location.origin}/download?code=${accessCode}`;

      // Call success callback
      if (onUploadSuccess) {
        onUploadSuccess({
          cid,
          fileName,
          fileSize,
          accessCode,
          shareLink,
          bcid,
        });
      }

      // Clear after successful upload
      setTimeout(() => {
        onClear();
        setUploadStatus("");
      }, 2000);

    } catch (err: any) {
      console.error("Upload error:", err);
      const errorMsg = err.message || err.error || "Upload failed. Please try again.";
      setError(errorMsg);
      if (onUploadError) {
        onUploadError(errorMsg);
      }
    } finally {
      setUploading(false);
    }
  };

  if (selectedFile) {
    return (
      <div className="bg-primary/5 border-2 border-primary/20 rounded-lg p-6 text-center">
        <div className="flex items-center justify-center gap-3 mb-3">
          <Upload className="w-5 h-5 text-primary" />
          <span className="text-lg font-semibold text-foreground">
            {selectedFile.name}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
        </p>
        <Button
          onClick={onClear}
          variant="outline"
          className="gap-2"
        >
          <X className="w-4 h-4" />
          Clear Selection
        </Button>
      </div>
    );
  }

  return (
    <label className="border-2 border-dashed border-border rounded-lg p-12 text-center cursor-pointer hover:border-primary/50 transition-colors bg-background/50">
      <input
        type="file"
        onChange={handleFileInput}
        className="hidden"
      />
      <div className="space-y-2">
        <Upload className="w-12 h-12 text-muted-foreground mx-auto" />
        <div>
          <p className="font-semibold text-foreground">
            Click to upload or drag and drop
          </p>
          <p className="text-sm text-muted-foreground">
            Max file size: 100 MB
          </p>
        </div>
      </div>
    </label>
  );
};
