import { apiRequest } from "../api-client";

export type Habit = {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  cadence: string;
  target_per_period: number;
  created_at: string;
};

export type Checkin = {
  id: string;
  habit_id: string;
  user_id: string;
  occurred_on: string;
  count: number;
  created_at: string;
};

export type Todo = {
  id: string;
  user_id: string;
  title: string;
  body_md: string | null;
  due_at: string | null;
  priority: number;
  status: string;
  completed_at: string | null;
  created_at: string;
};

export type Streak = { current: number; longest: number };
export type HeatmapEntry = { date: string; count: number };

export const habitsApi = {
  list: (token: string) =>
    apiRequest<Habit[]>("/v1/habits", { token }),

  create: (token: string, body: { name: string; description?: string; cadence?: string; target_per_period?: number }) =>
    apiRequest<Habit>("/v1/habits", { method: "POST", body, token }),

  getStreak: (token: string, habitId: string) =>
    apiRequest<Streak>(`/v1/habits/${habitId}/streak`, { token }),

  getHeatmap: (token: string, year: number) =>
    apiRequest<HeatmapEntry[]>(`/v1/habits/heatmap?year=${year}`, { token }),

  checkin: (token: string, habitId: string, note?: string) =>
    apiRequest<Checkin>("/v1/habits/checkins", { method: "POST", body: { habit_id: habitId, note }, token }),
};

export const todosApi = {
  list: (token: string, status?: string) =>
    apiRequest<Todo[]>(`/v1/todos${status ? `?status=${status}` : ""}`, { token }),

  create: (token: string, body: { title: string; body_md?: string; due_at?: string; priority?: number }) =>
    apiRequest<Todo>("/v1/todos", { method: "POST", body, token }),

  complete: (token: string, todoId: string) =>
    apiRequest<void>(`/v1/todos/${todoId}/complete`, { method: "POST", token }),
};
