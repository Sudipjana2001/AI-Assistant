/**
 * Databricks Service
 * Handles communication with backend Databricks endpoints
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1/databricks';

export interface Cluster {
  cluster_id: string;
  cluster_name: string;
  state: string;
  driver_type?: string;
  num_workers?: number;
}

export interface ExecutionResult {
  status: string;
  output?: string;
  error?: string;
}

export const databricksService = {
  /**
   * List all available clusters
   */
  listClusters: async (): Promise<Cluster[]> => {
    const response = await axios.get(`${API_BASE_URL}/clusters`);
    return response.data;
  },

  /**
   * Start a cluster
   */
  startCluster: async (clusterId: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/clusters/${clusterId}/start`);
  },

  /**
   * Stop (Terminate) a cluster
   */
  stopCluster: async (clusterId: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/clusters/${clusterId}/stop`);
  },

  /**
   * Execute code on a cluster
   */
  executeCode: async (clusterId: string, code: string, language: string = 'python'): Promise<ExecutionResult> => {
    const response = await axios.post(`${API_BASE_URL}/execute`, {
      cluster_id: clusterId,
      code,
      language
    });
    return response.data;
  },

  /**
   * Get WebSocket URL for execution stream
   */
  getStreamUrl: (sessionId: string): string => {
    return `ws://localhost:8000/api/v1/databricks/execute/stream/${sessionId}`;
  },

  /**
   * Restart the execution context (kernel)
   */
  restartContext: async (clusterId: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/context/destroy?cluster_id=${clusterId}`);
  }
};
