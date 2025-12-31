import { X, Code, BarChart3 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

const sampleData = [
  { name: 'Jan', value: 400, value2: 240 },
  { name: 'Feb', value: 300, value2: 139 },
  { name: 'Mar', value: 600, value2: 380 },
  { name: 'Apr', value: 800, value2: 400 },
  { name: 'May', value: 500, value2: 480 },
  { name: 'Jun', value: 900, value2: 380 },
  { name: 'Jul', value: 700, value2: 430 },
];

export function ArtifactModal() {
  const { activeArtifact, activeArtifactCode, setActiveArtifact } = useAppStore();
  const [showCode, setShowCode] = useState(false);

  if (!activeArtifact) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-8"
        onClick={() => setActiveArtifact(null)}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-card rounded-2xl w-full max-w-4xl border border-border shadow-elevated overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">
                  {activeArtifact.title || 'Visualization'}
                </h3>
                <p className="text-xs text-muted-foreground">
                  Generated from code execution
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={showCode ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setShowCode(!showCode)}
                className="gap-2"
              >
                <Code className="w-4 h-4" />
                {showCode ? 'Hide Code' : 'View Code'}
              </Button>
              <button
                onClick={() => setActiveArtifact(null)}
                className="p-2 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className={cn('grid transition-all', showCode ? 'grid-cols-2' : 'grid-cols-1')}>
            {/* Visualization */}
            <div className="p-6 min-h-[400px]">
              <div className="h-full w-full bg-muted/30 rounded-xl p-4">
                <ResponsiveContainer width="100%" height={350}>
                  {activeArtifact.type === 'chart' ? (
                    <LineChart data={sampleData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="name" 
                        stroke="hsl(var(--muted-foreground))" 
                        fontSize={12}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))" 
                        fontSize={12}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--popover))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--foreground))',
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke="hsl(var(--primary))" 
                        strokeWidth={2}
                        dot={{ fill: 'hsl(var(--primary))', strokeWidth: 0 }}
                        activeDot={{ r: 6, fill: 'hsl(var(--primary))' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="value2" 
                        stroke="hsl(var(--info))" 
                        strokeWidth={2}
                        dot={{ fill: 'hsl(var(--info))', strokeWidth: 0 }}
                        activeDot={{ r: 6, fill: 'hsl(var(--info))' }}
                      />
                    </LineChart>
                  ) : (
                    <BarChart data={sampleData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis 
                        dataKey="name" 
                        stroke="hsl(var(--muted-foreground))" 
                        fontSize={12}
                      />
                      <YAxis 
                        stroke="hsl(var(--muted-foreground))" 
                        fontSize={12}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--popover))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--foreground))',
                        }}
                      />
                      <Bar 
                        dataKey="value" 
                        fill="hsl(var(--primary))" 
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>

            {/* Code Panel */}
            <AnimatePresence>
              {showCode && activeArtifactCode && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="border-l border-border bg-editor-bg overflow-hidden"
                >
                  <div className="p-4 h-full overflow-auto">
                    <pre className="text-xs font-mono text-foreground whitespace-pre-wrap">
                      {activeArtifactCode}
                    </pre>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
