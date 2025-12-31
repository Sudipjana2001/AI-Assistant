import { Outlet } from 'react-router-dom';
import { AppSidebar } from './AppSidebar';
import { AIAssistant } from './AIAssistant';

export function AppLayout() {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
      <AIAssistant />
    </div>
  );
}
