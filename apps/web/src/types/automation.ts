import { Issue } from './issue';
import { Repository } from './repository';

export interface SavedSearch {
  id: string;
  user_id: string;
  name: string;
  search_query: string | null;
  filters_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Bookmark {
  id: string;
  user_id: string;
  issue_id: string;
  notes: string | null;
  created_at: string;
  issue?: Issue | null;
}

export interface NotificationItem {
  id: string;
  user_id: string;
  issue_id: string | null;
  saved_search_id: string | null;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  issue?: Issue | null;
}

export interface SyncJob {
  id: string;
  repository_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  started_at: string | null;
  finished_at: string | null;
  issues_processed: number;
  errors: string | null;
  created_at: string;
  updated_at: string;
  repository?: Repository | null;
}
