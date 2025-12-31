import { useState, useRef } from 'react';
import { Upload, Database, Globe, FileJson, FileSpreadsheet, Files, Loader2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { fileService } from '@/services/fileService';

const uploadOptions = [
  { type: 'csv', label: 'CSV File', icon: FileSpreadsheet, color: 'text-success', accept: '.csv' },
  { type: 'excel', label: 'Excel', icon: FileSpreadsheet, color: 'text-success', accept: '.xlsx,.xls' },
  { type: 'json', label: 'JSON', icon: FileJson, color: 'text-warning', accept: '.json' },
];

const connectionOptions = [
  { type: 'database', label: 'Database', icon: Database, color: 'text-info' },
  { type: 'api', label: 'REST API', icon: Globe, color: 'text-primary' },
];

export function UploadZone() {
  const { addDataSource } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [connectionType, setConnectionType] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const multiFileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  // Upload files to the backend and track status
  const uploadFilesToBackend = async (files: File[]) => {
    setIsUploading(true);
    setUploadError(null);
    
    for (const file of files) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      const type = extension === 'csv' ? 'csv' : extension === 'json' ? 'json' : 'excel';
      
      try {
        // Upload to backend
        const response = await fileService.uploadFile(file);
        console.log('File uploaded successfully:', response);
        
        // Add to local state after successful upload
        addDataSource({
          name: file.name,
          type: type as 'csv' | 'excel' | 'json',
          status: 'connected',
        });
      } catch (error) {
        console.error('File upload failed:', error);
        setUploadError(`Failed to upload ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        
        // Still add to local state but mark as error
        addDataSource({
          name: file.name,
          type: type as 'csv' | 'excel' | 'json',
          status: 'error',
        });
      }
    }
    
    setIsUploading(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    await uploadFilesToBackend(files);
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    await uploadFilesToBackend(files);
    // Reset input so same file can be selected again
    e.target.value = '';
  };

  const handleFileUpload = (type: string, accept: string) => {
    if (fileInputRef.current) {
      fileInputRef.current.accept = accept;
      fileInputRef.current.click();
    }
  };

  const handleMultiFileUpload = () => {
    if (multiFileInputRef.current) {
      multiFileInputRef.current.click();
    }
  };

  const handleConnection = (type: string) => {
    setConnectionType(type);
    setShowConnectionModal(true);
  };

  const confirmConnection = () => {
    if (connectionType) {
      addDataSource({
        name: connectionType === 'database' ? 'PostgreSQL Database' : 'External API',
        type: connectionType as 'database' | 'api',
        status: 'connected',
      });
    }
    setShowConnectionModal(false);
    setConnectionType(null);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-3xl"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-foreground mb-2">
            Connect Your Data
          </h1>
          <p className="text-muted-foreground">
            Upload files or connect to external data sources to begin analysis
          </p>
          
          {/* Upload status indicators */}
          {isUploading && (
            <div className="mt-4 flex items-center justify-center gap-2 text-primary">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm font-medium">Uploading files...</span>
            </div>
          )}
          
          {uploadError && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {uploadError}
            </div>
          )}
        </div>

        {/* Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={cn(
            'relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300',
            isDragging
              ? 'border-primary bg-primary/5 scale-[1.02]'
              : 'border-border hover:border-muted-foreground/50',
            isUploading && 'opacity-75 pointer-events-none'
          )}
        >
          <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent" />
          </div>

          <div className="relative">
            <div className={cn(
              'w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center transition-colors',
              isDragging ? 'bg-primary/20' : 'bg-muted'
            )}>
              {isUploading ? (
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              ) : (
                <Upload className={cn(
                  'w-8 h-8 transition-colors',
                  isDragging ? 'text-primary' : 'text-muted-foreground'
                )} />
              )}
            </div>

            <p className="text-lg font-medium text-foreground mb-1">
              {isUploading ? 'Uploading...' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-muted-foreground mb-6">
              or choose an option below
            </p>


            {/* Hidden file inputs */}
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileInputChange}
            />
            <input
              ref={multiFileInputRef}
              type="file"
              multiple
              accept=".csv,.xlsx,.xls,.json"
              className="hidden"
              onChange={handleFileInputChange}
            />

            {/* File Upload Options */}
            <div className="flex items-center justify-center gap-3 mb-6 flex-wrap">
              {uploadOptions.map((option) => (
                <Button
                  key={option.type}
                  variant="outline"
                  onClick={() => handleFileUpload(option.type, option.accept)}
                  className="gap-2"
                >
                  <option.icon className={cn('w-4 h-4', option.color)} />
                  {option.label}
                </Button>
              ))}
              <Button
                variant="outline"
                onClick={handleMultiFileUpload}
                className="gap-2 border-primary/50 hover:border-primary"
              >
                <Files className="w-4 h-4 text-primary" />
                Multiple Files
              </Button>
            </div>

            <div className="flex items-center gap-4 justify-center text-muted-foreground text-sm">
              <div className="h-px w-16 bg-border" />
              <span>or connect to</span>
              <div className="h-px w-16 bg-border" />
            </div>

            {/* Connection Options */}
            <div className="flex items-center justify-center gap-3 mt-6">
              {connectionOptions.map((option) => (
                <Button
                  key={option.type}
                  variant="secondary"
                  onClick={() => handleConnection(option.type)}
                  className="gap-2"
                >
                  <option.icon className={cn('w-4 h-4', option.color)} />
                  {option.label}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Connection Modal */}
      <AnimatePresence>
        {showConnectionModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setShowConnectionModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card rounded-2xl p-6 w-full max-w-md border border-border shadow-elevated"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-foreground mb-4">
                Connect to {connectionType === 'database' ? 'Database' : 'API'}
              </h3>

              <div className="space-y-4">
                {connectionType === 'database' ? (
                  <>
                    <input
                      type="text"
                      placeholder="Host"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                    <input
                      type="text"
                      placeholder="Database Name"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                    <input
                      type="text"
                      placeholder="Username"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                    <input
                      type="password"
                      placeholder="Password"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </>
                ) : (
                  <>
                    <input
                      type="text"
                      placeholder="API Endpoint URL"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                    <input
                      type="text"
                      placeholder="API Key (optional)"
                      className="w-full bg-muted rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowConnectionModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button onClick={confirmConnection} className="flex-1">
                  Connect
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
