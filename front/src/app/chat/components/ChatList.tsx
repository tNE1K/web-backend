import React, { useEffect, useState } from "react";
import { formatDistanceToNow as formatDistanceToNowFn } from "date-fns";
import { useAuth } from "@/app/component/authProvider";

interface ChatListProps {
  onSelectChat: (chatId: string) => void;
}

interface LastMessage {
  senderId: string;
  content: string;
  timestamp: string;
}

interface Chat {
  id: string;
  participants: {
    sender: string;
    receiver: string;
  };
  isGroupChat: boolean;
  lastMessage: LastMessage;
}

const ChatList: React.FC<ChatListProps> = ({ onSelectChat }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newChatUsername, setNewChatUsername] = useState(""); // State để lưu giá trị tìm kiếm
  const { user } = useAuth();

  useEffect(() => {
    if (!user?.id) return;

    const fetchChats = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://127.0.0.1:5000/chat/list", {
          method: "GET",
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch chats");
        }

        const result = await response.json();
        if (result.status === "success" && result.data.chats) {
          setChats(result.data.chats);
        }
      } catch (error) {
        console.error("Error fetching chats:", error);
        setError(error instanceof Error ? error.message : "Failed to load chats");
      } finally {
        setLoading(false);
      }
    };

    fetchChats();
  }, []);

  const handleSelectChat = (chatId: string) => {
    onSelectChat(chatId);
  };

  const handleCreateChat = async () => {
    if (!newChatUsername.trim()) return;

    try {
      const response = await fetch("http://127.0.0.1:5000/chat/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ receiver: newChatUsername }),
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to create chat");
      }

      const result = await response.json();
      if (result.status === "success" && result.data.chat) {
        setChats((prevChats) => [result.data.chat, ...prevChats]); // Cập nhật danh sách chat
        setNewChatUsername(""); // Reset ô nhập
      }
    } catch (error) {
      console.error("Error creating chat:", error);
    }
  };

  if (loading) {
    return (
      <div className="w-1/5 border-r border-gray-300 p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-1/3 border-r border-gray-300 p-4">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  function formatDistanceToNow(date: Date, options: { addSuffix: boolean }): React.ReactNode {
    return formatDistanceToNowFn(date, options);
  }

  return (
    <div className="w-1/5 border-r border-gray-300">
      <div className="overflow-y-auto max-h-[calc(100vh-8rem)]">
        {chats.length === 0 ? (
          <div className="p-4 text-gray-500 text-center">
            <p>Không có cuộc trò chuyện nào</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {chats.map((chat) => (
              <li
                key={chat.id}
                onClick={() => handleSelectChat(chat.id)}
                className="hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="p-4 space-y-2">
                  <div className="flex justify-between items-start">
                    <div className="font-medium">
                      {chat.isGroupChat ? "Group Chat" : chat.participants.receiver}
                    </div>
                    {chat.lastMessage?.timestamp && (
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(chat.lastMessage.timestamp), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                  {chat.lastMessage && (
                    <div className="flex justify-between items-center">
                      <p className="text-sm text-gray-600 truncate">
                        {chat.lastMessage.content || "No messages yet"}
                      </p>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Ô tìm kiếm tạo chat mới */}
      {/* <div className="p-4 border-t border-gray-300">
        <input
          type="text"
          value={newChatUsername}
          onChange={(e) => setNewChatUsername(e.target.value)}
          placeholder="Nhập tên người dùng để bắt đầu trò chuyện mới"
          className="w-full p-2 border border-gray-300 rounded"
        />
        <button
          onClick={handleCreateChat}
          className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition w-full"
        >
          Tạo cuộc trò chuyện
        </button>
      </div> */}
    </div>
  );
};

export default ChatList;
