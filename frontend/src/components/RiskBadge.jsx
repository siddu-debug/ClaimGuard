/**
 * RiskBadge component — color-coded decision/status badge.
 * Handles: auto_approve, auto_reject, manual_review, approved, rejected, pending.
 */

const BADGE_STYLES = {
  auto_approve: {
    bg: 'bg-emerald-500/15 border-emerald-500/30',
    text: 'text-emerald-400',
    dot: 'bg-emerald-400',
    label: 'Auto Approved',
  },
  approved: {
    bg: 'bg-emerald-500/15 border-emerald-500/30',
    text: 'text-emerald-400',
    dot: 'bg-emerald-400',
    label: 'Approved',
  },
  auto_reject: {
    bg: 'bg-red-500/15 border-red-500/30',
    text: 'text-red-400',
    dot: 'bg-red-400',
    label: 'Auto Rejected',
  },
  rejected: {
    bg: 'bg-red-500/15 border-red-500/30',
    text: 'text-red-400',
    dot: 'bg-red-400',
    label: 'Rejected',
  },
  manual_review: {
    bg: 'bg-amber-500/15 border-amber-500/30',
    text: 'text-amber-400',
    dot: 'bg-amber-400',
    label: 'Manual Review',
  },
  pending: {
    bg: 'bg-slate-500/15 border-slate-500/30',
    text: 'text-slate-400',
    dot: 'bg-slate-400',
    label: 'Pending',
  },
}

export default function RiskBadge({ status, size = 'sm' }) {
  const style = BADGE_STYLES[status] || BADGE_STYLES.pending
  const sizeClass = size === 'lg'
    ? 'px-3 py-1.5 text-sm gap-2'
    : 'px-2.5 py-1 text-xs gap-1.5'

  return (
    <span className={`inline-flex items-center rounded-full border font-semibold
      ${style.bg} ${style.text} ${sizeClass}`}>
      <span className={`rounded-full flex-shrink-0 ${style.dot} ${size === 'lg' ? 'w-2 h-2' : 'w-1.5 h-1.5'}`} />
      {style.label}
    </span>
  )
}
