import { useState, useRef } from 'react';
import { Database, Globe, FileJson, FileSpreadsheet, Files, Loader2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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

interface AddDataSourceDropdownProps {
  children: React.ReactNode;
}

export function AddDataSourceDropdown({ children }: AddDataSourceDropdownProps) {
  const { addDataSource } = useAppStore();
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [connectionType, setConnectionType] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const multiFileInputRef = useRef<HTMLInputElement>(null);

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setIsUploading(true);
    
    for (const file of files) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      const type = extension === 'csv' ? 'csv' : extension === 'json' ? 'json' : 'excel';
      
      try {
        // Upload to backend
        const response = await fileService.uploadFile(file);
        console.log('File uploaded successfully:', response);
        
        addDataSource({
          name: file.name,
          type: type as 'csv' | 'excel' | 'json',
          status: 'connected',
        });
      } catch (error) {
        console.error('File upload failed:', error);
        addDataSource({
          name: file.name,
          type: type as 'csv' | 'excel' | 'json',
          status: 'error',
        });
      }
    }
    
    setIsUploading(false);
    e.target.value = '';
  };

  const handleFileUpload = (accept: string) => {
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
    <>
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

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          {children}
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          {uploadOptions.map((option) => (
            <DropdownMenuItem
              key={option.type}
              onClick={() => handleFileUpload(option.accept)}
              className="gap-2 cursor-pointer"
            >
              <option.icon className={cn('w-4 h-4', option.color)} />
              {option.label}
            </DropdownMenuItem>
          ))}
          <DropdownMenuItem
            onClick={handleMultiFileUpload}
            className="gap-2 cursor-pointer"
          >
            <Files className="w-4 h-4 text-primary" />
            Multiple Files
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          {connectionOptions.map((option) => (
            <DropdownMenuItem
              key={option.type}
              onClick={() => handleConnection(option.type)}
              className="gap-2 cursor-pointer"
            >
              <option.icon className={cn('w-4 h-4', option.color)} />
              {option.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

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
    </>
  );
}