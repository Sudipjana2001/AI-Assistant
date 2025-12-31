import { useEffect, useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { RefreshCw, Power } from 'lucide-react';
import { databricksService, Cluster } from '@/services/databricksService';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface ClusterSelectorProps {
  selectedId: string | undefined;
  onSelect: (id: string) => void;
}

export function ClusterSelector({ selectedId, onSelect }: ClusterSelectorProps) {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadClusters();
  }, []);

  const loadClusters = async () => {
    setLoading(true);
    try {
      const data = await databricksService.listClusters();
      setClusters(data);
      // Auto-select first running cluster if none selected
      if (!selectedId && data.length > 0) {
        const running = data.find(c => c.state === 'RUNNING');
        if (running) onSelect(running.cluster_id);
      }
    } catch (error) {
      console.error('Failed to load clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (state: string) => {
    switch (state) {
      case 'RUNNING': return 'bg-green-500';
      case 'TERMINATED': return 'bg-red-500';
      case 'PENDING': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const activeCluster = clusters.find(c => c.cluster_id === selectedId);

  const handleStart = async () => {
    if (!selectedId) return;
    toast.promise(databricksService.startCluster(selectedId), {
       loading: 'Starting cluster...',
       success: 'Cluster start initiated',
       error: 'Failed to start cluster'
    });
    // Optimistic update
    setClusters(clusters.map(c => c.cluster_id === selectedId ? { ...c, state: 'PENDING' } : c));
  };

  const handleStop = async () => {
    if (!selectedId) return;
    toast.promise(databricksService.stopCluster(selectedId), {
       loading: 'Terminating cluster...',
       success: 'Cluster termination initiated',
       error: 'Failed to terminate cluster'
    });
    // Optimistic update
    setClusters(clusters.map(c => c.cluster_id === selectedId ? { ...c, state: 'TERMINATING' } : c));
  };

  return (
    <div className="flex items-center gap-2">
      <Select value={selectedId} onValueChange={onSelect}>
        <SelectTrigger className="w-[240px] h-8 text-xs">
          <div className="flex items-center gap-2 w-full">
            {activeCluster ? (
              <>
                <div className={cn("w-2 h-2 rounded-full", getStatusColor(activeCluster.state))} />
                <span className="truncate flex-1 text-left">{activeCluster.cluster_name}</span>
                <span className="text-muted-foreground text-[10px] uppercase mr-2">{activeCluster.state}</span>
              </>
            ) : (
              <span className="text-muted-foreground">Select Cluster</span>
            )}
          </div>
        </SelectTrigger>
        <SelectContent>
          {clusters.map((cluster) => (
            <SelectItem key={cluster.cluster_id} value={cluster.cluster_id}>
              <div className="flex items-center gap-2">
                <div className={cn("w-2 h-2 rounded-full", getStatusColor(cluster.state))} />
                <span>{cluster.cluster_name}</span>
                <span className="text-muted-foreground ml-auto text-[10px] uppercase">{cluster.state}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {/* Cluster Controls */}
      {selectedId && activeCluster && (
         <>
            {activeCluster.state === 'TERMINATED' && (
              <Button size="sm" variant="outline" className="h-8 gap-1.5 text-xs text-green-600 hover:text-green-700 hover:bg-green-50" onClick={handleStart}>
                <Power className="w-3.5 h-3.5" />
                Start
              </Button>
            )}
            
            {(activeCluster.state === 'RUNNING' || activeCluster.state === 'PENDING') && (
              <Button size="sm" variant="outline" className="h-8 gap-1.5 text-xs text-destructive hover:text-destructive hover:bg-destructive/10" onClick={handleStop}>
                <Power className="w-3.5 h-3.5" />
                Stop
              </Button>
            )}
         </>
      )}

      <Button 
        variant="ghost" 
        size="icon" 
        className="h-8 w-8"
        onClick={loadClusters}
        disabled={loading}
      >
        <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
      </Button>
    </div>
  );
}
