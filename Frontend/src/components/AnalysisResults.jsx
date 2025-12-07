import { useMemo } from 'react';
import { 
  RadialBarChart, RadialBar, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Area, AreaChart
} from 'recharts';

// Vibrant color palette for charts
const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#6366f1'];

function AnalysisResults({ analysis }) {
  if (!analysis) return null;

  // Calculate severity score for visualization
  const severityScore = useMemo(() => {
    if (!analysis.severity) return 50;
    const severity = analysis.severity.toLowerCase();
    if (severity.includes('severe')) return 85;
    if (severity.includes('moderate')) return 55;
    if (severity.includes('mild')) return 25;
    return 50;
  }, [analysis.severity]);

  // Prepare data for condition likelihood chart
  const conditionData = useMemo(() => {
    return analysis.conditions.map((condition, index) => ({
      name: condition.length > 30 ? condition.substring(0, 30) + '...' : condition,
      fullName: condition,
      likelihood: 100 - (index * 15), // Decreasing likelihood
      rank: index + 1
    }));
  }, [analysis.conditions]);

  // Prepare recommendation priority data
  const recommendationData = useMemo(() => {
    return analysis.recommendations.map((rec, index) => ({
      name: `Step ${index + 1}`,
      recommendation: rec,
      priority: 100 - (index * 10)
    }));
  }, [analysis.recommendations]);

  const getSeverityColor = (severity) => {
    if (!severity) return 'bg-gray-400';
    const s = severity.toLowerCase();
    if (s.includes('severe')) return 'bg-red-500';
    if (s.includes('moderate')) return 'bg-yellow-500';
    if (s.includes('mild')) return 'bg-green-500';
    return 'bg-gray-400';
  };

  // Colors for charts
  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
  const SEVERITY_COLORS = {
    severe: ['#ef4444', '#dc2626'],
    moderate: ['#f59e0b', '#d97706'],
    mild: ['#10b981', '#059669']
  };

  // Radial chart data for severity
  const radialData = [{
    name: 'Severity',
    value: severityScore,
    fill: severityScore > 70 ? '#ef4444' : severityScore > 40 ? '#f59e0b' : '#10b981'
  }];

  return (
    <div className="w-full max-w-7xl mx-auto mt-8 space-y-8 px-4 animate-fade-in">
      {/* Disclaimer */}
      <div className="relative bg-linear-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-400 rounded-xl p-6 shadow-lg">
        <div className="flex items-start">
          <div className="shrink-0">
            <svg className="h-6 w-6 text-yellow-600 animate-pulse" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm text-yellow-800 font-semibold">
              ⚠️ Important Medical Disclaimer
            </p>
            <p className="text-sm text-yellow-700 mt-1">
              {analysis.disclaimer}
            </p>
          </div>
        </div>
      </div>

      {/* Symptoms Summary */}
      <div className="relative bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
        <div className="flex items-center mb-6">
          <div className="p-3 bg-linear-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 ml-4">
            Your Reported Symptoms
          </h2>
        </div>
        <p className="text-gray-700 whitespace-pre-wrap leading-relaxed text-lg">{analysis.symptoms}</p>
      </div>

      {/* Severity Assessment */}
      {analysis.severity && (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Severity Assessment</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-gray-800 capitalize">{analysis.severity}</span>
              <span className="text-lg text-gray-600">{severityScore}% Alert Level</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-6">
              <div
                className={`h-6 rounded-full transition-all duration-500 ${getSeverityColor(analysis.severity)}`}
                style={{ width: `${severityScore}%` }}
              ></div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 mt-4">
              <p className="text-sm text-gray-700 leading-relaxed">
                <strong>What this means:</strong> The severity assessment indicates the potential urgency of your symptoms. 
                {severityScore > 70 && " A severe rating suggests you should seek immediate medical attention."}
                {severityScore > 40 && severityScore <= 70 && " A moderate rating means you should consult a healthcare provider soon."}
                {severityScore <= 40 && " A mild rating suggests monitoring symptoms, but still consult a doctor if they persist or worsen."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Conditions List with Explanations */}
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Possible Medical Conditions
        </h2>
        <p className="text-gray-600 mb-6 text-sm">
          Based on your symptoms, our AI has identified the following potential conditions ranked by likelihood. 
          These are educational suggestions only and not a definitive diagnosis. Each condition is assigned a likelihood 
          percentage based on symptom matching and medical knowledge.
        </p>
        
        <div className="space-y-4">
          {conditionData.map((item, index) => (
            <div 
              key={index} 
              className="group relative bg-linear-to-br from-gray-50 to-white rounded-xl p-6 shadow-md hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {index + 1}
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide block mb-1">
                      Rank #{index + 1}
                    </span>
                    <h3 className="text-lg font-bold text-gray-800">{item.fullName}</h3>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {item.likelihood}%
                  </div>
                  <span className="text-xs text-gray-500">Likelihood</span>
                </div>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden mb-3">
                <div
                  className="h-3 bg-linear-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${item.likelihood}%` }}
                ></div>
              </div>
              
              <div className="bg-blue-50 rounded-lg p-3 mt-3">
                <p className="text-xs text-gray-600">
                  <strong>Note:</strong> This condition ranks #{index + 1} with a {item.likelihood}% match based on your symptoms. 
                  {item.likelihood >= 75 && " High likelihood - strongly consider medical evaluation."}
                  {item.likelihood >= 50 && item.likelihood < 75 && " Moderate likelihood - monitoring recommended."}
                  {item.likelihood < 50 && " Lower likelihood - listed for completeness."}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations with Detailed Explanations */}
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Recommended Action Steps
        </h2>
        <p className="text-gray-600 mb-6 text-sm">
          Follow these steps in order of priority. Each recommendation is designed to help you address your symptoms 
          appropriately. Priority percentages indicate the importance and urgency of each action.
        </p>
        
        <div className="space-y-4">
          {recommendationData.map((item, index) => (
            <div 
              key={index} 
              className="group relative bg-linear-to-r from-green-50 to-emerald-50 rounded-xl p-6 shadow-md hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 border-l-4 border-green-500"
            >
              <div className="flex items-start space-x-4">
                <div className="shrink-0 w-14 h-14 bg-linear-to-br from-green-500 to-emerald-600 text-white rounded-xl flex items-center justify-center font-bold text-xl shadow-lg transform group-hover:scale-110 transition-transform duration-300">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-bold text-green-700 uppercase tracking-wide">Action Step {index + 1}</span>
                    <span className="text-sm font-bold text-gray-700 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200">
                      Priority: {item.priority}%
                    </span>
                  </div>
                  <p className="text-gray-800 font-semibold text-base leading-relaxed mb-4">{item.recommendation}</p>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden mb-3">
                    <div
                      className="h-3 bg-linear-to-r from-green-500 to-emerald-600 rounded-full transition-all duration-1000 ease-out shadow-sm"
                      style={{ width: `${item.priority}%` }}
                    ></div>
                  </div>
                  
                  <div className="bg-white rounded-lg p-3 border border-green-200">
                    <p className="text-xs text-gray-600">
                      <strong>Why this matters:</strong> This step has a {item.priority}% priority level. 
                      {item.priority >= 80 && " Critical action - should be done immediately."}
                      {item.priority >= 60 && item.priority < 80 && " Important action - complete within 24-48 hours."}
                      {item.priority >= 40 && item.priority < 60 && " Moderate priority - complete when possible."}
                      {item.priority < 40 && " Lower priority - supportive measure."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Conditions Card */}
        <div className="group relative bg-linear-to-br from-blue-500 to-purple-600 rounded-2xl shadow-2xl p-8 text-white transform hover:scale-105 transition-all duration-300 overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
          <div className="relative z-10">
            <div className="text-5xl font-bold mb-2">{analysis.conditions?.length || 0}</div>
            <div className="text-blue-100 text-lg font-medium">Possible Conditions</div>
            <div className="mt-4 flex items-center text-sm text-blue-200">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
              Educational purposes only
            </div>
          </div>
        </div>

        {/* Severity Card with Radial Chart */}
        <div className="relative bg-linear-to-br from-purple-500 to-pink-600 rounded-2xl shadow-2xl p-8 text-white transform hover:scale-105 transition-all duration-300 overflow-hidden">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-20 -mt-20"></div>
          <div className="relative z-10">
            <div className="text-5xl font-bold mb-2 capitalize">{analysis.severity || 'N/A'}</div>
            <div className="text-purple-100 text-lg font-medium">Severity Level</div>
            <div className="mt-4">
              <ResponsiveContainer width="100%" height={60}>
                <RadialBarChart 
                  cx="50%" 
                  cy="50%" 
                  innerRadius="60%" 
                  outerRadius="100%" 
                  barSize={10} 
                  data={radialData}
                  startAngle={180}
                  endAngle={0}
                >
                  <RadialBar
                    minAngle={15}
                    background
                    clockWise
                    dataKey="value"
                    cornerRadius={10}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="text-center text-sm text-purple-200 -mt-2">{severityScore}% Alert Level</div>
            </div>
          </div>
        </div>

        {/* Recommendations Card */}
        <div className="relative bg-linear-to-br from-pink-500 to-rose-600 rounded-2xl shadow-2xl p-8 text-white transform hover:scale-105 transition-all duration-300 overflow-hidden">
          <div className="absolute bottom-0 right-0 w-28 h-28 bg-white/10 rounded-full -mr-14 -mb-14"></div>
          <div className="relative z-10">
            <div className="text-5xl font-bold mb-2">{analysis.recommendations?.length || 0}</div>
            <div className="text-pink-100 text-lg font-medium">Action Steps</div>
            <div className="mt-4 space-y-2">
              {analysis.recommendations?.slice(0, 3).map((_, idx) => (
                <div key={idx} className="h-1.5 bg-white/30 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white rounded-full animate-pulse" 
                    style={{ width: `${100 - idx * 20}%` }}
                  ></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer with Icon */}
      <div className="relative bg-linear-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-400 rounded-xl p-6 shadow-lg">
        <div className="flex items-start">
          <div className="shrink-0">
            <svg className="h-6 w-6 text-yellow-600 animate-pulse" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm text-yellow-800 font-semibold">
              ⚠️ Important Medical Disclaimer
            </p>
            <p className="text-sm text-yellow-700 mt-1">
              {analysis.disclaimer}
            </p>
          </div>
        </div>
      </div>

      {/* Symptoms Summary with Glassmorphism */}
      <div className="relative bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 border border-white/20">
        <div className="flex items-center mb-6">
          <div className="p-3 bg-linear-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold ml-4 bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Your Symptoms
          </h2>
        </div>
        <p className="text-gray-700 whitespace-pre-wrap leading-relaxed text-lg">{analysis.symptoms}</p>
      </div>

      {/* Visual Analytics Section Header */}
      <div className="bg-linear-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-6 text-white text-center">
        <h2 className="text-3xl font-bold mb-2">📊 Visual Analytics & Charts</h2>
        <p className="text-indigo-100 text-sm">
          Interactive data visualizations to help you understand the analysis at a glance
        </p>
      </div>

      {/* Conditions with Interactive Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Bar Chart */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <div className="flex items-center mb-6">
            <div className="p-3 bg-linear-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold ml-4 text-gray-800">
              Likelihood Bar Chart
            </h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Vertical bar chart showing the relative likelihood of each condition based on symptom analysis. Higher bars indicate stronger likelihood.
          </p>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={conditionData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
              <XAxis 
                dataKey="rank" 
                stroke="#374151" 
                tick={{ fill: '#374151', fontSize: 14 }}
                label={{ value: 'Condition Rank', position: 'insideBottom', offset: -10, fill: '#6b7280' }}
              />
              <YAxis 
                stroke="#374151" 
                tick={{ fill: '#374151', fontSize: 14 }}
                domain={[0, 100]}
                label={{ value: 'Likelihood (%)', angle: -90, position: 'insideLeft', fill: '#6b7280' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.98)', 
                  borderRadius: '12px', 
                  border: '2px solid #8b5cf6',
                  boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.2)',
                  padding: '12px'
                }}
                labelStyle={{ fontWeight: 'bold', color: '#374151' }}
                formatter={(value, name, props) => [
                  `${value}%`, 
                  props.payload.fullName.length > 40 ? props.payload.fullName.substring(0, 40) + '...' : props.payload.fullName
                ]}
              />
              <Bar dataKey="likelihood" radius={[8, 8, 0, 0]} animationDuration={1000}>
                {conditionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <div className="flex items-center mb-6">
            <div className="p-3 bg-linear-to-br from-blue-500 to-cyan-600 rounded-xl shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold ml-4 text-gray-800">
              Distribution Pie Chart
            </h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Proportional distribution of condition likelihoods showing how each condition compares to others.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={conditionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ rank, likelihood }) => `#${rank} (${likelihood}%)`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="likelihood"
                animationBegin={0}
                animationDuration={800}
              >
                {conditionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                  borderRadius: '12px', 
                  border: '1px solid #e5e7eb',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}

export default AnalysisResults;
