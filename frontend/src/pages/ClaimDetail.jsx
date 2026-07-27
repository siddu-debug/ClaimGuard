import React, { useState, useEffect } from 'react';
import { ArrowLeft, Sparkles, Shield, User, FileSpreadsheet, Percent, Calendar, CheckSquare, AlertTriangle, AlertCircle } from 'lucide-react';
import { getClaim, updateClaimStatus } from '../api/client';
import RiskBadge from '../components/RiskBadge';

const INCIDENT_TYPE_LABELS = {
  auto_collision: 'Auto Collision',
  water_damage: 'Water Damage',
  theft_burglary: 'Theft / Burglary',
  fire_damage: 'Fire Damage',
  slip_and_fall: 'Slip & Fall',
  hail_damage: 'Hail Damage'
};

export default function ClaimDetail({ claimId, onBack }) {
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchClaim = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getClaim(claimId);
        setClaim(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch claim detail.');
      } finally {
        setLoading(false);
      }
    };
    if (claimId) {
      fetchClaim();
    }
  }, [claimId]);

  const handleStatusUpdate = async (newStatus) => {
    setActionLoading(true);
    setError('');
    try {
      const updated = await updateClaimStatus(claimId, newStatus);
      setClaim(updated);
    } catch (err) {
      setError(err.message || 'Failed to update claim status.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse p-4">
        <div className="h-6 w-24 bg-slate-800 rounded"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-slate-800 rounded-xl"></div>
          <div className="h-96 bg-slate-800 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="space-y-4">
        <button onClick={onBack} className="btn-ghost pl-0">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-sm font-medium">
          {error || 'Claim not found.'}
        </div>
      </div>
    );
  }

  const scorePct = Math.round((claim.fraud_score || 0) * 100);
  const strokeDashoffset = 282.6 - (282.6 * (claim.fraud_score || 0));
  
  // Decide ring color
  const ringColor = claim.fraud_score > 0.8 
    ? 'stroke-rose-500' 
    : claim.fraud_score > 0.4 
      ? 'stroke-amber-500' 
      : 'stroke-emerald-500';

  const ringShadow = claim.fraud_score > 0.8
    ? 'rgba(239,68,68,0.2)'
    : claim.fraud_score > 0.4
      ? 'rgba(234,179,8,0.2)'
      : 'rgba(34,197,94,0.2)';

  const shapExplanation = claim.shap_values || {};
  const topFeatures = shapExplanation.top_features || [];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <button onClick={onBack} className="btn-ghost pl-0 self-start">
          <ArrowLeft className="w-4 h-4" />
          Back to Queue
        </button>
        <div className="flex flex-wrap gap-3">
          {(claim.status === 'manual_review' || claim.status === 'auto_approve' || claim.status === 'auto_reject') && (
            <>
              <button
                disabled={actionLoading}
                onClick={() => handleStatusUpdate('approved')}
                className="btn-success text-xs font-semibold px-4 py-2"
              >
                Override Approve
              </button>
              <button
                disabled={actionLoading}
                onClick={() => handleStatusUpdate('rejected')}
                className="btn-danger text-xs font-semibold px-4 py-2"
              >
                Override Reject
              </button>
            </>
          )}
          {claim.status === 'approved' && (
            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-4 py-2 border border-emerald-500/30 rounded-lg">
              Claim Approved by Adjuster
            </span>
          )}
          {claim.status === 'rejected' && (
            <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-4 py-2 border border-rose-500/30 rounded-lg">
              Claim Rejected by Adjuster
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Claim Details & ML Explainer */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Metadata Card */}
          <div className="glass-card p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-700/50 pb-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Database ID: #{claim.id}</span>
                <h2 className="text-xl font-bold text-white mt-0.5 flex items-center gap-2">
                  Claim ID: <span className="font-mono text-indigo-400">{claim.claim_id}</span>
                </h2>
              </div>
              <RiskBadge status={claim.status} size="lg" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <User className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Claimant</span>
                    <span className="text-sm font-semibold text-slate-200">{claim.claimant_name}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Policy ID</span>
                    <span className="text-sm font-mono text-indigo-300">{claim.policy_id}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Percent className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Prior Claims</span>
                    <span className="text-sm font-semibold text-slate-200">{claim.prior_claims_count} events</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Policy Effective Date</span>
                    <span className="text-sm font-semibold text-slate-200">{claim.policy_start_date}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Claim Loss Date</span>
                    <span className="text-sm font-semibold text-slate-200">{claim.claim_date}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <CheckSquare className="w-4.5 h-4.5 text-slate-500" />
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Incident Type</span>
                    <span className="text-sm font-semibold text-slate-200">{INCIDENT_TYPE_LABELS[claim.incident_type] || claim.incident_type}</span>
                  </div>
                </div>
              </div>
            </div>

            {claim.incident_description && (
              <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-4">
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Claim Narrative</span>
                <p className="text-sm text-slate-300 leading-relaxed font-sans">{claim.incident_description}</p>
              </div>
            )}
            
            {claim.raw_text && (
              <div className="border-t border-slate-800/80 pt-4">
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Original Raw Audio / OCR Text Input</span>
                <p className="text-xs text-slate-400 bg-slate-900/40 rounded p-3 italic border-l-2 border-indigo-500/50 font-sans">
                  "{claim.raw_text}"
                </p>
              </div>
            )}
          </div>

          {/* SHAP Factor attribution bar list */}
          <div className="glass-card p-6 space-y-4">
            <div>
              <h3 className="text-base font-bold text-white">SHAP Risk Drivers Attribution</h3>
              <p className="text-xs text-slate-400 mt-0.5">Statistical feature contribution weights determining the risk probability deviation</p>
            </div>
            
            <div className="space-y-3.5 pt-2">
              {topFeatures.length === 0 ? (
                <div className="text-xs text-slate-500 text-center py-4">No feature attributions saved for this claim.</div>
              ) : (
                topFeatures.map((f, i) => {
                  const val = f.contribution;
                  const absVal = Math.abs(val);
                  // Dynamic max scale logic, cap normalized bar width to a reasonable max
                  const barWidth = Math.min(100, Math.max(8, (absVal * 120)));
                  const formattedContribution = val > 0 ? `+${val.toFixed(3)}` : val.toFixed(3);

                  return (
                    <div key={i} className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center text-xs">
                      <span className="font-semibold text-slate-300 truncate sm:col-span-1" title={f.label}>
                        {f.label}
                      </span>
                      <div className="sm:col-span-2 flex items-center gap-2">
                        <div className="w-full bg-slate-900/60 rounded-full h-2 overflow-hidden border border-slate-700/30 flex">
                          {val >= 0 ? (
                            <div className="h-full bg-orange-500/90 shadow-[0_0_6px_rgba(249,115,22,0.4)]" style={{ width: `${barWidth}%`, marginLeft: '0' }} />
                          ) : (
                            <div className="h-full bg-cyan-500/90 shadow-[0_0_6px_rgba(6,182,212,0.4)]" style={{ width: `${barWidth}%`, marginLeft: 'auto' }} />
                          )}
                        </div>
                      </div>
                      <span className={`font-mono text-right font-bold sm:col-span-1 ${val >= 0 ? 'text-orange-400' : 'text-cyan-400'}`}>
                        {formattedContribution}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Right Side: Score Circle & Groq Narrative */}
        <div className="space-y-6">
          
          {/* Gauge Widget */}
          <div className="glass-card p-6 flex flex-col items-center justify-center text-center space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Fraud Risk Score</h3>

            <div className="relative flex items-center justify-center w-36 h-36">
              <svg className="w-full h-full">
                {/* Background Ring */}
                <circle
                  className="stroke-slate-800"
                  strokeWidth="8"
                  fill="transparent"
                  r="45"
                  cx="72"
                  cy="72"
                />
                {/* Value Ring */}
                <circle
                  className={`score-ring ${ringColor}`}
                  strokeWidth="8"
                  strokeDasharray="282.6"
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  fill="transparent"
                  r="45"
                  cx="72"
                  cy="72"
                  style={{ filter: `drop-shadow(0 0 6px ${ringShadow})` }}
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-extrabold text-white tracking-tight">{scorePct}%</span>
                <span className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold mt-0.5">Probability</span>
              </div>
            </div>

            <div className="w-full border-t border-slate-700/50 pt-3">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Auto-Approve</span>
                <span className="text-slate-500">Auto-Reject</span>
              </div>
              <div className="relative w-full h-2.5 bg-slate-900 rounded-full mt-1.5 overflow-hidden border border-slate-700/50">
                <div className="absolute left-[20%] w-[1px] h-full bg-slate-700"></div>
                <div className="absolute left-[80%] w-[1px] h-full bg-slate-700"></div>
                {/* Pointer indicator */}
                <div 
                  className="absolute top-0 bottom-0 w-2 bg-indigo-500 border border-white rounded-full transition-all duration-500"
                  style={{ left: `calc(${claim.fraud_score * 100}% - 4px)` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] text-slate-600 mt-1 font-mono">
                <span>0.00</span>
                <span>0.20</span>
                <span>0.80</span>
                <span>1.00</span>
              </div>
            </div>
          </div>

          {/* AI Narrative Explanation */}
          <div className="glass-card p-6 border-indigo-500/20 bg-indigo-950/20 relative overflow-hidden space-y-4">
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl"></div>
            <div className="flex items-center gap-2 border-b border-indigo-900/40 pb-3">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-white tracking-wide">AI Narrative Explanation</h3>
            </div>
            
            <p className="text-sm text-slate-200 leading-relaxed font-sans italic">
              "{claim.explanation || 'No explanation generated.'}"
            </p>

            <div className="text-[11px] text-slate-500 flex items-center gap-1.5 pt-2 border-t border-indigo-900/30">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>llama-3.3-70b-versatile synthesized</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
