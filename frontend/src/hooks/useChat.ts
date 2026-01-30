import { useState, useCallback, useRef, useEffect } from 'react';
import { Message } from '@/types';
import { sendChatMessage } from '@/lib/api';

export function useChat(employeeId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadIdRef = useRef<string>(`thread-${Date.now()}`);

  // Add welcome message on mount
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm your HR AI Assistant. I can help you with:

🏖️ **Leave Management**
   • Check your leave balance
   • Submit leave requests

💰 **Payroll Information**
   • View your recent pay stubs
   • Understand your deductions

📋 **HR Policies**
   • Leave policies and procedures
   • Healthcare benefits
   • Retirement benefits

How can I assist you today?`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(
        employeeId,
        content,
        threadIdRef.current
      );

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        toolCalls: response.tool_calls,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);

      const errorAssistantMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${errorMessage}. Please try again or contact HR directly.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [employeeId]);

  const clearChat = useCallback(() => {
    threadIdRef.current = `thread-${Date.now()}`;
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `Chat cleared. How can I help you today?`,
      timestamp: new Date(),
    }]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
}
