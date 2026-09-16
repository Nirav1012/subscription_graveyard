import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const { logout } = useAuth();

  useEffect(() => {
    api.get('/dashboard/')
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load dashboard.'));
  }, []);

  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!data) return <p>Loading...</p>;

  return (
    <div style={{ maxWidth: 600, margin: '40px auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2>Dashboard</h2>
        <button onClick={logout}>Log Out</button>
      </div>

      <div style={{ display: 'flex', gap: 20, margin: '20px 0' }}>
        <div style={{ border: '1px solid #ccc', padding: 16, flex: 1 }}>
          <p>Monthly Burn</p>
          <h3>₹{data.total_monthly_burn}</h3>
        </div>
        <div style={{ border: '1px solid red', padding: 16, flex: 1 }}>
          <p>Flagged Waste</p>
          <h3 style={{ color: 'red' }}>₹{data.total_flagged_monthly_waste}</h3>
        </div>
      </div>

      <p>
        Active: {data.subscription_counts.active} |
        Flagged: {data.subscription_counts.flagged} |
        Cancelled: {data.subscription_counts.cancelled}
      </p>

      <h4>Category Breakdown</h4>
      <ul>
        {Object.entries(data.category_breakdown).map(([category, amount]) => (
          <li key={category}>{category}: ₹{amount}</li>
        ))}
      </ul>

      <h4>Upcoming Renewals</h4>
      <ul>
        {data.upcoming_renewals.map((sub) => (
          <li key={sub.id}>{sub.name} — {sub.next_renewal_date}</li>
        ))}
      </ul>

      <nav style={{ marginTop: 20 }}>
        <Link to="/subscriptions">All Subscriptions</Link> |{' '}
        <Link to="/graveyard">Graveyard</Link>
      </nav>
    </div>
  );
}