import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Download, X, FileText, Image, AlertCircle } from 'lucide-react';
import { leaveAPI } from '../lib/api';

export function FileViewer({ isOpen, onClose, leaveId, filename, mimetype }) {
  const [fileUrl, setFileUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadedLeaveId, setLoadedLeaveId] = useState(null); // Track which file is loaded

  useEffect(() => {
    let isMounted = true;

    const loadFile = async () => {
      // Skip if already loaded the same file
      if (!isOpen || !leaveId || loadedLeaveId === leaveId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const blob = await leaveAPI.downloadAttachment(leaveId);
        if (isMounted) {
          const url = URL.createObjectURL(blob);
          setFileUrl(url);
          setLoadedLeaveId(leaveId); // Mark this file as loaded
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to load file');
          console.error('Error loading file:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    if (isOpen && leaveId) {
      loadFile();
    }

    return () => {
      isMounted = false;
    };
  }, [isOpen, leaveId]); // Removed loadedLeaveId from dependencies to prevent infinite loop

  // Separate effect for cleanup
  useEffect(() => {
    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [fileUrl]);

  // Reset state when dialog closes
  useEffect(() => {
    if (!isOpen) {
      setFileUrl(null);
      setLoadedLeaveId(null);
      setError(null);
      setLoading(false);
    }
  }, [isOpen]);

  const handleDownload = async () => {
    try {
      const blob = await leaveAPI.downloadAttachmentFile(leaveId); // Use new download endpoint
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading file:', err);
    }
  };

  const isImage = () => {
    return mimetype && mimetype.startsWith('image/');
  };

  const isPDF = () => {
    return mimetype === 'application/pdf';
  };

  const isDocument = () => {
    return mimetype && (
      mimetype.includes('word') || 
      mimetype.includes('document') ||
      mimetype === 'application/msword' ||
      mimetype === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );
  };

  const renderFileContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading file...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center text-red-500">
            <AlertCircle className="h-12 w-12 mx-auto mb-4" />
            <p>{error}</p>
          </div>
        </div>
      );
    }

    if (!fileUrl) return null;

    if (isImage()) {
      return (
        <div className="flex justify-center p-4">
          <img 
            src={fileUrl} 
            alt={filename}
            className="max-w-full max-h-96 object-contain rounded-lg shadow-lg"
            onError={() => setError('Failed to load image')}
          />
        </div>
      );
    }

    if (isPDF()) {
      return (
        <div className="h-96">
          <iframe
            src={fileUrl}
            title={filename}
            className="w-full h-full border rounded-lg"
            onError={() => setError('Failed to load PDF')}
          />
        </div>
      );
    }

    if (isDocument()) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <FileText className="h-16 w-16 mx-auto mb-4 text-blue-500" />
            <p className="text-lg font-medium mb-2">{filename}</p>
            <p className="text-gray-500 mb-4">
              Document files cannot be previewed directly in the browser.
            </p>
            <Button onClick={handleDownload} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Download to View
            </Button>
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium mb-2">{filename}</p>
          <p className="text-gray-500 mb-4">
            This file type cannot be previewed in the browser.
          </p>
          <Button onClick={handleDownload} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Download File
          </Button>
        </div>
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isImage() && <Image className="h-5 w-5" />}
              {(isPDF() || isDocument()) && <FileText className="h-5 w-5" />}
              <DialogTitle className="truncate">{filename}</DialogTitle>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
                className="flex items-center gap-1"
              >
                <Download className="h-4 w-4" />
                Download
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="flex items-center gap-1"
              >
                <X className="h-4 w-4" />
                Close
              </Button>
            </div>
          </div>
          <DialogDescription className="sr-only">
            File viewer for {filename}. You can preview the file content or download it to your device.
          </DialogDescription>
        </DialogHeader>
        
        {renderFileContent()}
        
        <div className="text-sm text-gray-500 mt-4 p-4 bg-gray-50 rounded">
          <p><strong>File:</strong> {filename}</p>
          <p><strong>Type:</strong> {mimetype || 'Unknown'}</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
