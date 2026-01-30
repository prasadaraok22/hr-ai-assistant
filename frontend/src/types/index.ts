export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}

export interface ChatRequest {
  employee_id: string;
  message: string;
  thread_id: string;
}

export interface ChatResponse {
  response: string;
  employee_id: string;
  thread_id: string;
  tool_calls: ToolCall[];
}

export interface Employee {
  id: string;
  name: string;
  department: string;
}
