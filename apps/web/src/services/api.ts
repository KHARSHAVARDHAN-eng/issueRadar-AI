import { Bookmark, NotificationItem, SavedSearch, SyncJob } from '../types/automation';
import { SystemHealthResponse } from '../types/health';
import { Issue, IssueAnalysis, IssueDetail, IssueScore } from '../types/issue';
import { Repository } from '../types/repository';
import { User } from '../types/user';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface PaginatedIssuesResponse {
  items: Issue[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface IssueSearchParams {
  search?: string;
  repository_id?: string;
  difficulty?: string;
  risk?: string;
  recommendation?: string;
  min_score?: number;
  max_score?: number;
  min_merge_probability?: number;
  max_estimated_time?: number;
  language?: string;
  label?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export async function fetchHealthStatus(): Promise<SystemHealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) {
    if (response.status === 401) throw new Error('Unauthenticated');
    throw new Error(`Failed to fetch current user (${response.status})`);
  }
  return response.json();
}

export async function logoutUser(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Logout failed');
}

export function getGithubLoginUrl(): string {
  return `${API_BASE_URL}/api/v1/auth/login`;
}

/* Repository API Methods */

export async function fetchRepositories(): Promise<Repository[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch repositories (${response.status})`);
  return response.json();
}

export async function addRepository(urlOrName: string): Promise<Repository> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ url_or_name: urlOrName }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to add repository');
  return data;
}

export async function deleteRepository(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories/${id}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to delete repository');
  }
}

export async function syncRepository(repoId: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories/${repoId}/sync`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to enqueue repository sync');
  return data;
}

export async function rescoreRepository(repoId: string): Promise<{ scored_count: number }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories/${repoId}/score`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to rescore repository');
  return data;
}

export async function analyzeRepository(repoId: string): Promise<{ analyzed_count: number }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories/${repoId}/analyze`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to analyze repository with AI');
  return data;
}

/* Issue Search & Discovery API Methods */

export async function searchIssues(params: IssueSearchParams): Promise<PaginatedIssuesResponse> {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '' && val !== 'all') {
      urlParams.append(key, String(val));
    }
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/issues?${urlParams.toString()}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!response.ok) throw new Error(`Failed to search issues (${response.status})`);
  return response.json();
}

export async function fetchIssueDetail(issueId: string): Promise<IssueDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/issues/${issueId}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch issue details (${response.status})`);
  return response.json();
}

export async function fetchIssueScore(issueId: string): Promise<IssueScore> {
  const response = await fetch(`${API_BASE_URL}/api/v1/issues/${issueId}/score`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch issue score (${response.status})`);
  return response.json();
}

export async function fetchIssueAnalysis(issueId: string): Promise<IssueAnalysis> {
  const response = await fetch(`${API_BASE_URL}/api/v1/issues/${issueId}/analysis`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch issue AI analysis (${response.status})`);
  return response.json();
}

/* Saved Searches API Methods */

export async function fetchSavedSearches(): Promise<SavedSearch[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/saved-searches`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch saved searches (${response.status})`);
  return response.json();
}

export async function createSavedSearch(
  name: string,
  search_query?: string,
  filters_json: Record<string, unknown> = {},
): Promise<SavedSearch> {
  const response = await fetch(`${API_BASE_URL}/api/v1/saved-searches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ name, search_query, filters_json }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to save search');
  return data;
}

export async function deleteSavedSearch(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/saved-searches/${id}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to delete saved search');
}

/* Bookmarks API Methods */

export async function fetchBookmarks(): Promise<Bookmark[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/bookmarks`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch bookmarks (${response.status})`);
  return response.json();
}

export async function addBookmark(issueId: string, notes?: string): Promise<Bookmark> {
  const response = await fetch(`${API_BASE_URL}/api/v1/bookmarks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ issue_id: issueId, notes }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to bookmark issue');
  return data;
}

export async function deleteBookmark(bookmarkIdOrIssueId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/bookmarks/${bookmarkIdOrIssueId}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to remove bookmark');
}

/* Notifications API Methods */

export async function fetchNotifications(unreadOnly: boolean = false): Promise<NotificationItem[]> {
  const params = unreadOnly ? '?unread_only=true' : '';
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications${params}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch notifications (${response.status})`);
  return response.json();
}

export async function markNotificationRead(id: string): Promise<NotificationItem> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications/${id}/read`, {
    method: 'PUT',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to mark notification as read');
  return response.json();
}

export async function markAllNotificationsRead(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications/read-all`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to mark all notifications as read');
}

export async function deleteNotification(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications/${id}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to delete notification');
}

/* Jobs API Methods */

export async function fetchSyncJobs(): Promise<SyncJob[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/jobs`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error(`Failed to fetch sync jobs (${response.status})`);
  return response.json();
}

export async function retrySyncJob(jobId: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}/retry`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Failed to retry sync job');
  return data;
}
