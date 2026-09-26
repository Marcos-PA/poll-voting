import type { Poll, PollInput } from "../types/poll";
import { api } from "./api";

export async function listPolls(): Promise<Poll[]> {
  const { data } = await api.get<Poll[]>("/polls");
  return data;
}

export async function getPoll(id: number): Promise<Poll> {
  const { data } = await api.get<Poll>(`/polls/${id}`);
  return data;
}

export async function createPoll(poll: PollInput): Promise<Poll> {
  const { data } = await api.post<Poll>("/polls", poll);
  return data;
}
