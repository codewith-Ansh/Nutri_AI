import { ChatContainer } from "@/components/ChatContainer";
import { Header } from "@/components/Header";

const Index = () => {
  const handleClearChat = () => {
    window.location.reload();
  };

  const handleShare = () => {
    // Future: implement share functionality
    console.log("Share clicked");
  };

  return (
    <div className="flex flex-col h-screen bg-background transition-colors duration-300">
      <Header onClearChat={handleClearChat} onShare={handleShare} />

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <ChatContainer />
      </main>
    </div>
  );
};

export default Index;