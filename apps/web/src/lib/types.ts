export type Classification = {
  id: number;
  question_id: number;
  area: string;
  subarea: string | null;
  topic: string | null;
  subtopic: string | null;
  competence: string | null;
  skill: string | null;
  difficulty: number;
  requires_formula: boolean;
  requires_graph: boolean;
  requires_colombia_context: boolean;
  concepts_json: string[];
  keywords_json: string[];
  likely_error_types_json: string[];
  confidence: number;
  classified_by: string;
  created_at: string;
};

export type Question = {
  id: number;
  document_id: number | null;
  external_id: string | null;
  year: number | null;
  area: string;
  question_number: number | null;
  statement: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: "A" | "B" | "C" | "D";
  explanation: string | null;
  source_file: string | null;
  page: number | null;
  raw_text: string | null;
  is_invalid: boolean;
  is_incomplete: boolean;
  created_at: string;
  updated_at: string;
  classification: Classification | null;
};

export type Overview = {
  total_questions: number;
  answered_questions: number;
  total_attempts: number;
  global_accuracy: number;
  due_review_count: number;
  imported_documents: number;
  ai_configured: boolean;
  embeddings_enabled: boolean;
  recommendation_today: string;
};

export type AreaAnalytics = {
  area: string;
  total_questions: number;
  attempts: number;
  correct_attempts: number;
  accuracy: number;
};

export type TopicPriority = {
  area: string;
  topic: string;
  total_questions: number;
  recent_questions: number;
  attempts: number;
  correct_attempts: number;
  error_rate: number;
  avg_confidence: number | null;
  avg_time_seconds: number | null;
  frequency_score: number;
  recent_score: number;
  low_confidence_score: number;
  strategic_area_weight: number;
  mastery_score: number;
  priority_score: number;
  interpretation: string;
};

export type Attempt = {
  id: number;
  question_id: number;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  confidence: number;
  time_seconds: number | null;
  error_type: string | null;
  notes: string | null;
  attempted_at: string;
  review_after: string | null;
};

export type DocumentSource = {
  id: number;
  filename: string;
  source_type: string;
  year: number | null;
  area: string | null;
  official_status: string | null;
  imported_at: string;
  metadata_json: Record<string, unknown>;
};

export type DailyPlan = {
  id: number | null;
  plan_date: string;
  available_minutes: number;
  generated_at: string | null;
  plan_json: {
    blocks: Array<{
      block: number;
      minutes: number;
      area: string;
      topic: string;
      activity: string;
      suggested_questions: number;
      review_question_ids: number[];
      reason: string;
    }>;
    due_review_question_ids: number[];
    preference: string;
    phase: string;
  };
};
