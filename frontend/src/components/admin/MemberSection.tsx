'use client';

import { useState, useEffect } from 'react';
import { membersAPI } from '@/lib/api';

function MemberSection() {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [memberId, setMemberId] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  useEffect(() => {
    fetchMembers();
  }, []);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const response = await membersAPI.getMembers();
      setMembers(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setActiveAction(null);
    setName('');
    setEmail('');
    setPhone('');
    setError(null);
  };

  // Create member
  const handleCreateMember = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      await membersAPI.createMember({
        name,
        email,
        phone,
      });
      setSuccess('Member created successfully!');
      resetForm();
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Update Member
  const handleUpdateMember = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updateData: any = {};
      if (name) updateData.name = name;
      if (email) updateData.email = email;
      if (phone) updateData.phone = phone;

      if (Object.keys(updateData).length === 0) {
        setError('Please provide at least one field to update');
        setLoading(false);
        return;
      }

      await membersAPI.updateMember(parseInt(memberId), updateData);
      setSuccess('Member updated successfully!');
      resetForm();
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search Member By ID
  const handleSearchMemberById = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await membersAPI.getMember(parseInt(memberId));
      setMembers([response.data]);
      setSuccess('Member found!');
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete a Member
  const handleDeleteMember = async (e: any) => {
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this member?')) return;

    setLoading(true);
    try {
      await membersAPI.deleteMember(parseInt(memberId));
      setSuccess('Member successfully deleted!');
      resetForm();
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="section-content">
      <h2 className="section-title">Members Management</h2>

      {error && <div className="message error-message">{error}</div>}
      {success && <div className="message success-message">{success}</div>}

      <div className="action-buttons">
        <button onClick={fetchMembers}>Get Members</button>
        <button onClick={() => setActiveAction('createMember')}>
          Add Member
        </button>
        <button onClick={() => setActiveAction('updateMember')}>
          Edit Member
        </button>
        <button onClick={() => setActiveAction('searchMember')}>
          Search Member
        </button>
        <button onClick={() => setActiveAction('deleteMember')}>
          Delete Member
        </button>
      </div>

      {activeAction === 'createMember' && (
        <form onSubmit={handleCreateMember} className="action-form">
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Email *"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Phone Number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Member'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'updateMember' && (
        <form onSubmit={handleUpdateMember} className="action-form">
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="text"
            placeholder="Phone Number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Updating...' : 'Update Member'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'searchMember' && (
        <form onSubmit={handleSearchMemberById} className="action-form">
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search Member'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'deleteMember' && (
        <form onSubmit={handleDeleteMember} className="action-form">
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Deleting...' : 'Delete Member'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="data-table">
        <h3>Members List ({members.length})</h3>
        {loading && !activeAction ? (
          <p className="loading-text">Loading Members...</p>
        ) : members.length === 0 ? (
          <p className="no-data-text">No Members Found</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone Number</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id}>
                  <td>{member.id}</td>
                  <td>{member.name || '-'}</td>
                  <td>{member.email}</td>
                  <td>{member.phone || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default MemberSection;
