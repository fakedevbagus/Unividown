export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'paused' | 'cancelled';

export interface DownloadJobInfo {
  id: number;
  url: string;
  platform?: string | null;
  title?: string | null;
  thumbnail_url?: string | null;
  status: JobStatus;
  progress: number;
  priority?: number;
  quality?: string | null;
  bitrate?: number | null;
  error_message?: string | null;
  created_at?: string;
}

export interface ProcessingJobInfo {
  id: number;
  tool_type: 'convert' | 'trim' | 'compress' | 'merge';
  status: JobStatus;
  progress: number;
  input_files: string[];
  output_files?: string[] | null;
  parameters?: Record<string, unknown>;
  error_message?: string | null;
  created_at?: string;
}
