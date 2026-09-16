import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function Graveyard() {
  const [flagged, setFlagged] = useState([]);

  useEffect(() => {
    api.get('/subscriptions/').then((res) => {
      setFlagged(res.data.filter((s) => s.status === 'flagged'));
    });
  }, []);

  const totalWaste = flagged.reduce((sum, s) => sum + parseFloat(s.monthly_cost), 0);

  return (
    <div style={{ maxWidth: 600, margin: '40px auto' }}>
      <Link to="/dashboard">← Back to Dashboard</Link>
      <h2>🪦 The Graveyard</h2>
      <p>Subscriptions flagged as likely unused.</p>
      <h3 style={{ color: 'red' }}>Total wasted: ₹{totalWaste.toFixed(2)}/month</h3>

      <ul>
        {flagged.map((sub) => (
          <li key={sub.id}>{sub.name} — ₹{sub.monthly_cost}/month ({sub.category})</li>
        ))}
      </ul>
      {flagged.length === 0 && <p>Nothing here yet — that's a good thing!</p>}
    </div>
  );
}