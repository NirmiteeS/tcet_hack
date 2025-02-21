import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BookOpen, User, Calendar, CheckCircle, ListChecks } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import EnhancedWorkflow from '@/components/EnhancedWorkflow';

const TaskList = ({ tasks }) => {
  return (
    <div className="w-1/3 bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">Task List</h2>
      <div className="space-y-6">
        {tasks.map((task, index) => (
          <Card key={index} className="shadow-md hover:shadow-lg transition-shadow duration-300 border">
            <CardHeader className="bg-gradient-to-r from-[#0d1a42] to-[#a8d2fa] text-white p-4 rounded-t-lg">
              <CardTitle className="text-lg font-semibold flex items-center">
                <ListChecks className="mr-2" size={20} />
                {task.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 text-gray-700">
              <div className="mb-3 flex items-center">
                <User className="text-gray-600 mr-2" size={18} />
                <span className="font-medium">Assigned to:</span>
                <span className="ml-1 text-gray-800">{task.assignee.join(', ')}</span>
              </div>
              <div className="mb-3 flex items-center">
                <Calendar className="text-gray-600 mr-2" size={18} />
                <span className="font-medium">Due Date:</span>
                <span className="ml-1 text-gray-800">{task.dueDate}</span>
              </div>
              <div className="mb-3 flex items-center">
                <CheckCircle className={`mr-2 ${task.status === "Completed" ? "text-green-500" : "text-yellow-500"}`} size={18} />
                <span className="font-medium">Status:</span>
                <span className="ml-1 text-gray-800">{task.status}</span>
              </div>
              <p className="text-sm text-gray-600 italic">{task.project}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default function WorkflowPage() {
  const [task, setTask] = useState('');
  const [showWorkflow, setShowWorkflow] = useState(false);
  const [workflow, setWorkflow] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleGenerateWorkflow = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/generate-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch workflow');
      }

      const data = await response.json();
      console.log(data.workflow);
      setWorkflow(data.workflow);
      setTasks(data.tasks);
      setShowWorkflow(true);
      setIsModalOpen(false);
    } catch (error) {
      console.error('Error generating workflow:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">Task Workflow Generator</h1>
      <div className='w-[70%] mx-auto text-center text-gray-600 mb-12'>
        Our tool helps you break down complex tasks into structured workflows, assigning responsibilities and setting deadlines for better productivity.
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogTrigger asChild>
          <div className="relative p-6 bg-white border-2 border-dashed border-blue-500 rounded-lg cursor-pointer transition-all duration-300 ease-in-out hover:bg-blue-50 mx-auto max-w-md">
            <h3 className="text-xl font-semibold text-blue-500 text-center">Create a Workflow</h3>
            <BookOpen className="absolute top-4 right-4 text-blue-500" size={24} />
          </div>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Generate a Workflow</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 p-4">
            <div>
              <label htmlFor="task" className="block text-sm font-medium text-gray-700 mb-1">
                Task Description
              </label>
              <Input
                id="task"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="e.g. Develop a new website, Organize an event"
                className="w-full bg-white"
              />
            </div>
            <Button onClick={handleGenerateWorkflow} className="w-full">
              Generate Workflow
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {showWorkflow && (
        <div className="flex gap-8 mt-8">
          <div className="w-2/3">
            <EnhancedWorkflow data={{ workflow, task }} />
          </div>
          <TaskList tasks={tasks} />
        </div>
      )}
    </div>
  );
}
