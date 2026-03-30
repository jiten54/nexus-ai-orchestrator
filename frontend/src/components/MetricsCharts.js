import { useMemo } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export const MetricsCharts = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      // Generate some placeholder data
      return Array.from({ length: 20 }, (_, i) => ({
        time: new Date(Date.now() - (20 - i) * 2000).toLocaleTimeString(),
        cpu: 40 + Math.random() * 20,
        memory: 50 + Math.random() * 15,
        latency: 100 + Math.random() * 100,
        throughput: 1200 + Math.random() * 500
      }));
    }
    return data;
  }, [data]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#141414] border border-white/10 rounded-lg p-3 shadow-xl">
          <p className="text-xs text-[#666666] mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-xs" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}
              {entry.name === 'CPU' || entry.name === 'Memory' ? '%' : ''}
              {entry.name === 'Latency' ? 'ms' : ''}
              {entry.name === 'Throughput' ? '/s' : ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-2 gap-4 h-full">
      {/* CPU & Memory Chart */}
      <div className="h-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00E5FF" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7000FF" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#7000FF" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="time" 
              stroke="#666" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickLine={{ stroke: '#666' }}
            />
            <YAxis 
              stroke="#666" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickLine={{ stroke: '#666' }}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: '10px' }}
              formatter={(value) => <span style={{ color: '#A0A0A0' }}>{value}</span>}
            />
            <Area 
              type="monotone" 
              dataKey="cpu" 
              name="CPU"
              stroke="#00E5FF" 
              fill="url(#cpuGradient)" 
              strokeWidth={2}
            />
            <Area 
              type="monotone" 
              dataKey="memory" 
              name="Memory"
              stroke="#7000FF" 
              fill="url(#memoryGradient)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Latency & Throughput Chart */}
      <div className="h-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="time" 
              stroke="#666" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickLine={{ stroke: '#666' }}
            />
            <YAxis 
              yAxisId="left"
              stroke="#666" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickLine={{ stroke: '#666' }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#666" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickLine={{ stroke: '#666' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: '10px' }}
              formatter={(value) => <span style={{ color: '#A0A0A0' }}>{value}</span>}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="latency" 
              name="Latency"
              stroke="#FFB020" 
              strokeWidth={2}
              dot={false}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="throughput" 
              name="Throughput"
              stroke="#00FF66" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
