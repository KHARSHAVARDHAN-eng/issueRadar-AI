import React, { useEffect, useState } from 'react';
import { IssueDetailModal } from '../components/IssueDetailModal';
import { IssueSkeleton } from '../components/IssueSkeleton';
import { useAuth } from '../hooks/useAuth';
import { useDebounce } from '../hooks/useDebounce';
import {
  analyzeRepository,
  fetchRepositories,
  rescoreRepository,
  searchIssues,
} from '../services/api';
import { Issue } from '../types/issue';
import { Repository } from '../types/repository';
import {
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FolderGit2,
  GitPullRequest,
  LayoutDashboard,
  ListTodo,
  LogOut,
  MessageSquare,
  Search,
  Sparkles,
  SlidersHorizontal,
  X,
  Zap,
} from 'lucide-react';

interface IssuesPageProps {
  onNavigateToDashboard: () => void;
  onNavigateToRepositories: () => void;
}

export const IssuesPage: React.FC<IssuesPageProps> = ({
  onNavigateToDashboard,
  onNavigateToRepositories,
}) => {
  const { user, logout } = useAuth();
  const [repositories, setRepositories] = useState<Repository[]>([]);

  // Raw Search Input & Debounced Search Input
  const [searchInput, setSearchInput] = useState<string>('');
  const debouncedSearch = useDebounce(searchInput, 300);

  // Filters State
  const [repoId, setRepoId] = useState<string>('all');
  const [difficulty, setDifficulty] = useState<string>('all');
  const [risk, setRisk] = useState<string>('all');
  const [recommendation, setRecommendation] = useState<string>('all');
  const [minScore, setMinScore] = useState<string>('all');
  const [minMergeProb, setMinMergeProb] = useState<string>('all');
  const [maxTime, setMaxTime] = useState<string>('all');
  const [language, setLanguage] = useState<string>('');
  const [label, setLabel] = useState<string>('');
  const [sort, setSort] = useState<string>('score_desc');
  const [page, setPage] = useState<number>(1);
  const pageSize = 20;

  // Response Data State
  const [issues, setIssues] = useState<Issue[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [pages, setPages] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [rescoring, setRescoring] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  // 1. Read URL Search Parameters on initial mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.has('search')) setSearchInput(params.get('search') || '');
    if (params.has('repository_id')) setRepoId(params.get('repository_id') || 'all');
    if (params.has('difficulty')) setDifficulty(params.get('difficulty') || 'all');
    if (params.has('risk')) setRisk(params.get('risk') || 'all');
    if (params.has('recommendation')) setRecommendation(params.get('recommendation') || 'all');
    if (params.has('min_score')) setMinScore(params.get('min_score') || 'all');
    if (params.has('min_merge_probability'))
      setMinMergeProb(params.get('min_merge_probability') || 'all');
    if (params.has('max_estimated_time')) setMaxTime(params.get('max_estimated_time') || 'all');
    if (params.has('language')) setLanguage(params.get('language') || '');
    if (params.has('label')) setLabel(params.get('label') || '');
    if (params.has('sort')) setSort(params.get('sort') || 'score_desc');
    if (params.has('page')) setPage(parseInt(params.get('page') || '1', 10));
  }, []);

  // 2. Fetch monitored repositories list
  useEffect(() => {
    const loadRepos = async () => {
      try {
        const repos = await fetchRepositories();
        setRepositories(repos);
      } catch (err) {
        console.error('Failed to fetch repositories:', err);
      }
    };
    loadRepos();
  }, []);

  // 3. Search Execution & URL State Synchronization
  const executeSearch = React.useCallback(async () => {
    setLoading(true);
    setError(null);

    // Build URL search params
    const urlParams = new URLSearchParams();
    if (debouncedSearch) urlParams.set('search', debouncedSearch);
    if (repoId !== 'all') urlParams.set('repository_id', repoId);
    if (difficulty !== 'all') urlParams.set('difficulty', difficulty);
    if (risk !== 'all') urlParams.set('risk', risk);
    if (recommendation !== 'all') urlParams.set('recommendation', recommendation);
    if (minScore !== 'all') urlParams.set('min_score', minScore);
    if (minMergeProb !== 'all') urlParams.set('min_merge_probability', minMergeProb);
    if (maxTime !== 'all') urlParams.set('max_estimated_time', maxTime);
    if (language) urlParams.set('language', language);
    if (label) urlParams.set('label', label);
    if (sort !== 'score_desc') urlParams.set('sort', sort);
    if (page > 1) urlParams.set('page', String(page));

    // Update browser URL without reloading page
    const newUrl = `${window.location.pathname}${urlParams.toString() ? `?${urlParams.toString()}` : ''}`;
    window.history.replaceState(null, '', newUrl);

    try {
      const res = await searchIssues({
        search: debouncedSearch,
        repository_id: repoId === 'all' ? undefined : repoId,
        difficulty: difficulty === 'all' ? undefined : difficulty,
        risk: risk === 'all' ? undefined : risk,
        recommendation: recommendation === 'all' ? undefined : recommendation,
        min_score: minScore === 'all' ? undefined : parseFloat(minScore),
        min_merge_probability: minMergeProb === 'all' ? undefined : parseFloat(minMergeProb),
        max_estimated_time: maxTime === 'all' ? undefined : parseInt(maxTime, 10),
        language: language || undefined,
        label: label || undefined,
        sort,
        page,
        page_size: pageSize,
      });

      setIssues(res.items);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search issues');
    } finally {
      setLoading(false);
    }
  }, [
    debouncedSearch,
    repoId,
    difficulty,
    risk,
    recommendation,
    minScore,
    minMergeProb,
    maxTime,
    language,
    label,
    sort,
    page,
  ]);

  useEffect(() => {
    executeSearch();
  }, [executeSearch]);

  const clearAllFilters = () => {
    setSearchInput('');
    setRepoId('all');
    setDifficulty('all');
    setRisk('all');
    setRecommendation('all');
    setMinScore('all');
    setMinMergeProb('all');
    setMaxTime('all');
    setLanguage('');
    setLabel('');
    setSort('score_desc');
    setPage(1);
  };

  const handleRescore = async () => {
    if (repoId === 'all') return;
    setRescoring(true);
    try {
      await rescoreRepository(repoId);
      await executeSearch();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to rescore repository');
    } finally {
      setRescoring(false);
    }
  };

  const handleAIAnalyze = async () => {
    if (repoId === 'all') return;
    setAnalyzing(true);
    try {
      await analyzeRepository(repoId);
      await executeSearch();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to run AI analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRecommendationBadge = (rec?: string) => {
    if (!rec) return null;
    switch (rec) {
      case 'Implement':
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          >
            🟢 Implement
          </span>
        );
      case 'Investigate':
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(245, 158, 11, 0.15)',
              color: '#fbbf24',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          >
            🟡 Investigate
          </span>
        );
      default:
        return (
          <span
            style={{
              padding: '0.125rem 0.5rem',
              borderRadius: '9999px',
              background: 'rgba(239, 68, 68, 0.15)',
              color: '#f87171',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          >
            🔴 Skip
          </span>
        );
    }
  };

  const hasActiveFilters =
    debouncedSearch ||
    repoId !== 'all' ||
    difficulty !== 'all' ||
    risk !== 'all' ||
    recommendation !== 'all' ||
    minScore !== 'all' ||
    minMergeProb !== 'all' ||
    maxTime !== 'all' ||
    language ||
    label;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div className="brand">
            <div className="brand-icon">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <h1 className="brand-title">IssueRadar AI</h1>
          </div>

          <nav style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={onNavigateToDashboard}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={onNavigateToRepositories}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <FolderGit2 className="w-4 h-4" />
              <span>Repositories</span>
            </button>

            <button
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.875rem',
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#93c5fd',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <ListTodo className="w-4 h-4" />
              <span>Smart Search</span>
            </button>
          </nav>
        </div>

        {/* User Profile & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {user?.avatar_url && (
            <img
              src={user.avatar_url}
              alt={user.username}
              style={{ width: '2.25rem', height: '2.25rem', borderRadius: '50%' }}
            />
          )}
          <button
            onClick={logout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.4rem 0.75rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              color: '#f87171',
              borderRadius: '0.5rem',
              fontSize: '0.8125rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Hero Header */}
      <section style={{ marginBottom: '1.5rem' }}>
        <h2 className="hero-title" style={{ textAlign: 'left', fontSize: '2.25rem' }}>
          Smart <span>Issue Discovery</span>
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          Search across open-source issues with live debounced search, rule score filters, and AI
          insights.
        </p>
      </section>

      {/* Top Debounced Live Search Bar */}
      <div
        className="card"
        style={{
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
        }}
      >
        <div style={{ position: 'relative', flexGrow: 1 }}>
          <Search
            className="w-5 h-5 text-blue-400"
            style={{
              position: 'absolute',
              left: '1rem',
              top: '50%',
              transform: 'translateY(-50%)',
            }}
          />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              setPage(1);
            }}
            placeholder="Live search by issue title or body content..."
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 2.75rem',
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.5rem',
              color: 'var(--text-primary)',
              fontSize: '0.9375rem',
              outline: 'none',
            }}
          />
          {searchInput && (
            <button
              onClick={() => setSearchInput('')}
              style={{
                position: 'absolute',
                right: '0.875rem',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Sort Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Sort:</span>
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              setPage(1);
            }}
            style={{
              padding: '0.625rem 0.875rem',
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.5rem',
              color: 'var(--text-primary)',
              fontSize: '0.8125rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="score_desc">Highest Rule Score</option>
            <option value="score_asc">Lowest Rule Score</option>
            <option value="merge_desc">Highest Merge Probability</option>
            <option value="difficulty">Easiest Difficulty</option>
            <option value="estimated_time">Shortest Est Time</option>
            <option value="created_desc">Newest Created</option>
            <option value="created_asc">Oldest Created</option>
            <option value="updated_desc">Recently Updated</option>
          </select>
        </div>
      </div>

      {/* Active Filter Chips Bar */}
      {hasActiveFilters && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            flexWrap: 'wrap',
            marginBottom: '1.5rem',
            padding: '0.75rem 1rem',
            background: 'rgba(59, 130, 246, 0.08)',
            borderRadius: '0.5rem',
            border: '1px solid rgba(59, 130, 246, 0.2)',
          }}
        >
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-blue)' }}>
            Active Filters:
          </span>

          {debouncedSearch && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Search: "{debouncedSearch}"{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setSearchInput('')} />
            </span>
          )}

          {repoId !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Repo: {repositories.find((r) => r.id === repoId)?.name || '1 Selected'}{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setRepoId('all')} />
            </span>
          )}

          {difficulty !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Difficulty: {difficulty}{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setDifficulty('all')} />
            </span>
          )}

          {recommendation !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Rec: {recommendation}{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setRecommendation('all')} />
            </span>
          )}

          {minScore !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Min Score: {minScore}+{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setMinScore('all')} />
            </span>
          )}

          {minMergeProb !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Merge Prob: ≥{Math.round(parseFloat(minMergeProb) * 100)}%{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setMinMergeProb('all')} />
            </span>
          )}

          {maxTime !== 'all' && (
            <span
              className="status-pill"
              style={{ background: 'rgba(0, 0, 0, 0.4)', color: 'var(--text-primary)' }}
            >
              Time: ≤{maxTime}m{' '}
              <X className="w-3 h-3 cursor-pointer" onClick={() => setMaxTime('all')} />
            </span>
          )}

          <button
            onClick={clearAllFilters}
            style={{
              marginLeft: 'auto',
              background: 'none',
              border: 'none',
              color: '#f87171',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Clear All
          </button>
        </div>
      )}

      {/* Main Grid: Sidebar Filters (Left) + Search Results (Right) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '260px 1fr',
          gap: '1.5rem',
          alignItems: 'start',
        }}
      >
        {/* Sidebar Filters Column */}
        <aside
          className="card"
          style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <SlidersHorizontal className="w-4 h-4 text-blue-400" />
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>Filters</h4>
            </div>
            <button
              onClick={clearAllFilters}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                fontSize: '0.75rem',
                cursor: 'pointer',
              }}
            >
              Reset
            </button>
          </div>

          {/* 1. Repository Filter */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              Repository
            </label>
            <select
              value={repoId}
              onChange={(e) => {
                setRepoId(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">All Repositories ({repositories.length})</option>
              {repositories.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>

          {/* 2. Recommendation Filter */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              Recommendation
            </label>
            <select
              value={recommendation}
              onChange={(e) => {
                setRecommendation(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">All Recommendations</option>
              <option value="Implement">🟢 Implement (Score ≥ 50)</option>
              <option value="Investigate">🟡 Investigate (20 - 49)</option>
              <option value="Skip">🔴 Skip (Score &lt; 20)</option>
            </select>
          </div>

          {/* 3. AI Difficulty */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              AI Difficulty
            </label>
            <select
              value={difficulty}
              onChange={(e) => {
                setDifficulty(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">All Difficulties</option>
              <option value="beginner">Beginner (~30m)</option>
              <option value="intermediate">Intermediate (~60m)</option>
              <option value="advanced">Advanced (~180m)</option>
            </select>
          </div>

          {/* 4. Minimum Score */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              Minimum Rule Score
            </label>
            <select
              value={minScore}
              onChange={(e) => {
                setMinScore(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">Any Score</option>
              <option value="20">≥ 20 pts</option>
              <option value="50">≥ 50 pts (High)</option>
              <option value="75">≥ 75 pts (Top Target)</option>
            </select>
          </div>

          {/* 5. Merge Probability */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              Merge Probability
            </label>
            <select
              value={minMergeProb}
              onChange={(e) => {
                setMinMergeProb(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">Any Probability</option>
              <option value="0.5">≥ 50% High Likelihood</option>
              <option value="0.75">≥ 75% Very High Likelihood</option>
              <option value="0.9">≥ 90% Almost Guaranteed</option>
            </select>
          </div>

          {/* 6. Max Estimated Time */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '0.375rem',
              }}
            >
              Max Estimated Time
            </label>
            <select
              value={maxTime}
              onChange={(e) => {
                setMaxTime(e.target.value);
                setPage(1);
              }}
              style={{
                width: '100%',
                padding: '0.5rem',
                backgroundColor: 'rgba(0,0,0,0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.375rem',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
              }}
            >
              <option value="all">Any Duration</option>
              <option value="30">≤ 30 Minutes (Quick Win)</option>
              <option value="60">≤ 1 Hour</option>
              <option value="120">≤ 2 Hours</option>
            </select>
          </div>

          {/* Action Buttons for Rescoring/AI */}
          {repoId !== 'all' && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
                paddingTop: '0.5rem',
                borderTop: '1px solid var(--border-color)',
              }}
            >
              <button
                onClick={handleRescore}
                disabled={rescoring}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.375rem',
                  padding: '0.5rem',
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  color: '#93c5fd',
                  borderRadius: '0.375rem',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Sparkles className={`w-3.5 h-3.5 ${rescoring ? 'animate-spin' : ''}`} />
                <span>Rescore Repo</span>
              </button>

              <button
                onClick={handleAIAnalyze}
                disabled={analyzing}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.375rem',
                  padding: '0.5rem',
                  background: 'rgba(139, 92, 246, 0.15)',
                  border: '1px solid rgba(139, 92, 246, 0.3)',
                  color: '#c084fc',
                  borderRadius: '0.375rem',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <BrainCircuit className={`w-3.5 h-3.5 ${analyzing ? 'animate-spin' : ''}`} />
                <span>AI Analyze Repo</span>
              </button>
            </div>
          )}
        </aside>

        {/* Search Results Column */}
        <main>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
              <IssueSkeleton />
              <IssueSkeleton />
              <IssueSkeleton />
            </div>
          ) : error ? (
            <div
              className="card"
              style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}
            >
              <AlertCircle className="w-8 h-8" style={{ margin: '0 auto 1rem auto' }} />
              <p>{error}</p>
            </div>
          ) : issues.length === 0 ? (
            /* No Results Illustration */
            <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
              <Search className="w-10 h-10 text-muted" style={{ margin: '0 auto 1.25rem auto' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                No Issues Matched Your Query
              </h3>
              <p
                style={{
                  color: 'var(--text-secondary)',
                  maxWidth: '420px',
                  margin: '0 auto 1.5rem auto',
                  fontSize: '0.875rem',
                }}
              >
                We couldn't find any issues matching your active search terms and sidebar filters.
              </p>
              <button
                onClick={clearAllFilters}
                style={{
                  padding: '0.5rem 1.25rem',
                  background: 'var(--accent-blue)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Clear All Filters
              </button>
            </div>
          ) : (
            <>
              {/* Results Items List */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.875rem',
                  marginBottom: '1.5rem',
                }}
              >
                {issues.map((issue) => (
                  <div
                    key={issue.id}
                    className="card"
                    style={{
                      padding: '1.25rem 1.5rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '1rem',
                    }}
                    onClick={() => setSelectedIssueId(issue.id)}
                  >
                    {/* Left Group */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '1rem',
                        flexGrow: 1,
                      }}
                    >
                      <div style={{ marginTop: '0.25rem' }}>
                        {issue.is_pull_request ? (
                          <GitPullRequest className="w-5 h-5 text-purple-400" />
                        ) : issue.state === 'open' ? (
                          <AlertCircle className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <CheckCircle2 className="w-5 h-5 text-gray-500" />
                        )}
                      </div>

                      <div style={{ flexGrow: 1 }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.625rem',
                            marginBottom: '0.375rem',
                            flexWrap: 'wrap',
                          }}
                        >
                          {/* Score Tag */}
                          {issue.score && (
                            <span
                              style={{
                                fontSize: '0.75rem',
                                fontWeight: 800,
                                fontFamily: 'var(--font-mono)',
                                padding: '0.125rem 0.5rem',
                                borderRadius: '0.375rem',
                                background: 'rgba(59, 130, 246, 0.15)',
                                color: '#60a5fa',
                                border: '1px solid rgba(59, 130, 246, 0.3)',
                              }}
                            >
                              {issue.score.score} pts
                            </span>
                          )}

                          {getRecommendationBadge(issue.score?.recommendation)}

                          {/* AI Difficulty Badge */}
                          {issue.analysis && (
                            <span
                              style={{
                                fontSize: '0.7rem',
                                fontWeight: 600,
                                padding: '0.125rem 0.5rem',
                                borderRadius: '9999px',
                                background: 'rgba(139, 92, 246, 0.15)',
                                color: '#c084fc',
                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                textTransform: 'capitalize',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                              }}
                            >
                              <BrainCircuit className="w-3 h-3" />
                              {issue.analysis.difficulty} (~{issue.analysis.estimated_time_minutes}
                              m)
                            </span>
                          )}

                          <span
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: '0.875rem',
                              color: 'var(--text-muted)',
                            }}
                          >
                            #{issue.number}
                          </span>

                          <h4
                            style={{
                              fontSize: '1.05rem',
                              fontWeight: 600,
                              color: 'var(--text-primary)',
                              lineHeight: 1.3,
                            }}
                          >
                            {issue.title}
                          </h4>
                        </div>

                        {/* Labels & Meta */}
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            flexWrap: 'wrap',
                            marginTop: '0.5rem',
                          }}
                        >
                          {issue.labels.map((lbl) => (
                            <span
                              key={lbl.id}
                              style={{
                                fontSize: '0.75rem',
                                padding: '0.125rem 0.5rem',
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

                          <span
                            style={{
                              fontSize: '0.8125rem',
                              color: 'var(--text-muted)',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.375rem',
                            }}
                          >
                            {issue.author_avatar_url && (
                              <img
                                src={issue.author_avatar_url}
                                alt=""
                                style={{
                                  width: '1.125rem',
                                  height: '1.125rem',
                                  borderRadius: '50%',
                                }}
                              />
                            )}
                            <span>@{issue.author_username || 'ghost'}</span>
                          </span>

                          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                            Updated {new Date(issue.github_updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Right Comments Badge */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.375rem',
                        color: 'var(--text-muted)',
                        fontSize: '0.875rem',
                        flexShrink: 0,
                      }}
                    >
                      <MessageSquare className="w-4 h-4" />
                      <span>{issue.comments_count}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination Controls */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '1rem',
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border-color)',
                }}
              >
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                  Page <strong>{page}</strong> of <strong>{pages}</strong> ({total} total issues)
                </span>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      padding: '0.375rem 0.75rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      borderRadius: '0.375rem',
                      fontSize: '0.8125rem',
                      cursor: page <= 1 ? 'not-allowed' : 'pointer',
                      opacity: page <= 1 ? 0.5 : 1,
                    }}
                  >
                    <ChevronLeft className="w-4 h-4" /> Previous
                  </button>

                  <button
                    onClick={() => setPage((p) => Math.min(pages, p + 1))}
                    disabled={page >= pages}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      padding: '0.375rem 0.75rem',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-primary)',
                      borderRadius: '0.375rem',
                      fontSize: '0.8125rem',
                      cursor: page >= pages ? 'not-allowed' : 'pointer',
                      opacity: page >= pages ? 0.5 : 1,
                    }}
                  >
                    Next <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </main>
      </div>

      {/* Issue Detail Modal */}
      <IssueDetailModal issueId={selectedIssueId} onClose={() => setSelectedIssueId(null)} />
    </div>
  );
};
