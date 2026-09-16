import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [form, setForm] = useState({ name: '', cost: '', billing_cycle: 'monthly', category: '', next_renewal_date: '' });
  const [error, setError] = useState('');

  const loadSubscriptions = () => {
    api.get('/subscriptions/').then((res) => setSubscriptions(res.data));
  };

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/subscriptions/', form);
      setForm({ name: '', cost: '', billing_cycle: 'monthly', category: '', next_renewal_date: '' });
      loadSubscriptions();
    } catch (err) {
      setError('Failed to add subscription. Check all fields are filled correctly.');
    }
  };

  const triggerCheckin = async (id) => {
    await api.post(`/subscriptions/${id}/checkin/`);
    alert('Check-in triggered! Go to your CheckIns in Django admin, or build a CheckIns page next, to respond to it.');
  };

  return (
    <div style={{ maxWidth: 700, margin: '40px auto' }}>
      <Link to="/dashboard">← Back to Dashboard</Link>
      <h2>All Subscriptions</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: 30 }}>
        <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required />
        <input name="cost" placeholder="Cost" value={form.cost} onChange={handleChange} required />
        <select name="billing_cycle" value={form.billing_cycle} onChange={handleChange}>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
        <input name="category" placeholder="Category" value={form.category} onChange={handleChange} />
        <input name="next_renewal_date" type="date" value={form.next_renewal_date} onChange={handleChange} required />
        <button type="submit">Add Subscription</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Name</th><th>Cost</th><th>Cycle</th><th>Category</th><th>Renewal</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((sub) => (
            <tr key={sub.id}>
              <td>{sub.name}</td>
              <td>₹{sub.cost}</td>
              <td>{sub.billing_cycle}</td>
              <td>{sub.category}</td>
              <td>{sub.next_renewal_date}</td>
              <td>{sub.status}</td>
              <td><button onClick={() => triggerCheckin(sub.id)}>Trigger Check-in</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}