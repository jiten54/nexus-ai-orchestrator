import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodeColors = {
  idle: '#666666',
  running: '#00E5FF',
  completed: '#00FF66',
  error: '#FF3B30'
};

const CustomNode = ({ data }) => {
  const status = data.status || 'idle';
  const borderColor = nodeColors[status];
  
  return (
    <div 
      className="px-4 py-3 bg-[#141414] rounded-lg border-2 min-w-[120px] text-center transition-all"
      style={{ borderColor, boxShadow: status === 'running' ? `0 0 20px ${borderColor}40` : 'none' }}
    >
      <div className="text-white text-sm font-medium">{data.label}</div>
      <div className="text-xs mt-1" style={{ color: borderColor }}>{status}</div>
    </div>
  );
};

const nodeTypes = {
  source: CustomNode,
  process: CustomNode,
  sink: CustomNode,
  default: CustomNode
};

export const WorkflowGraph = ({ nodes: initialNodes, edges: initialEdges }) => {
  const formattedNodes = useMemo(() => 
    (initialNodes || []).map(node => ({
      ...node,
      type: node.type || 'default',
      data: { ...node.data }
    })), [initialNodes]
  );

  const formattedEdges = useMemo(() => 
    (initialEdges || []).map(edge => ({
      ...edge,
      type: 'smoothstep',
      animated: edge.animated || false,
      style: { 
        stroke: '#00E5FF', 
        strokeWidth: 2,
        strokeDasharray: edge.animated ? '5,5' : 'none'
      }
    })), [initialEdges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(formattedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(formattedEdges);

  // Update nodes when props change
  useMemo(() => {
    setNodes(formattedNodes);
    setEdges(formattedEdges);
  }, [formattedNodes, formattedEdges, setNodes, setEdges]);

  return (
    <div className="h-full w-full" data-testid="workflow-graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#333" gap={20} />
        <Controls className="bg-[#141414] border-white/10 [&_button]:bg-[#1E1E1E] [&_button]:border-white/10 [&_button]:text-white [&_button:hover]:bg-[#2A2A2A]" />
        <MiniMap 
          nodeColor={(node) => nodeColors[node.data?.status] || '#666666'}
          maskColor="rgba(0,0,0,0.8)"
          className="bg-[#141414] border border-white/10"
        />
      </ReactFlow>
    </div>
  );
};
