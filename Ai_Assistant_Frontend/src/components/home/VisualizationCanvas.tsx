import { useState } from 'react';
import { ChevronDown, ChevronRight, Database, FileSpreadsheet, Globe, X, Plus, BarChart3, PieChart, Activity, TrendingUp, Table } from 'lucide-react';
import { useAppStore, DataSource } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { AddDataSourceDropdown } from './AddDataSourceDropdown';

const visualizationTypes = [
  { type: 'line', label: 'Line Chart', icon: Activity },
  { type: 'bar', label: 'Bar Chart', icon: BarChart3 },
  { type: 'pie', label: 'Pie Chart', icon: PieChart },
  { type: 'kpi', label: 'KPI Card', icon: TrendingUp },
  { type: 'table', label: 'Data Table', icon: Table },
];

function SourceIcon({ type }: { type: DataSource['type'] }) {
  switch (type) {
    case 'csv':
    case 'excel':
      return <FileSpreadsheet className="w-4 h-4 text-success" />;
    case 'json':
      return <FileSpreadsheet className="w-4 h-4 text-warning" />;
    case 'database':
      return <Database className="w-4 h-4 text-info" />;
    case 'api':
      return <Globe className="w-4 h-4 text-primary" />;
    default:
      return null;
  }
}

export function VisualizationCanvas() {
  const { dataSources, removeDataSource } = useAppStore();
  const [isSourcesExpanded, setIsSourcesExpanded] = useState(false);
  const [tiles, setTiles] = useState<Array<{ id: string; type: string }>>([]);

  const addTile = (type: string) => {
    setTiles([...tiles, { id: crypto.randomUUID(), type }]);
  };

  const removeTile = (id: string) => {
    setTiles(tiles.filter((t) => t.id !== id));
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header with Connected Sources */}
      <div className="border-b border-border">
        <div className="flex items-center px-6 py-3">
          <button
            onClick={() => setIsSourcesExpanded(!isSourcesExpanded)}
            className="flex items-center gap-2 hover:bg-muted/50 rounded-lg px-2 py-1 -ml-2 transition-colors"
          >
            {isSourcesExpanded ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            )}
            <span className="text-sm font-medium text-foreground">Connected Sources</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
              {dataSources.length}
            </span>
          </button>
          <AddDataSourceDropdown>
            <button
              className="ml-2 p-1 rounded-md hover:bg-muted text-muted-foreground hover:text-primary transition-colors"
              title="Add data source"
            >
              <Plus className="w-4 h-4" />
            </button>
          </AddDataSourceDropdown>
        </div>

        <AnimatePresence>
          {isSourcesExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="px-6 pb-4 flex flex-wrap gap-2">
                {dataSources.map((source) => (
                  <div
                    key={source.id}
                    className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg text-sm"
                  >
                    <SourceIcon type={source.type} />
                    <span className="text-foreground">{source.name}</span>
                    <button
                      onClick={() => removeDataSource(source.id)}
                      className="p-0.5 hover:bg-destructive/20 rounded text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Canvas */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-min">
          {/* Existing Tiles */}
          <AnimatePresence mode="popLayout">
            {tiles.map((tile) => {
              const VizIcon = visualizationTypes.find((v) => v.type === tile.type)?.icon;
              return (
                <motion.div
                  key={tile.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="bg-card border border-border rounded-xl p-4 aspect-[4/3] flex flex-col"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      {VizIcon && (
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                          <VizIcon className="w-4 h-4 text-primary" />
                        </div>
                      )}
                      <span className="text-sm font-medium text-foreground">
                        {visualizationTypes.find((v) => v.type === tile.type)?.label}
                      </span>
                    </div>
                    <button
                      onClick={() => removeTile(tile.id)}
                      className="p-1 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="flex-1 flex items-center justify-center border-2 border-dashed border-border rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      Use AI to populate this visualization
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {/* Add Tile Button */}
          <div className="bg-card/50 border-2 border-dashed border-border rounded-xl aspect-[4/3] flex flex-col items-center justify-center hover:border-muted-foreground/50 hover:bg-card transition-all group">
            <div className="text-center">
              <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mx-auto mb-3 group-hover:bg-primary/10 transition-colors">
                <Plus className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-3">Add Visualization</p>
              <div className="flex flex-wrap gap-2 justify-center px-4">
                {visualizationTypes.slice(0, 3).map((viz) => (
                  <button
                    key={viz.type}
                    onClick={() => addTile(viz.type)}
                    className="text-xs px-2 py-1 rounded-md bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {viz.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
