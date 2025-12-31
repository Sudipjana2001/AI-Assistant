import { useAppStore } from '@/store/appStore';
import { UploadZone } from '@/components/home/UploadZone';
import { VisualizationCanvas } from '@/components/home/VisualizationCanvas';

const Home = () => {
  const { isConnected } = useAppStore();

  return (
    <div className="h-screen overflow-hidden">
      {isConnected ? <VisualizationCanvas /> : <UploadZone />}
    </div>
  );
};

export default Home;
