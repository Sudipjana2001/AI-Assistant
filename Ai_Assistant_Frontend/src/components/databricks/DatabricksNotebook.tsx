import { useState, useEffect } from 'react';
import { databricksService } from '@/services/databricksService';
import { NotebookCell } from './NotebookCell';
import { ClusterSelector } from './ClusterSelector';
import { Button } from '@/components/ui/button';
import { Plus, Play, Sparkles, RotateCw, Trash, FileText, Code2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { toast } from 'sonner';

interface Cell {
  id: string;
  code: string;
  output?: string;
  status: 'idle' | 'running' | 'success' | 'error';
  type: 'code' | 'markdown';
}

export function DatabricksNotebook() {
  const { getActiveQuery } = useAppStore();
  const activeQuery = getActiveQuery();
  
  const [clusterId, setClusterId] = useState<string>();
  const [cells, setCells] = useState<Cell[]>([
    { 
      id: '1', 
      code: '# Databricks Spark Session initialized\n# This notebook is connected to your Azure Databricks cluster.\n\nprint("Spark Session Active")', 
      output: 'SparkSession - active', 
      status: 'success', 
      type: 'code' 
    },
    { 
      id: '2', 
      code: '## Analysis Overview\nThis notebook demonstrates data analysis using PySpark and Pandas on Databricks.', 
      status: 'success', 
      type: 'markdown' 
    },
    {
       id: '3',
       code: activeQuery?.code || 'import pandas as pd\nimport numpy as np\n\n# Create sample data\ndf = pd.DataFrame(np.random.randn(10, 4), columns=list("ABCD"))\nprint(df.head())',
       status: 'idle',
       type: 'code'
    }
  ]);

  // Load cluster logic can be enhanced here if needed (e.g., auto-scan)

  const addCell = (type: 'code' | 'markdown' = 'code') => {
    const newCell: Cell = {
      id: Math.random().toString(36).substr(2, 9),
      code: type === 'code' ? '' : '### New Markdown Cell',
      status: 'idle',
      type
    };
    setCells([...cells, newCell]);
  };

  const handleCellChange = (id: string, value: string) => {
    setCells(cells.map(c => c.id === id ? { ...c, code: value } : c));
  };

  const executeCell = async (id: string) => {
    const cell = cells.find(c => c.id === id);
    if (!cell) return;

    // Handle Markdown "Execution" (Just Render)
    if (cell.type === 'markdown') {
       setCells(cells.map(c => c.id === id ? { ...c, status: 'success' } : c));
       return;
    }

    if (!clusterId) {
      toast.error("Please select a Databricks cluster first");
      return;
    }

    setCells(cells.map(c => c.id === id ? { ...c, status: 'running', output: undefined } : c));
    
    try {
      const result = await databricksService.executeCode(clusterId, cell.code);
      
      setCells(cells.map(c => c.id === id ? {
        ...c,
        status: result.status === 'error' ? 'error' : 'success',
        output: result.error || result.output
      } : c));

    } catch (error) {
      setCells(cells.map(c => c.id === id ? {
        ...c,
        status: 'error',
        output: 'Failed to execute code'
      } : c));
      toast.error("Execution failed");
    }
  };

  const runAll = async () => {
    if (!clusterId) {
       toast.error("Please select a Databricks cluster first");
       return;
    }
    
    // Reset all statuses first
    setCells(prev => prev.map(c => ({ ...c, status: c.status === 'running' ? 'running' : 'idle' })));

    for (const cell of cells) {
      // Scroll into view?
      setCells(prev => prev.map(c => c.id === cell.id ? { ...c, status: 'running' } : c));
      
      try {
        if (cell.type === 'markdown') {
           // Simulate slight delay for visual flow
           await new Promise(r => setTimeout(r, 200));
           setCells(prev => prev.map(c => c.id === cell.id ? { ...c, status: 'success' } : c));
           continue;
        }

        const result = await databricksService.executeCode(clusterId, cell.code);
        
        const isError = result.status === 'error';
        setCells(prev => prev.map(c => c.id === cell.id ? {
          ...c,
          status: isError ? 'error' : 'success',
          output: result.error || result.output
        } : c));

        if (isError) {
           toast.error(`Execution stopped at cell ${cell.id}`);
           break; // Stop on error
        }

      } catch (error) {
         setCells(prev => prev.map(c => c.id === cell.id ? { ...c, status: 'error', output: 'System Error during Run All' } : c));
         break;
      }
    }
  };

  const restartKernel = async () => {
    if (!clusterId) return;
    try {
      toast.promise(databricksService.restartContext(clusterId), {
        loading: 'Restarting Kernel...',
        success: 'Kernel Restarted. Memory cleared.',
        error: 'Failed to restart kernel'
      });
      // Clear all outputs
      setCells(cells.map(c => ({ ...c, status: 'idle', output: undefined })));
    } catch (e) {
      console.error(e);
    }
  };
  
  const clearOutputs = () => {
     setCells(cells.map(c => ({ ...c, status: 'idle', output: undefined })));
     toast.success("Outputs cleared");
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Toolbar */}
      <div className="h-14 flex items-center justify-between px-4 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#ff3621]" />
            <span className="font-semibold text-foreground text-sm">Databricks Notebook</span>
          </div>
          <div className="h-4 w-px bg-border" />
          <ClusterSelector selectedId={clusterId} onSelect={setClusterId} />
        </div>
        
        <div className="flex items-center gap-2">
           <Button variant="ghost" size="sm" onClick={restartKernel} title="Restart Kernel">
             <RotateCw className="w-4 h-4 text-muted-foreground hover:text-foreground" />
           </Button>
           <Button variant="ghost" size="sm" onClick={clearOutputs} title="Clear Outputs">
             <Trash className="w-4 h-4 text-muted-foreground hover:text-foreground" />
           </Button>
           <div className="h-4 w-px bg-border mx-1" />
           <Button size="sm" variant="secondary" onClick={runAll}>
            <Play className="w-4 h-4 mr-2 fill-current" />
            Run All
          </Button>
        </div>
      </div>

      {/* Notebook Content */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar bg-secondary/10">
        <div className="max-w-5xl mx-auto space-y-4 pb-20">
          {cells.map((cell, index) => (
            <NotebookCell
              key={cell.id}
              {...cell}
              onCodeChange={(val) => handleCellChange(cell.id, val)}
              onRun={() => executeCell(cell.id)}
              onDelete={() => setCells(cells.filter(c => c.id !== cell.id))}
              onMoveUp={() => {
                if (index === 0) return;
                const newCells = [...cells];
                [newCells[index], newCells[index - 1]] = [newCells[index - 1], newCells[index]];
                setCells(newCells);
              }}
              onMoveDown={() => {
                if (index === cells.length - 1) return;
                const newCells = [...cells];
                [newCells[index], newCells[index + 1]] = [newCells[index + 1], newCells[index]];
                setCells(newCells);
              }}
            />
          ))}
          
          {/* Add Cell Controls */}
          <div className="flex items-center justify-center gap-4 py-8 opacity-50 hover:opacity-100 transition-opacity">
            <Button variant="outline" className="gap-2 bg-background border-dashed" onClick={() => addCell('code')}>
               <Code2 className="w-4 h-4" />
               Code
            </Button>
            <Button variant="outline" className="gap-2 bg-background border-dashed" onClick={() => addCell('markdown')}>
               <FileText className="w-4 h-4" />
               Text
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
