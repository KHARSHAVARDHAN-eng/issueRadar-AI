export interface User {
  id: string;
  github_id: number;
  username: string;
  email: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}
