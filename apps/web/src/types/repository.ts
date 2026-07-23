export interface Repository {
  id: string;
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  default_branch: string;
  stars: number;
  forks: number;
  private: boolean;
  added_by_id: string;

  // Sync Tracking Fields
  last_sync_started_at: string | null;
  last_sync_completed_at: string | null;
  sync_status: string;
  sync_error: string | null;
  open_issues_count: number;
  closed_issues_count: number;
  total_issues_count: number;

  created_at: string;
  updated_at: string;
}

export interface RepositoryCreateInput {
  url_or_name: string;
}
