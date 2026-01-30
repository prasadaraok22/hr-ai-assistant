const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function sendChatMessage(
  employeeId: string,
  message: string,
  threadId: string
): Promise<{
  response: string;
  employee_id: string;
  thread_id: string;
  tool_calls: Array<{ name: string; args: Record<string, unknown> }>;
}> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      employee_id: employeeId,
      message: message,
      thread_id: threadId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('API is not healthy');
  }
  return response.json();
}

export async function getWorkflowGraph(): Promise<{ graph: string }> {
  const response = await fetch(`${API_BASE_URL}/api/graph`);
  if (!response.ok) {
    throw new Error('Failed to fetch workflow graph');
  }
  return response.json();
}
