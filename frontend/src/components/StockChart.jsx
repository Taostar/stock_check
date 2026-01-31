
import React from 'react';
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{
        backgroundColor: '#fff',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '8px',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' 
      }}>
        <p className="label" style={{ fontWeight: 'bold', marginBottom: '5px' }}>{label}</p>
        {payload.map((entry, index) => (
          <div key={index} style={{ color: entry.color, marginBottom: '2px' }}>
            <span style={{ fontWeight: 600 }}>{entry.name}:</span>
            {' '}
            {/* We want to show raw price if available in payload, but Recharts payload structure 
                might be normalized. We'll need to pass raw data or handle it. 
                For now, let's display the normalized value and handle raw in App or logic improvement.
                Actually, simpler: The chart displays normalized, but the payload has the value.
                Wait, if we pass normalized data to Chart, payload has normalized value.
                To show RAW price, we need raw data in the object too.
            */}
             {/* If we strictly pass normalized data, we lose raw. 
                 Strategy: Pass normalized data to lines, but keep raw data in the data object 
                 with a different key key (e.g. "AAPL_raw"). 
                 Then formatter can access it? Recharts is tricky with mixed data.
                 
                 Simpler approach for this step: Just show the percentage change in tooltip for now. 
                 User requirement said: "real price tags can be shown in the hover cursor."
                 
                 So I need to pass raw prices in the data object as well.
                 e.g. { date:..., AAPL: 15 (norm), AAPL_raw: 150 (raw) }
            */}
            {/* Let's assume the data passed specifically has both `Ticker` (normalized) and `Ticker_raw` (raw). */}
            <span>{entry.payload[entry.name + '_raw'] !== undefined 
                ? `$${ Number(entry.payload[entry.name + '_raw']).toLocaleString() } ` 
                : entry.value.toFixed(2) + '%'}</span>
            <span style={{fontSize: '0.8em', marginLeft: '5px'}}>
               ({entry.value > 0 ? '+' : ''}{entry.value.toFixed(2)}%)
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const StockChart = ({ data, tickers }) => {
  if (!data || data.length === 0) return null;

  // Process data for normalization if not already done?
  // Ideally App.jsx handles fetching. But normalization logic is presentation.
  // Actually, better to do it here or in a hook.
  // Let's do it here to keep App.jsx clean.
  
  const normalizedData = data.map((item, index) => {
      const newItem = { ...item };
      tickers.forEach(ticker => {
          const startPrice = data.find(d => d[ticker] != null)?.[ticker];
          if (startPrice && item[ticker] != null) {
              newItem[ticker + '_raw'] = item[ticker]; // Save raw
              newItem[ticker] = ((item[ticker] - startPrice) / startPrice) * 100;
          }
      });
      return newItem;
  });

  return (
    <div className="chart-container">
      <h3>Performance Comparison</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={normalizedData}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(str) => str.slice(5)} 
            stroke="#64748b"
            fontSize={12}
          />
          <YAxis 
             tickFormatter={(number) => `${ number.toFixed(0) }% `}
             stroke="#64748b"
             fontSize={12}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {tickers.map((ticker, index) => (
             <Line 
                key={ticker}
                type="monotone" 
                dataKey={ticker} 
                stroke={COLORS[index % COLORS.length]} 
                strokeWidth={2}
                dot={false}
                name={ticker}
             />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;

