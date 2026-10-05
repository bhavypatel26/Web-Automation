export type Workflow = {
  id: string; version: number; name: string; description: string; portal_url: string;
  allowed_hosts: string[]; inputs: {name: string; label: string; kind: 'text' | 'file'; required: boolean; default?: string | null}[];
  steps: {instruction: string; expected_result: string; submits_form: boolean}[];
  completion: string; skill: string; status: string;
  submissions_authorized: boolean;
};
export type Run = {id: string; workflow_id: string; status: string; stage: string; summary: string; files: string[]};
