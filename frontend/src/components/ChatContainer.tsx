import { useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Bot, Trash2, Calendar, DollarSign, FileText, HelpCircle } from 'lucide-react';

interface ChatContainerProps {
  employeeId: string;
  employeeName: string;
}

const quickActions = [
  { label: 'Check Leave Balance', message: 'What is my current leave balance?', icon: Calendar },
  { label: 'View Pay Stubs', message: 'Show me my recent pay stubs', icon: DollarSign },
  { label: 'Healthcare Benefits', message: 'What healthcare benefits are available?', icon: FileText },
  { label: 'Retirement Plan', message: 'Tell me about the 401k retirement plan', icon: HelpCircle },
];

export function ChatContainer({ employeeId, employeeName }: ChatContainerProps) {
  const { messages, isLoading, sendMessage, clearChat } = useChat(employeeId);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <Card className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-primary">
            <Bot className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <CardTitle className="text-lg">HR AI Assistant</CardTitle>
            <p className="text-sm text-muted-foreground">
              Logged in as: {employeeName} ({employeeId})
            </p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={clearChat}>
          <Trash2 className="h-4 w-4 mr-2" />
          Clear Chat
        </Button>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="p-4 border-b bg-muted/30">
            <p className="text-sm text-muted-foreground mb-3">Quick Actions:</p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => sendMessage(action.message)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  <action.icon className="h-3 w-3 mr-1" />
                  {action.label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <ScrollArea className="flex-1">
          <div ref={scrollRef} className="p-4 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {isLoading && (
              <div className="flex gap-3 p-4 rounded-lg bg-muted/50">
                <div className="p-2 rounded-full bg-primary h-8 w-8 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm text-muted-foreground">Thinking...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </CardContent>
    </Card>
  );
}
