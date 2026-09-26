export interface PollOption {
  id: number;
  text: string;
}

export interface Poll {
  id: number;
  question: string;
  created_at: string;
  options: PollOption[];
}

export interface PollInput {
  question: string;
  options: string[];
}
