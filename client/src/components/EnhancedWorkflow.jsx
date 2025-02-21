import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ListChecks } from 'lucide-react';

const WorkflowStep = ({ step, index }) => {
  return (
    <div className="flex items-start mb-8">
      <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#0d1a42] flex items-center justify-center text-white font-bold text-lg relative z-50 mt-5">
        {index + 1}
      </div>
      <div className="ml-4 flex-grow">
        <Card className="w-full shadow-lg hover:shadow-xl transition-shadow duration-300">
          <CardHeader className="bg-gradient-to-r from-[#0d1a42] to-[#a8d2fa] text-white">
            <CardTitle className="text-xl font-bold flex items-center">
              <ListChecks className="mr-2" size={20} />
              {step?.title || "Untitled Step"}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <p className="text-gray-600 mb-3">{step?.description || "No description available"}</p>

            {step?.expectedOutcomes && step.expectedOutcomes.length > 0 && (
              <>
                <strong className="text-gray-800">Expected Outcomes:</strong>
                <ul className="list-disc list-inside text-gray-600 mb-3">
                  {step.expectedOutcomes.map((outcome, i) => (
                    <li key={i}>{outcome}</li>
                  ))}
                </ul>
              </>
            )}

            {step?.keySteps && step.keySteps.length > 0 ? (
              <>
                <strong className="text-gray-800">Key Steps:</strong>
                <ul className="list-disc list-inside text-gray-600">
                  {step.keySteps.map((keyStep, i) => (
                    <li key={i} className="mb-1">
                      <span className="font-medium">{keyStep?.task || "Unnamed Task"}</span> - Assigned to{" "}
                      {keyStep?.assignee?.join(", ") || "Unknown"} (Due: {keyStep?.dueDate || "No due date"})
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="text-gray-500 italic">No key steps available.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const EnhancedWorkflow = ({ data }) => {
  const workflow = data?.workflow || []; // Ensure workflow is an array

  return (
    <div className="max-w-3xl mx-auto mt-12 px-4">
      <h2 className="text-3xl font-bold text-center mb-10 text-gray-800">
        Project Workflow
      </h2>
      <div className="relative">
        <div className="absolute left-6 top-0 h-full w-0.5 bg-blue-300" aria-hidden="true"></div>
        {workflow.length > 0 ? (
          workflow.map((step, index) => (
            <WorkflowStep key={index} step={step} index={index} />
          ))
        ) : (
          <p className="text-gray-500 italic text-center">No workflow steps available.</p>
        )}
      </div>
    </div>
  );
};

export default EnhancedWorkflow;
