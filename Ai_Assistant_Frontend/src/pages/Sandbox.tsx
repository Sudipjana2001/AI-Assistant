import { QueryWorkflow } from '@/components/sandbox/QueryWorkflow';
import { CodeSandbox } from '@/components/sandbox/CodeSandbox';
import { ArtifactModal } from '@/components/sandbox/ArtifactModal';

const Sandbox = () => {
  return (
    <div className="h-screen flex overflow-hidden">
      {/* Query Workflow Panel - width managed internally */}
      <QueryWorkflow />
      
      {/* Code Sandbox */}
      <div className="flex-1 min-w-0">
        <CodeSandbox />
      </div>

      {/* Artifact Modal */}
      <ArtifactModal />
    </div>
  );
};

export default Sandbox;
