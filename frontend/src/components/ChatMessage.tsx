import { Message } from '@/types';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg',
        isAssistant ? 'bg-muted/50' : 'bg-background'
      )}
    >
      <Avatar className={cn('h-8 w-8', isAssistant ? 'bg-primary' : 'bg-secondary')}>
        <AvatarFallback className={isAssistant ? 'bg-primary text-primary-foreground' : 'bg-secondary'}>
          {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm">
            {isAssistant ? 'HR Assistant' : 'You'}
          </span>
          <span className="text-xs text-muted-foreground">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div className="message-content text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 pt-2 border-t border-border">
            <span className="text-xs text-muted-foreground">
              🔧 Actions: {message.toolCalls.map(tc => tc.name).join(', ')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
