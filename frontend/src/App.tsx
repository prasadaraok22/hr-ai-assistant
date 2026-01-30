import { useState } from 'react';
import { ChatContainer } from '@/components/ChatContainer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Building2, User } from 'lucide-react';

// Demo employees for testing
const demoEmployees = [
  { id: 'EMP001', name: 'John Smith', department: 'Engineering' },
  { id: 'EMP002', name: 'Sarah Johnson', department: 'Marketing' },
  { id: 'EMP003', name: 'Michael Brown', department: 'Finance' },
];

function App() {
  const [selectedEmployee, setSelectedEmployee] = useState<{ id: string; name: string } | null>(null);
  const [customId, setCustomId] = useState('');

  if (!selectedEmployee) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 p-3 rounded-full bg-primary w-fit">
              <Building2 className="h-8 w-8 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl">HR AI Assistant</CardTitle>
            <CardDescription>
              Select your employee profile to start chatting with the HR assistant
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Demo Employees:</p>
              {demoEmployees.map((emp) => (
                <Button
                  key={emp.id}
                  variant="outline"
                  className="w-full justify-start h-auto py-3"
                  onClick={() => setSelectedEmployee({ id: emp.id, name: emp.name })}
                >
                  <User className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium">{emp.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {emp.id} • {emp.department}
                    </div>
                  </div>
                </Button>
              ))}
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Or enter custom ID</span>
              </div>
            </div>

            <div className="flex gap-2">
              <Input
                placeholder="Employee ID (e.g., EMP004)"
                value={customId}
                onChange={(e) => setCustomId(e.target.value)}
              />
              <Button
                onClick={() => {
                  if (customId.trim()) {
                    setSelectedEmployee({ id: customId.trim(), name: 'Employee' });
                  }
                }}
                disabled={!customId.trim()}
              >
                Login
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">HR AI Assistant</h1>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedEmployee(null)}
          >
            Switch User
          </Button>
        </div>
        <ChatContainer
          employeeId={selectedEmployee.id}
          employeeName={selectedEmployee.name}
        />
      </div>
    </div>
  );
}

export default App;
