import { AppSidebar } from "@/components/AppSidebar";
import { useIsMobile } from "@/hooks/use-mobile";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const isMobile = useIsMobile();

  return (
    <div className={`min-h-screen w-full ${isMobile ? "flex flex-col" : "flex"}`}>
      <AppSidebar />
      <main className="flex-1 p-4 sm:p-6 overflow-auto">
        {children}
      </main>
    </div>
  );
}
