export interface Label {
  id: string;
  github_id: number | null;
  name: string;
  color: string;
  description: string | null;
}

export interface Comment {
  id: string;
  github_id: number;
  body: string;
  author_username: string | null;
  author_avatar_url: string | null;
  github_created_at: string;
}

export interface IssueScore {
  id: string;
  issue_id: string;
  score: number;
  recommendation: 'Implement' | 'Investigate' | 'Skip';
  rule_breakdown: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface IssueAnalysis {
  id: string;
  issue_id: string;
  summary: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_time_minutes: number;
  risk: 'low' | 'medium' | 'high';
  component: string;
  languages: string[];
  likely_files: string[];
  merge_probability: number;
  ai_confidence: number;
  model_name: string;
  analysis_version: string;
  analyzed_at: string;

  // AI Coach Extensions
  problem_explanation: string;
  implementation_plan: string[];
  required_knowledge: string[];
  prerequisites: string[];
  acceptance_criteria: string[];
  testing_strategy: string;
  possible_challenges: string[];
  estimated_learning_time: number;
  confidence_reasoning: string;
}

export interface Issue {
  id: string;
  github_id: number;
  number: number;
  title: string;
  body: string | null;
  state: 'open' | 'closed';
  author_username: string | null;
  author_avatar_url: string | null;
  html_url: string;
  comments_count: number;
  is_pull_request: boolean;
  repository_id: string;
  labels: Label[];
  score?: IssueScore | null;
  analysis?: IssueAnalysis | null;
  github_created_at: string;
  github_updated_at: string;
  github_closed_at: string | null;
}

export interface IssueDetail extends Issue {
  comments: Comment[];
}
