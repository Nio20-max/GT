import MainMenu from "@/components/MainMenu";
import TopBar from "@/components/TopBar";
import BottomBar from "@/components/BottomBar";

export default function GameLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* Left sidebar */}
      <MainMenu />

      {/* Main area */}
      <div className="flex flex-1 flex-col">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
        <BottomBar />
      </div>
    </div>
  );
}
