import React, { useState } from 'react';
import { X, Sparkles, Send, FileText } from 'lucide-react';
import { createClaim, createUnstructuredClaim } from '../api/client';

export default function NewClaimModal({ isOpen, onClose, onClaimCreated }) {
  const [activeTab, setActiveTab] = useState('unstructured'); // 'unstructured' | 'structured'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Unstructured fields
  const [rawText, setRawText] = useState('');

  // Structured fields
  const [formData, setFormData] = useState({
    policy_id: '',
    claimant_name: '',
    policy_start_date: '',
    claim_date: '',
    claim_amount: '',
    incident_type: 'auto_collision',
    incident_description: '',
    prior_claims_count: 0
  });

  if (!isOpen) return null;

  const handleStructuredChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'prior_claims_count' || name === 'claim_amount' ? (value === '' ? '' : Number(value)) : value
    }));
  };

  const handleUnstructuredSubmit = async (e) => {
    e.preventDefault();
    if (!rawText.trim()) return;
    setLoading(true);
    setError('');
    try {
      const result = await createUnstructuredClaim(rawText);
      onClaimCreated(result);
      onClose();
      setRawText('');
    } catch (err) {
      setError(err.message || 'Failed to submit narrative claim.');
    } finally {
      setLoading(false);
    }
  };

  const handleStructuredSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...formData,
        claim_amount: Number(formData.claim_amount),
        prior_claims_count: Number(formData.prior_claims_count)
      };
      const result = await createClaim(payload);
      onClaimCreated(result);
      onClose();
      setFormData({
        policy_id: '',
        claimant_name: '',
        policy_start_date: '',
        claim_date: '',
        claim_amount: '',
        incident_type: 'auto_collision',
        incident_description: '',
        prior_claims_count: 0
      });
    } catch (err) {
      setError(err.message || 'Failed to submit structured claim.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold text-white">Create New Claim</h2>
            <p className="text-xs text-slate-400 mt-1">Submit claims for real-time automated fraud scoring and decisioning</p>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-700/50 rounded-lg text-slate-400 hover:text-white transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-lg font-medium">
            {error}
          </div>
        )}

        <div className="flex border-b border-slate-700/60 mb-6">
          <button
            onClick={() => setActiveTab('unstructured')}
            className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-all ${
              activeTab === 'unstructured'
                ? 'border-indigo-500 text-white'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-4 h-4 text-indigo-400" />
            AI Unstructured Text
          </button>
          <button
            onClick={() => setActiveTab('structured')}
            className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-all ${
              activeTab === 'structured'
                ? 'border-indigo-500 text-white'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4 text-slate-400" />
            Structured Manual Entry
          </button>
        </div>

        {activeTab === 'unstructured' ? (
          <form onSubmit={handleUnstructuredSubmit} className="space-y-4">
            <div>
              <label className="form-label">Paste Claim Narrative / Free Text Description</label>
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="e.g. Claimant John Smith (Policy POL-99231) filed a claim on 2024-07-20. Slipped and fell on wet tile floor inside grocery store entrance. Claiming $12,500 in medical and rehabilitation coverage..."
                className="form-input min-h-[160px] font-sans resize-none"
                required
              />
              <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed">
                The Groq Llama-3 model will parse the unstructured text to extract metadata fields like claimant name, policy ID, claim date, and amount before executing risk evaluations.
              </p>
            </div>
            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800/80">
              <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'AI Parsing & Scoring...' : 'Submit & Analyze'}
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleStructuredSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">Claimant Name</label>
                <input
                  type="text"
                  name="claimant_name"
                  value={formData.claimant_name}
                  onChange={handleStructuredChange}
                  placeholder="e.g. Jane Doe"
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label className="form-label">Policy ID</label>
                <input
                  type="text"
                  name="policy_id"
                  value={formData.policy_id}
                  onChange={handleStructuredChange}
                  placeholder="e.g. POL-12345"
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label className="form-label">Policy Start Date</label>
                <input
                  type="date"
                  name="policy_start_date"
                  value={formData.policy_start_date}
                  onChange={handleStructuredChange}
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label className="form-label">Claim Date</label>
                <input
                  type="date"
                  name="claim_date"
                  value={formData.claim_date}
                  onChange={handleStructuredChange}
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label className="form-label">Claim Amount ($)</label>
                <input
                  type="number"
                  name="claim_amount"
                  value={formData.claim_amount}
                  onChange={handleStructuredChange}
                  placeholder="e.g. 5200"
                  min="0"
                  className="form-input"
                  required
                />
              </div>
              <div>
                <label className="form-label">Incident Type</label>
                <select
                  name="incident_type"
                  value={formData.incident_type}
                  onChange={handleStructuredChange}
                  className="form-select"
                >
                  <option value="auto_collision">Auto Collision</option>
                  <option value="water_damage">Water Damage</option>
                  <option value="theft_burglary">Theft / Burglary</option>
                  <option value="fire_damage">Fire Damage</option>
                  <option value="slip_and_fall">Slip & Fall</option>
                  <option value="hail_damage">Hail Damage</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="form-label">Prior Claims Count</label>
                <input
                  type="number"
                  name="prior_claims_count"
                  value={formData.prior_claims_count}
                  onChange={handleStructuredChange}
                  placeholder="0"
                  min="0"
                  className="form-input"
                  required
                />
              </div>
              <div className="col-span-2">
                <label className="form-label">Incident Description</label>
                <textarea
                  name="incident_description"
                  value={formData.incident_description}
                  onChange={handleStructuredChange}
                  placeholder="Detailed description of the claim event..."
                  className="form-input min-h-[80px]"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800/80">
              <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Scoring...' : 'Submit Claim'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
