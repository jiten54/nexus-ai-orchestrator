import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  Cpu, Network, Activity, AlertTriangle, Zap, BarChart3, 
  Terminal, Brain, Play, Square, Plus, LogOut, Settings,
  TrendingUp, TrendingDown, Clock, Server, Database, Workflow
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { WorkflowGraph } from '../components/WorkflowGraph';
import { MetricsCharts } from '../components/MetricsCharts';
import { motion, AnimatePresence } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const WS_URL = process.env.REACT_APP_BACKEND_URL?.replace('https://', 'wss://').replace('http://', 'ws://');

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [metrics, setMetrics] = useState({ cpu: 0, memory: 0, latency: 0, throughput: 0, error_rate: 0, active_workers: 0, queue_depth: 0 });
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [healingActions, setHealingActions] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isAiActive, setIsAiActive] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [newWorkflowType, setNewWorkflowType] = useState('etl');
  
  const wsRef = useRef(null);
  const logsEndRef = useRef(null);

  // Fetch initial data
  const fetchData = useCallback(async () => {
    try {
      const [workflowsRes, metricsRes, logsRes, alertsRes, predictionsRes, healingRes] = await Promise.all([
        axios.get(`${API}/workflows`, { withCredentials: true }),
        axios.get(`${API}/metrics/current`, { withCredentials: true }),
        axios.get(`${API}/logs`, { withCredentials: true }),
        axios.get(`${API}/alerts`, { withCredentials: true }),
        axios.get(`${API}/predictions`, { withCredentials: true }),
        axios.get(`${API}/healing-actions`, { withCredentials: true })
      ]);
      
      setWorkflows(workflowsRes.data);
      setMetrics(metricsRes.data);
      setLogs(logsRes.data.slice(0, 100));
      setAlerts(alertsRes.data.slice(0, 20));
      setPredictions(predictionsRes.data.slice(0, 5));
      setHealingActions(healingRes.data.slice(0, 20));
      
      if (workflowsRes.data.length > 0 && !selectedWorkflow) {
        setSelectedWorkflow(workflowsRes.data[0]);
      }
    } catch (e) {
      console.error('Error fetching data:', e);
    }
  }, [selectedWorkflow]);

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      wsRef.current = new WebSocket(`${WS_URL}/ws`);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
      };
      
      wsRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
          case 'metrics':
            setMetrics(message.data);
            setMetricsHistory(prev => [...prev.slice(-59), { ...message.data, time: new Date().toLocaleTimeString() }]);
            break;
          case 'log':
            setLogs(prev => [message.data, ...prev.slice(0, 99)]);
            break;
          case 'alert':
            setAlerts(prev => [message.data, ...prev.slice(0, 19)]);
            break;
          case 'prediction':
            setPredictions(prev => [message.data, ...prev.slice(0, 4)]);
            break;
          case 'healing_action':
            setHealingActions(prev => [message.data, ...prev.slice(0, 19)]);
            break;
          case 'workflow_update':
            setWorkflows(prev => prev.map(w => w.id === message.data.id ? { ...w, ...message.data } : w));
            if (selectedWorkflow?.id === message.data.id) {
              setSelectedWorkflow(prev => ({ ...prev, ...message.data }));
            }
            break;
          default:
            break;
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        setTimeout(connectWebSocket, 3000);
      };
    };
    
    connectWebSocket();
    fetchData();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchData]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleCreateWorkflow = async () => {
    try {
      const { data } = await axios.post(`${API}/workflows`, {
        name: newWorkflowName,
        workflow_type: newWorkflowType
      }, { withCredentials: true });
      
      setWorkflows(prev => [...prev, data]);
      setSelectedWorkflow(data);
      setShowCreateDialog(false);
      setNewWorkflowName('');
    } catch (e) {
      console.error('Error creating workflow:', e);
    }
  };

  const handleStartWorkflow = async (workflowId) => {
    try {
      await axios.post(`${API}/workflows/${workflowId}/start`, {}, { withCredentials: true });
    } catch (e) {
      console.error('Error starting workflow:', e);
    }
  };

  const handleStopWorkflow = async (workflowId) => {
    try {
      await axios.post(`${API}/workflows/${workflowId}/stop`, {}, { withCredentials: true });
    } catch (e) {
      console.error('Error stopping workflow:', e);
    }
  };

  const handleAnalyzeLogs = async () => {
    try {
      setIsAiActive(true);
      const { data } = await axios.post(`${API}/ai/analyze-logs`, {}, { withCredentials: true });
      setAiAnalysis(data);
    } catch (e) {
      console.error('Error analyzing logs:', e);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-[#00E5FF]';
      case 'completed': return 'text-[#00FF66]';
      case 'error': return 'text-[#FF3B30]';
      case 'idle': return 'text-[#666666]';
      default: return 'text-[#A0A0A0]';
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'text-[#FF3B30]';
      case 'WARNING': return 'text-[#FFB020]';
      case 'INFO': return 'text-[#00E5FF]';
      default: return 'text-[#A0A0A0]';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-[#FF3B30]/20 text-[#FF3B30] border-[#FF3B30]/30';
      case 'warning': return 'bg-[#FFB020]/20 text-[#FFB020] border-[#FFB020]/30';
      default: return 'bg-[#007AFF]/20 text-[#007AFF] border-[#007AFF]/30';
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white" data-testid="dashboard">
      {/* Header */}
      <header className="h-14 border-b border-white/10 bg-[#141414]/80 backdrop-blur-xl fixed top-0 left-0 right-0 z-50">
        <div className="h-full px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#00E5FF]/10 rounded-lg flex items-center justify-center border border-[#00E5FF]/30">
              <Cpu className="w-4 h-4 text-[#00E5FF]" />
            </div>
            <span className="font-bold text-lg tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>NEXUS_AI</span>
            <Badge variant="outline" className="border-[#00FF66]/30 text-[#00FF66] text-xs">ONLINE</Badge>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-[#A0A0A0]">
              <Server className="w-4 h-4" />
              <span>{user?.name || 'Operator'}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-[#A0A0A0] hover:text-white" data-testid="logout-button">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-14 min-h-screen">
        <div className="grid grid-cols-12 gap-4 p-4 h-[calc(100vh-56px)]">
          
          {/* Left Sidebar - Workflows */}
          <div className="col-span-2 space-y-4">
            <Card className="bg-[#141414] border-white/10 h-full">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">Workflows</CardTitle>
                  <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                    <DialogTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-[#00E5FF]" data-testid="create-workflow-button">
                        <Plus className="w-4 h-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-[#141414] border-white/10">
                      <DialogHeader>
                        <DialogTitle className="text-white">Create Workflow</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4 mt-4">
                        <div className="space-y-2">
                          <Label className="text-[#A0A0A0]">Name</Label>
                          <Input
                            value={newWorkflowName}
                            onChange={(e) => setNewWorkflowName(e.target.value)}
                            className="bg-[#0A0A0A] border-white/10 text-white"
                            placeholder="My Workflow"
                            data-testid="workflow-name-input"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-[#A0A0A0]">Type</Label>
                          <Select value={newWorkflowType} onValueChange={setNewWorkflowType}>
                            <SelectTrigger className="bg-[#0A0A0A] border-white/10 text-white" data-testid="workflow-type-select">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-[#141414] border-white/10">
                              <SelectItem value="etl">ETL Pipeline</SelectItem>
                              <SelectItem value="microservice">Microservice</SelectItem>
                              <SelectItem value="batch">Batch Processing</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Button onClick={handleCreateWorkflow} className="w-full bg-[#00E5FF] text-black font-semibold" data-testid="create-workflow-submit">
                          Create
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent className="p-2">
                <ScrollArea className="h-[calc(100vh-200px)]">
                  <div className="space-y-1">
                    {workflows.map((workflow) => (
                      <motion.div
                        key={workflow.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`p-2 rounded-lg cursor-pointer transition-all ${
                          selectedWorkflow?.id === workflow.id 
                            ? 'bg-[#00E5FF]/10 border border-[#00E5FF]/30' 
                            : 'hover:bg-white/5 border border-transparent'
                        }`}
                        onClick={() => setSelectedWorkflow(workflow)}
                        data-testid={`workflow-item-${workflow.id}`}
                      >
                        <div className="flex items-center gap-2">
                          <Workflow className="w-4 h-4 text-[#A0A0A0]" />
                          <span className="text-sm truncate">{workflow.name}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs ${getStatusColor(workflow.status)}`}>{workflow.status}</span>
                          <span className="text-xs text-[#666666]">{workflow.workflow_type}</span>
                        </div>
                      </motion.div>
                    ))}
                    {workflows.length === 0 && (
                      <p className="text-sm text-[#666666] text-center py-4">No workflows yet</p>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Center - Workflow Graph & Metrics */}
          <div className="col-span-7 space-y-4">
            {/* Workflow Graph */}
            <Card className="bg-[#141414] border-white/10 h-[45%]">
              <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                  Workflow Execution Graph
                </CardTitle>
                {selectedWorkflow && (
                  <div className="flex items-center gap-2">
                    <Badge className={getSeverityColor(selectedWorkflow.status === 'running' ? 'warning' : 'info')}>
                      {selectedWorkflow.status}
                    </Badge>
                    {selectedWorkflow.status !== 'running' ? (
                      <Button 
                        size="sm" 
                        className="bg-[#00FF66]/10 text-[#00FF66] hover:bg-[#00FF66]/20 h-7"
                        onClick={() => handleStartWorkflow(selectedWorkflow.id)}
                        data-testid="start-workflow-button"
                      >
                        <Play className="w-3 h-3 mr-1" /> Start
                      </Button>
                    ) : (
                      <Button 
                        size="sm" 
                        className="bg-[#FF3B30]/10 text-[#FF3B30] hover:bg-[#FF3B30]/20 h-7"
                        onClick={() => handleStopWorkflow(selectedWorkflow.id)}
                        data-testid="stop-workflow-button"
                      >
                        <Square className="w-3 h-3 mr-1" /> Stop
                      </Button>
                    )}
                  </div>
                )}
              </CardHeader>
              <CardContent className="p-0 h-[calc(100%-60px)]">
                {selectedWorkflow ? (
                  <WorkflowGraph nodes={selectedWorkflow.nodes} edges={selectedWorkflow.edges} />
                ) : (
                  <div className="h-full flex items-center justify-center text-[#666666]">
                    Select or create a workflow
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Metrics Dashboard */}
            <Card className="bg-[#141414] border-white/10 h-[53%]">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                  System Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[calc(100%-60px)]">
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <MetricCard icon={<Activity className="w-4 h-4" />} label="CPU" value={`${metrics.cpu?.toFixed(1)}%`} trend={metrics.cpu > 75 ? 'up' : 'stable'} />
                  <MetricCard icon={<Database className="w-4 h-4" />} label="Memory" value={`${metrics.memory?.toFixed(1)}%`} trend={metrics.memory > 80 ? 'up' : 'stable'} />
                  <MetricCard icon={<Clock className="w-4 h-4" />} label="Latency" value={`${metrics.latency?.toFixed(0)}ms`} trend={metrics.latency > 500 ? 'up' : 'stable'} />
                  <MetricCard icon={<BarChart3 className="w-4 h-4" />} label="Throughput" value={`${metrics.throughput?.toFixed(0)}/s`} trend="stable" />
                </div>
                <MetricsCharts data={metricsHistory} />
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar - AI Brain & Alerts */}
          <div className="col-span-3 space-y-4">
            {/* AI Brain Panel */}
            <Card className="bg-[#141414] border-white/10">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isAiActive ? 'bg-[#00E5FF] animate-pulse' : 'bg-[#666666]'}`} />
                    <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                      AI Brain
                    </CardTitle>
                  </div>
                  <Button size="sm" variant="ghost" onClick={handleAnalyzeLogs} className="text-[#00E5FF] h-6 text-xs" data-testid="analyze-logs-button">
                    <Brain className="w-3 h-3 mr-1" /> Analyze
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {aiAnalysis ? (
                  <div className="space-y-3 text-sm">
                    <p className="text-[#A0A0A0]">{aiAnalysis.summary}</p>
                    {aiAnalysis.anomalies?.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-xs text-[#666666] uppercase tracking-wider">Anomalies</span>
                        {aiAnalysis.anomalies.slice(0, 3).map((a, i) => (
                          <div key={i} className={`p-2 rounded border ${getSeverityColor(a.severity)}`}>
                            {a.description}
                          </div>
                        ))}
                      </div>
                    )}
                    {aiAnalysis.prediction && (
                      <div className="p-2 bg-[#7000FF]/10 border border-[#7000FF]/30 rounded">
                        <span className="text-xs text-[#7000FF]">Failure Risk: {(aiAnalysis.prediction.failure_probability * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-[#666666]">Click Analyze to get AI insights</p>
                )}
              </CardContent>
            </Card>

            {/* Predictions */}
            <Card className="bg-[#141414] border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                  Predictions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-24">
                  <div className="space-y-2">
                    <AnimatePresence>
                      {predictions.map((pred, i) => (
                        <motion.div
                          key={pred.id || i}
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0 }}
                          className="flex items-center justify-between text-xs p-2 bg-[#1E1E1E] rounded"
                        >
                          <span className="text-[#A0A0A0]">Failure Risk</span>
                          <span className={pred.probability > 0.5 ? 'text-[#FF3B30]' : 'text-[#00FF66]'}>
                            {(pred.probability * 100).toFixed(0)}%
                          </span>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Alerts */}
            <Card className="bg-[#141414] border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                  Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-32">
                  <div className="space-y-2">
                    <AnimatePresence>
                      {alerts.map((alert, i) => (
                        <motion.div
                          key={alert.id || i}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0 }}
                          className={`p-2 rounded border text-xs ${getSeverityColor(alert.severity)}`}
                        >
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                            <span className="line-clamp-2">{alert.message}</span>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Auto-Healing Actions */}
            <Card className="bg-[#141414] border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-[#A0A0A0] uppercase tracking-[0.2em]">
                  Auto-Healing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-24">
                  <div className="space-y-2">
                    <AnimatePresence>
                      {healingActions.map((action, i) => (
                        <motion.div
                          key={action.id || i}
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0 }}
                          className="flex items-center gap-2 text-xs p-2 bg-[#00FF66]/5 border border-[#00FF66]/20 rounded"
                        >
                          <Zap className="w-3 h-3 text-[#00FF66]" />
                          <span className="text-[#A0A0A0]">{action.type}: {action.result}</span>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Bottom Terminal Panel */}
        <div className="fixed bottom-0 left-0 right-0 h-48 bg-black border-t border-white/10">
          <div className="flex items-center justify-between px-4 py-2 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#00E5FF]" />
              <span className="text-xs uppercase tracking-[0.2em] text-[#A0A0A0]">Event Stream</span>
            </div>
            <span className="text-xs text-[#666666]">{logs.length} events</span>
          </div>
          <ScrollArea className="h-[calc(100%-40px)] p-2 font-mono text-xs">
            <div className="space-y-1">
              {logs.map((log, i) => (
                <div key={log.id || i} className="flex gap-2">
                  <span className="text-[#666666] w-20 flex-shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`w-16 flex-shrink-0 ${getLogLevelColor(log.level)}`}>
                    [{log.level}]
                  </span>
                  <span className="text-[#00E5FF] w-24 flex-shrink-0 truncate">
                    [{log.component}]
                  </span>
                  <span className="text-[#A0A0A0]">{log.message}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </ScrollArea>
        </div>
      </main>
    </div>
  );
};

const MetricCard = ({ icon, label, value, trend }) => (
  <div className="p-3 bg-[#1E1E1E] rounded-lg border border-white/5">
    <div className="flex items-center justify-between mb-1">
      <span className="text-[#666666]">{icon}</span>
      {trend === 'up' && <TrendingUp className="w-3 h-3 text-[#FF3B30]" />}
      {trend === 'down' && <TrendingDown className="w-3 h-3 text-[#00FF66]" />}
    </div>
    <div className="text-lg font-bold text-white" style={{ fontFamily: 'JetBrains Mono, monospace' }}>{value}</div>
    <div className="text-xs text-[#666666] uppercase tracking-wider">{label}</div>
  </div>
);

export default Dashboard;
