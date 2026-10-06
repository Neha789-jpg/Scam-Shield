import type { Signal } from "../types";

interface SignalListProps {
  signals: Signal[];
}

const statusMark = {
  safe: "✓",
  warning: "!",
  info: "i",
  unavailable: "—",
};


export function SignalList({ signals }: SignalListProps) {
  return (
    <div className="signal-list">
      {signals.map((signal) => (
        <article className={`signal signal-${signal.status}`} key={signal.code}>
          <span className="signal-mark" aria-hidden="true">
            {statusMark[signal.status]}
          </span>
          <div>
            <div className="signal-heading">
              <h4>{signal.title}</h4>
              {signal.score_delta > 0 && <span>+{signal.score_delta}</span>}
            </div>
            <p>{signal.message}</p>
            {/* Show extracted raw UPI or handle evidence */}
            {signal.evidence && (
              <code className="evidence-badge" style={{
                display: 'inline-block',
                marginTop: '6px',
                padding: '2px 8px',
                background: '#162942',
                border: '1px solid #2f80ff',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#7dd3fc'
              }}>
                Evidence: {signal.evidence}
              </code>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}