import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { HardHat, Clock, Settings, TrendingUp, Layers, Activity, AlertCircle, Database, Download } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [formData, setFormData] = useState({
    worker_count: 50, machinery_status: 1, task_progress: 75, vibration_level: 20,
    safety_incidents: 0, material_shortage_alert: 0, update_frequency: 10,
    temperature: 25, humidity: 50, energy_consumption: 150, risk_score: 2,
    simulation_deviation: 1.2, material_usage: 450, equipment_utilization_rate: 65,
    cost_deviation: 5, time_deviation: 2
  });

  const [results, setResults] = useState({ cost: null, time: null, equipment: null, segmentation: null });
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({ total: 0, avg_cost: 0, alerts: 0 });
  const [loading, setLoading] = useState({});

  const fetchData = async () => {
    try {
      const [hRes, sRes] = await Promise.all([
        axios.get(`${API_BASE}/history`),
        axios.get(`${API_BASE}/stats`)
      ]);
      if (!hRes.data.error) setHistory(hRes.data);
      if (!sRes.data.error) setStats(sRes.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => { fetchData(); }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
  };

  const predict = async (type) => {
    setLoading(prev => ({ ...prev, [type]: true }));
    try {
      const res = await axios.post(`${API_BASE}/predict/${type}`, formData);
      setResults(prev => ({ ...prev, [type]: res.data }));
      fetchData();
    } catch (err) { console.error(err); }
    setLoading(prev => ({ ...prev, [type]: false }));
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(22);
    doc.setTextColor(243, 122, 1); // BATIX Orange
    doc.text('BATIX AI - Analysis Report', 14, 22);
    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);

    const tableData = [
      ['Budget Variance', results.cost ? `${results.cost.prediction.toFixed(2)}%` : 'N/A', results.cost?.interpretation || 'N/A'],
      ['Schedule Delay', results.time ? `${results.time.prediction.toFixed(1)} Days` : 'N/A', results.time?.interpretation || 'N/A'],
      ['Equipment Utilization', results.equipment?.prediction || 'N/A', results.equipment?.interpretation || 'N/A'],
      ['Site Cluster', results.segmentation?.segment_name || 'N/A', results.segmentation?.interpretation || 'N/A'],
    ];

    autoTable(doc, {
      startY: 40,
      head: [['Metric', 'Value', 'Interpretation']],
      body: tableData,
      theme: 'striped',
      headStyles: { fillColor: [243, 122, 1] }
    });

    const paramData = Object.entries(formData).map(([k, v]) => [k.replace(/_/g, ' '), v]);
    autoTable(doc, {
      startY: doc.lastAutoTable.finalY + 15,
      head: [['Parameter', 'Value']],
      body: paramData,
      theme: 'plain'
    });

    doc.save(`BATIX_Report_${Date.now()}.pdf`);
  };

  const radarData = [
    { subject: 'Progress', A: formData.task_progress },
    { subject: 'Workers', A: (formData.worker_count / 200) * 100 },
    { subject: 'Risk', A: (formData.risk_score / 10) * 100 },
    { subject: 'Util.', A: formData.equipment_utilization_rate },
    { subject: 'Vibration', A: formData.vibration_level },
  ];

  return (
    <div className="dashboard">
      <header style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem', padding: '1rem', background: '#1e293b', borderRadius: '1rem', border: '1px solid #334155'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
          <img src="/logo.png" alt="BATIX Logo" style={{height: '50px'}} />
          <h1 className="title" style={{margin: 0, fontSize: '1.5rem'}}>AI BY BATIX</h1>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <div style={{textAlign: 'right', marginRight: '1rem'}}>
            <div style={{fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase'}}>Fleet Efficiency</div>
            <div style={{fontSize: '1.1rem', fontWeight: 700, color: '#f37a01'}}>{(100 - stats.avg_cost).toFixed(1)}%</div>
          </div>
          <button onClick={generatePDF} className="btn" style={{background: '#334155'}}><Download size={16} /> Rapport PDF</button>
        </div>
      </header>

      {/* Stats Bar */}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem'}}>
        <StatCard icon={<Database size={20} />} label="Analyses Totales" value={stats.total} color="#f37a01" />
        <StatCard icon={<AlertCircle size={20} />} label="Alertes Détectées" value={stats.alerts} color="#ef4444" />
        <StatCard icon={<Activity size={20} />} label="Déviation Moyenne" value={`${stats.avg_cost}%`} color="#3b82f6" />
        <StatCard icon={<TrendingUp size={20} />} label="Santé du Parc" value="Optimal" color="#10b981" />
      </div>

      <div className="grid">
        {/* Left Col */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
          <div className="card">
            <h2><Settings size={18} /> Paramètres Projet</h2>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
              {Object.keys(formData).slice(0, 10).map(key => (
                <div className="input-group" key={key}>
                  <label>{key.replace(/_/g, ' ')}</label>
                  <input name={key} value={formData[key]} onChange={handleChange} type="number" />
                </div>
              ))}
            </div>
          </div>
          <div className="card" style={{height: '320px'}}>
            <h2><Activity size={18} /> Profil de Risque</h2>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" tick={{fill: '#94a3b8', fontSize: 10}} />
                <Radar name="BATIX" dataKey="A" stroke="#f37a01" fill="#f37a01" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Col */}
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
          <PredictionCard title="Coût (Déviation)" result={results.cost} onPredict={() => predict('cost')} loading={loading.cost} icon={<TrendingUp />} />
          <PredictionCard title="Planning (Retard)" result={results.time} onPredict={() => predict('time')} loading={loading.time} icon={<Clock />} unit="Jours" />
          <PredictionCard title="Équipement (Utilisation)" result={results.equipment} onPredict={() => predict('equipment')} loading={loading.equipment} icon={<HardHat />} />
          <PredictionCard title="Segmentation Site" result={results.segmentation} onPredict={() => predict('segmentation')} loading={loading.segmentation} icon={<Layers />} valKey="segment_name" />
          
          <div className="card" style={{gridColumn: 'span 2'}}>
            <h2><Database size={18} /> Historique BATIX (SQL)</h2>
            <div style={{maxHeight: '200px', overflowY: 'auto'}}>
              <table style={{width: '100%', fontSize: '0.8rem'}}>
                <thead><tr style={{color: '#94a3b8', textAlign: 'left'}}><th style={{padding: '0.5rem'}}>Heure</th><th>Module</th><th>Valeur</th><th>Interprétation</th></tr></thead>
                <tbody>
                  {history.map(item => (
                    <tr key={item.id} style={{borderTop: '1px solid #334155'}}><td style={{padding: '0.5rem'}}>{new Date(item.created_at).toLocaleTimeString()}</td><td>{item.prediction_type}</td><td style={{color: '#f37a01', fontWeight: 700}}>{item.predicted_value}</td><td>{item.interpretation}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="card" style={{display: 'flex', alignItems: 'center', gap: '1rem', borderTop: `4px solid ${color}`}}>
      <div style={{color: color}}>{icon}</div>
      <div>
        <div style={{fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase'}}>{label}</div>
        <div style={{fontSize: '1.2rem', fontWeight: 800}}>{value}</div>
      </div>
    </div>
  );
}

function PredictionCard({ title, icon, result, onPredict, loading, unit = "%", valKey = "prediction" }) {
  return (
    <div className="card" style={{display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: '#f37a01'}}>{icon} <span style={{color: '#f8fafc'}}>{title}</span></div>
      <button className="btn" onClick={onPredict} disabled={loading}>{loading ? 'Calcul...' : 'Lancer'}</button>
      {result && (
        <div className="result">
          <div className="result-value" style={{color: '#f37a01'}}>{typeof result[valKey] === 'number' ? result[valKey].toFixed(1) + unit : result[valKey]}</div>
          <div style={{fontSize: '0.7rem', color: '#94a3b8'}}>{result.interpretation}</div>
        </div>
      )}
    </div>
  );
}

export default App;
