import React, { useEffect, useState } from 'react';
import { fetchIssueAnalysis, fetchIssueDetail, fetchIssueScore } from '../services/api';
import { IssueAnalysis, IssueDetail, IssueScore } from '../types/issue';
import {
  AlertCircle,
  AlertTriangle,
  BrainCircuit,
  Calendar,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Copy,
  ExternalLink,
  GitPullRequest,
  GraduationCap,
  HelpCircle,
  ListOrdered,
  Loader2,
  MessageSquare,
  Sparkles,
  User,
  X,
} from 'lucide-react';

interface IssueDetailModalProps {
  issueId: string | null;
  onClose: () => void;
}

export const IssueDetailModal: React.FC<IssueDetailModalProps> = ({ issueId, onClose }) => {
  const [detail, setDetail] = useState<IssueDetail | null>(null);
  const [scoreObj, setScoreObj] = useState<IssueScore | null>(null);
  const [analysisObj, setAnalysisObj] = useState<IssueAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // UI Interactive State
  const [copiedPlan, setCopiedPlan] = useState<boolean>(false);
  const [showConfidenceReasoning, setShowConfidenceReasoning] = useState<boolean>(false);

  useEffect(() => {
    if (!issueId) return;

    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchIssueDetail(issueId);
        setDetail(data);

        if (data.score) {
          setScoreObj(data.score);
        } else {
          const scoreData = await fetchIssueScore(issueId).catch(() => null);
          setScoreObj(scoreData);
        }

        if (data.analysis) {
          setAnalysisObj(data.analysis);
        } else {
          const aiData = await fetchIssueAnalysis(issueId).catch(() => null);
          setAnalysisObj(aiData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load issue details');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [issueId]);

  if (!issueId) return null;

  const handleCopyPlan = () => {
    if (!analysisObj || !analysisObj.implementation_plan) return;
    const text = analysisObj.implementation_plan.map((step, i) => `${i + 1}. ${step}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopiedPlan(true);
    setTimeout(() => setCopiedPlan(false), 2000);
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'Implement':
        return (
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontWeight: 700,
              fontSize: '0.8125rem',
            }}
          >
            🟢 Implement
          </span>
        );
      case 'Investigate':
        return (
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              background: 'rgba(245, 158, 11, 0.15)',
              color: '#fbbf24',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              fontWeight: 700,
              fontSize: '0.8125rem',
            }}
          >
            🟡 Investigate
          </span>
        );
      default:
        return (
          <span
            style={{
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              background: 'rgba(239, 68, 68, 0.15)',
              color: '#f87171',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              fontWeight: 700,
              fontSize: '0.8125rem',
            }}
          >
            🔴 Skip
          </span>
        );
    }
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff) {
      case 'beginner':
        return { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399' };
      case 'intermediate':
        return { bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24' };
      default:
        return { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171' };
    }
  };

  const getRuleLabel = (key: string): string => {
    const map: Record<string, string> = {
      good_first_issue: 'Good First Issue / Help Wanted Label',
      unassigned: 'Unassigned Developer Status',
      bug_label: 'Bug / Defect Classification',
      has_reproduction_steps: 'Reproduction Steps / Code Snippets Provided',
      description_quality: 'Detailed Description (>200 characters)',
      security_critical: 'Security / Critical Priority Label',
      feature_enhancement: 'Feature / Enhancement Label',
      state_closed: 'Issue State is Closed',
      is_pull_request: 'Linked Pull Request Entity',
      discussion_noise: 'High Comment Discussion Noise',
    };
    return map[key] || key.replace(/_/g, ' ');
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
        padding: '1.5rem 1rem',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: '900px',
          width: '100%',
          maxHeight: '92vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '0',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '1.5rem 2rem',
            borderBottom: '1px solid var(--border-color)',
            position: 'relative',
          }}
        >
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: '1.25rem',
              right: '1.25rem',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '0.375rem',
            }}
          >
            <X className="w-5 h-5" />
          </button>

          {loading ? (
            <div
              style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem 0' }}
            >
              <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
              <span>Loading AI Coach insights...</span>
            </div>
          ) : error ? (
            <div style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          ) : detail ? (
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  marginBottom: '0.5rem',
                }}
              >
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    padding: '0.25rem 0.625rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background:
                      detail.state === 'open'
                        ? 'var(--status-success-bg)'
                        : 'rgba(107, 114, 128, 0.2)',
                    color: detail.state === 'open' ? 'var(--status-success-text)' : '#9ca3af',
                    border: `1px solid ${detail.state === 'open' ? 'var(--status-success-border)' : 'rgba(107, 114, 128, 0.4)'}`,
                  }}
                >
                  {detail.is_pull_request ? (
                    <GitPullRequest className="w-3.5 h-3.5" />
                  ) : (
                    <AlertCircle className="w-3.5 h-3.5" />
                  )}
                  <span style={{ textTransform: 'capitalize' }}>{detail.state}</span>
                </span>

                <span
                  style={{
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.9rem',
                  }}
                >
                  #{detail.number}
                </span>

                <a
                  href={detail.html_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    color: 'var(--accent-blue)',
                    fontSize: '0.8125rem',
                    textDecoration: 'none',
                    marginLeft: 'auto',
                  }}
                >
                  <span>View on GitHub</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <h3
                style={{
                  fontSize: '1.35rem',
                  fontWeight: 700,
                  lineHeight: 1.3,
                  marginBottom: '0.75rem',
                }}
              >
                {detail.title}
              </h3>

              {/* Labels */}
              {detail.labels.length > 0 && (
                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0.375rem',
                    marginBottom: '0.75rem',
                  }}
                >
                  {detail.labels.map((lbl) => (
                    <span
                      key={lbl.id}
                      style={{
                        fontSize: '0.75rem',
                        padding: '0.125rem 0.625rem',
                        borderRadius: '9999px',
                        backgroundColor: `#${lbl.color}22`,
                        color: `#${lbl.color}`,
                        border: `1px solid #${lbl.color}55`,
                        fontWeight: 500,
                      }}
                    >
                      {lbl.name}
                    </span>
                  ))}
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1.25rem',
                  fontSize: '0.8125rem',
                  color: 'var(--text-muted)',
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  {detail.author_avatar_url ? (
                    <img
                      src={detail.author_avatar_url}
                      alt=""
                      style={{ width: '1.25rem', height: '1.25rem', borderRadius: '50%' }}
                    />
                  ) : (
                    <User className="w-3.5 h-3.5" />
                  )}
                  <span>@{detail.author_username || 'ghost'}</span>
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Created {new Date(detail.github_created_at).toLocaleDateString()}</span>
                </span>
              </div>
            </div>
          ) : null}
        </div>

        {/* Modal Scrollable Body */}
        <div style={{ padding: '1.5rem 2rem', overflowY: 'auto', flexGrow: 1 }}>
          {detail && (
            <>
              {/* 1. AI ISSUE COACH SECTION */}
              {analysisObj && (
                <div
                  style={{
                    padding: '1.5rem',
                    background:
                      'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1))',
                    border: '1px solid rgba(139, 92, 246, 0.35)',
                    borderRadius: '0.75rem',
                    marginBottom: '1.75rem',
                  }}
                >
                  {/* Coach Section Title */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '1.25rem',
                      flexWrap: 'wrap',
                      gap: '0.5rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                      <div
                        style={{
                          padding: '0.5rem',
                          background: 'rgba(139, 92, 246, 0.2)',
                          borderRadius: '0.5rem',
                        }}
                      >
                        <GraduationCap className="w-6 h-6 text-purple-400" />
                      </div>
                      <div>
                        <h4
                          style={{
                            fontSize: '1.15rem',
                            fontWeight: 800,
                            color: 'var(--text-primary)',
                          }}
                        >
                          AI Issue Coach
                        </h4>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                          Actionable developer guidance & step-by-step implementation plan
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-muted)',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {analysisObj.model_name} (v{analysisObj.analysis_version})
                      </span>
                    </div>
                  </div>

                  {/* Coaching Overview Grid */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                      gap: '0.75rem',
                      marginBottom: '1.25rem',
                    }}
                  >
                    <div
                      style={{
                        padding: '0.625rem 0.875rem',
                        background: 'rgba(0,0,0,0.35)',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <span
                        style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}
                      >
                        Difficulty
                      </span>
                      <span
                        style={{
                          fontSize: '0.875rem',
                          fontWeight: 700,
                          textTransform: 'capitalize',
                          color: getDifficultyColor(analysisObj.difficulty).text,
                        }}
                      >
                        {analysisObj.difficulty}
                      </span>
                    </div>

                    <div
                      style={{
                        padding: '0.625rem 0.875rem',
                        background: 'rgba(0,0,0,0.35)',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <span
                        style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}
                      >
                        Estimated Effort
                      </span>
                      <span
                        style={{
                          fontSize: '0.875rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                        }}
                      >
                        <Clock className="w-3.5 h-3.5 text-blue-400" />~
                        {analysisObj.estimated_time_minutes} mins
                      </span>
                    </div>

                    <div
                      style={{
                        padding: '0.625rem 0.875rem',
                        background: 'rgba(0,0,0,0.35)',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <span
                        style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}
                      >
                        Learning Time
                      </span>
                      <span
                        style={{
                          fontSize: '0.875rem',
                          fontWeight: 700,
                          color: '#c084fc',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                        }}
                      >
                        <GraduationCap className="w-3.5 h-3.5 text-purple-400" />~
                        {analysisObj.estimated_learning_time || 15} mins
                      </span>
                    </div>

                    <div
                      style={{
                        padding: '0.625rem 0.875rem',
                        background: 'rgba(0,0,0,0.35)',
                        borderRadius: '0.5rem',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <span
                        style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}
                      >
                        Merge Probability
                      </span>
                      <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#34d399' }}>
                        {Math.round(analysisObj.merge_probability * 100)}%
                      </span>
                    </div>
                  </div>

                  {/* Confidence Reasoning Toggle */}
                  <div style={{ marginBottom: '1.25rem' }}>
                    <button
                      onClick={() => setShowConfidenceReasoning(!showConfidenceReasoning)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--accent-blue)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        cursor: 'pointer',
                        padding: 0,
                      }}
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>
                        Why AI assigned {Math.round(analysisObj.ai_confidence * 100)}% confidence
                        score
                      </span>
                      <ChevronDown
                        className={`w-3.5 h-3.5 transition-transform ${showConfidenceReasoning ? 'rotate-180' : ''}`}
                      />
                    </button>
                    {showConfidenceReasoning && (
                      <p
                        style={{
                          marginTop: '0.375rem',
                          fontSize: '0.8125rem',
                          color: 'var(--text-secondary)',
                          background: 'rgba(0,0,0,0.3)',
                          padding: '0.5rem 0.75rem',
                          borderRadius: '0.375rem',
                        }}
                      >
                        {analysisObj.confidence_reasoning ||
                          'Calculated based on issue title clarity, available labels, and matched component schemas.'}
                      </p>
                    )}
                  </div>

                  {/* 1A. Problem Explanation Card */}
                  <div
                    style={{
                      marginBottom: '1.25rem',
                      background: 'rgba(0,0,0,0.3)',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      border: '1px solid rgba(255,255,255,0.08)',
                    }}
                  >
                    <h5
                      style={{
                        fontSize: '0.875rem',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        marginBottom: '0.375rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.375rem',
                      }}
                    >
                      <BrainCircuit className="w-4 h-4 text-purple-400" />
                      Problem Explanation
                    </h5>
                    <p
                      style={{
                        fontSize: '0.875rem',
                        color: 'var(--text-primary)',
                        lineHeight: 1.5,
                      }}
                    >
                      {analysisObj.problem_explanation || analysisObj.summary}
                    </p>
                  </div>

                  {/* 1B. Numbered Implementation Plan Timeline */}
                  {analysisObj.implementation_plan &&
                    analysisObj.implementation_plan.length > 0 && (
                      <div
                        style={{
                          marginBottom: '1.25rem',
                          background: 'rgba(0,0,0,0.3)',
                          padding: '1rem',
                          borderRadius: '0.5rem',
                          border: '1px solid rgba(255,255,255,0.08)',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: '0.875rem',
                          }}
                        >
                          <h5
                            style={{
                              fontSize: '0.875rem',
                              fontWeight: 700,
                              color: 'var(--text-primary)',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.375rem',
                            }}
                          >
                            <ListOrdered className="w-4 h-4 text-blue-400" />
                            Implementation Plan Timeline
                          </h5>
                          <button
                            onClick={handleCopyPlan}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.25rem',
                              padding: '0.25rem 0.5rem',
                              background: 'rgba(255,255,255,0.08)',
                              border: '1px solid var(--border-color)',
                              color: 'var(--text-secondary)',
                              borderRadius: '0.25rem',
                              fontSize: '0.75rem',
                              cursor: 'pointer',
                            }}
                          >
                            {copiedPlan ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                            <span>{copiedPlan ? 'Copied!' : 'Copy Plan'}</span>
                          </button>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                          {analysisObj.implementation_plan.map((step, idx) => (
                            <div
                              key={idx}
                              style={{
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '0.75rem',
                                background: 'rgba(255,255,255,0.02)',
                                padding: '0.625rem 0.875rem',
                                borderRadius: '0.375rem',
                                border: '1px solid rgba(255,255,255,0.05)',
                              }}
                            >
                              <span
                                style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  width: '1.5rem',
                                  height: '1.5rem',
                                  borderRadius: '50%',
                                  background: 'var(--accent-blue)',
                                  color: '#fff',
                                  fontSize: '0.75rem',
                                  fontWeight: 800,
                                  flexShrink: 0,
                                }}
                              >
                                {idx + 1}
                              </span>
                              <span
                                style={{
                                  fontSize: '0.875rem',
                                  color: 'var(--text-primary)',
                                  lineHeight: 1.4,
                                  paddingTop: '0.125rem',
                                }}
                              >
                                {step}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* 1C. Acceptance Criteria Checkboxes */}
                  {analysisObj.acceptance_criteria &&
                    analysisObj.acceptance_criteria.length > 0 && (
                      <div
                        style={{
                          marginBottom: '1.25rem',
                          background: 'rgba(0,0,0,0.3)',
                          padding: '1rem',
                          borderRadius: '0.5rem',
                          border: '1px solid rgba(255,255,255,0.08)',
                        }}
                      >
                        <h5
                          style={{
                            fontSize: '0.875rem',
                            fontWeight: 700,
                            color: 'var(--text-primary)',
                            marginBottom: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.375rem',
                          }}
                        >
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          Acceptance Criteria Checklist
                        </h5>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {analysisObj.acceptance_criteria.map((crit, idx) => (
                            <label
                              key={idx}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.625rem',
                                fontSize: '0.8125rem',
                                color: 'var(--text-primary)',
                                cursor: 'pointer',
                              }}
                            >
                              <input
                                type="checkbox"
                                defaultChecked
                                style={{ accentColor: '#10b981', width: '1rem', height: '1rem' }}
                              />
                              <span>{crit}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* 1D. Required Knowledge & Prerequisites Chips */}
                  {((analysisObj.required_knowledge && analysisObj.required_knowledge.length > 0) ||
                    (analysisObj.prerequisites && analysisObj.prerequisites.length > 0)) && (
                    <div
                      style={{
                        marginBottom: '1.25rem',
                        background: 'rgba(0,0,0,0.3)',
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        border: '1px solid rgba(255,255,255,0.08)',
                      }}
                    >
                      <h5
                        style={{
                          fontSize: '0.875rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          marginBottom: '0.625rem',
                        }}
                      >
                        Required Knowledge & Prerequisites
                      </h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                        {analysisObj.required_knowledge?.map((item, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              padding: '0.25rem 0.625rem',
                              borderRadius: '9999px',
                              background: 'rgba(59, 130, 246, 0.15)',
                              color: '#93c5fd',
                              border: '1px solid rgba(59, 130, 246, 0.3)',
                            }}
                          >
                            📚 {item}
                          </span>
                        ))}
                        {analysisObj.prerequisites?.map((item, idx) => (
                          <span
                            key={`prereq-${idx}`}
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              padding: '0.25rem 0.625rem',
                              borderRadius: '9999px',
                              background: 'rgba(139, 92, 246, 0.15)',
                              color: '#c084fc',
                              border: '1px solid rgba(139, 92, 246, 0.3)',
                            }}
                          >
                            ⚡ {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 1E. Testing Strategy Box */}
                  {analysisObj.testing_strategy && (
                    <div
                      style={{
                        marginBottom: '1.25rem',
                        background: 'rgba(0,0,0,0.3)',
                        padding: '0.875rem 1rem',
                        borderRadius: '0.5rem',
                        border: '1px solid rgba(255,255,255,0.08)',
                      }}
                    >
                      <strong
                        style={{
                          fontSize: '0.8125rem',
                          color: 'var(--text-primary)',
                          display: 'block',
                          marginBottom: '0.25rem',
                        }}
                      >
                        🧪 Testing Strategy:
                      </strong>
                      <p
                        style={{
                          fontSize: '0.8125rem',
                          color: 'var(--text-secondary)',
                          lineHeight: 1.4,
                        }}
                      >
                        {analysisObj.testing_strategy}
                      </p>
                    </div>
                  )}

                  {/* 1F. Possible Challenges Warning Cards */}
                  {analysisObj.possible_challenges &&
                    analysisObj.possible_challenges.length > 0 && (
                      <div
                        style={{
                          background: 'rgba(239, 68, 68, 0.08)',
                          padding: '0.875rem 1rem',
                          borderRadius: '0.5rem',
                          border: '1px solid rgba(239, 68, 68, 0.25)',
                        }}
                      >
                        <strong
                          style={{
                            fontSize: '0.8125rem',
                            color: '#f87171',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.375rem',
                            marginBottom: '0.375rem',
                          }}
                        >
                          <AlertTriangle className="w-4 h-4" /> Potential Pitfalls & Challenges:
                        </strong>
                        <ul
                          style={{
                            margin: 0,
                            paddingLeft: '1.25rem',
                            fontSize: '0.8125rem',
                            color: '#fca5a5',
                            lineHeight: 1.5,
                          }}
                        >
                          {analysisObj.possible_challenges.map((ch, idx) => (
                            <li key={idx}>{ch}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              )}

              {/* 2. Deterministic Rule Score Section */}
              {scoreObj && (
                <div
                  style={{
                    padding: '1.25rem 1.5rem',
                    background: 'rgba(59, 130, 246, 0.08)',
                    border: '1px solid rgba(59, 130, 246, 0.25)',
                    borderRadius: '0.75rem',
                    marginBottom: '1.75rem',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '1rem',
                      flexWrap: 'wrap',
                      gap: '0.5rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Sparkles className="w-5 h-5 text-blue-400" />
                      <h4
                        style={{
                          fontSize: '1.05rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                        }}
                      >
                        Rule-Based Score Explanation
                      </h4>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span
                        style={{
                          fontSize: '1.125rem',
                          fontWeight: 800,
                          color: 'var(--accent-blue)',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {scoreObj.score} pts
                      </span>
                      {getRecommendationBadge(scoreObj.recommendation)}
                    </div>
                  </div>

                  {/* Rule Breakdown List */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {Object.entries(scoreObj.rule_breakdown).map(([ruleKey, delta]) => (
                      <div
                        key={ruleKey}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.5rem 0.75rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          borderRadius: '0.375rem',
                          fontSize: '0.8125rem',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            color: 'var(--text-secondary)',
                          }}
                        >
                          <ChevronRight className="w-3.5 h-3.5 text-muted" />
                          <span>{getRuleLabel(ruleKey)}</span>
                        </div>
                        <span
                          style={{
                            fontWeight: 700,
                            fontFamily: 'var(--font-mono)',
                            color: delta > 0 ? '#34d399' : '#f87171',
                          }}
                        >
                          {delta > 0 ? `+${delta}` : delta} pts
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Issue Description */}
              <div
                style={{
                  padding: '1.25rem',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.75rem',
                  marginBottom: '2rem',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '0.9375rem',
                  lineHeight: 1.6,
                  color: 'var(--text-primary)',
                }}
              >
                {detail.body || <em>No description provided.</em>}
              </div>

              {/* Comments Header */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '1rem',
                }}
              >
                <MessageSquare className="w-4 h-4 text-blue-400" />
                <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>
                  Synchronized Comments ({detail.comments.length})
                </h4>
              </div>

              {/* Comments List */}
              {detail.comments.length === 0 ? (
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                  No comments on this issue yet.
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {detail.comments.map((comment) => (
                    <div
                      key={comment.id}
                      style={{
                        padding: '1rem 1.25rem',
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '0.625rem',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '0.5rem',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            fontSize: '0.8125rem',
                          }}
                        >
                          {comment.author_avatar_url ? (
                            <img
                              src={comment.author_avatar_url}
                              alt=""
                              style={{ width: '1.25rem', height: '1.25rem', borderRadius: '50%' }}
                            />
                          ) : (
                            <User className="w-3.5 h-3.5 text-muted" />
                          )}
                          <strong style={{ color: 'var(--text-primary)' }}>
                            @{comment.author_username || 'ghost'}
                          </strong>
                        </div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {new Date(comment.github_created_at).toLocaleString()}
                        </span>
                      </div>
                      <p
                        style={{
                          fontSize: '0.875rem',
                          color: 'var(--text-secondary)',
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.5,
                        }}
                      >
                        {comment.body}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
