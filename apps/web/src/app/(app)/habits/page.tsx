"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { habitsApi, todosApi } from "@/lib/api/habits";
import { CheckSquare, Plus, Flame, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function HabitsPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [newHabit, setNewHabit] = useState("");
  const [newTodo, setNewTodo] = useState("");

  const { data: habits, isLoading: habitsLoading } = useQuery({
    queryKey: ["habits"],
    queryFn: async () => {
      const token = await getToken();
      return habitsApi.list(token!);
    },
  });

  const { data: todos, isLoading: todosLoading } = useQuery({
    queryKey: ["todos", "open"],
    queryFn: async () => {
      const token = await getToken();
      return todosApi.list(token!, "open");
    },
  });

  const createHabitMutation = useMutation({
    mutationFn: async (name: string) => {
      const token = await getToken();
      return habitsApi.create(token!, { name });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      setNewHabit("");
    },
  });

  const checkinMutation = useMutation({
    mutationFn: async (habitId: string) => {
      const token = await getToken();
      return habitsApi.checkin(token!, habitId);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["habits"] }),
  });

  const createTodoMutation = useMutation({
    mutationFn: async (title: string) => {
      const token = await getToken();
      return todosApi.create(token!, { title });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["todos"] });
      setNewTodo("");
    },
  });

  const completeTodoMutation = useMutation({
    mutationFn: async (todoId: string) => {
      const token = await getToken();
      return todosApi.complete(token!, todoId);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["todos"] }),
  });

  return (
    <div className="max-w-2xl space-y-10">
      {/* Habits */}
      <section className="space-y-4">
        <h1 className="text-lg font-semibold">Habits</h1>

        <div className="flex gap-2">
          <input
            value={newHabit}
            onChange={(e) => setNewHabit(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && newHabit && createHabitMutation.mutate(newHabit)}
            placeholder="Add a habit..."
            className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <button
            onClick={() => newHabit && createHabitMutation.mutate(newHabit)}
            disabled={!newHabit || createHabitMutation.isPending}
            className="rounded-md bg-foreground px-3 py-2 text-sm text-background disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {habitsLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : habits?.length === 0 ? (
          <p className="text-sm text-muted-foreground">No habits yet. Add one above.</p>
        ) : (
          <ul className="space-y-2">
            {habits?.map((habit) => (
              <li
                key={habit.id}
                className="flex items-center justify-between rounded-lg border border-border p-4"
              >
                <div className="space-y-0.5">
                  <p className="text-sm font-medium">{habit.name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{habit.cadence}</p>
                </div>
                <button
                  onClick={() => checkinMutation.mutate(habit.id)}
                  disabled={checkinMutation.isPending}
                  className={cn(
                    "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    "bg-accent hover:bg-accent/80"
                  )}
                >
                  <Flame className="h-3.5 w-3.5" />
                  Check in
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Todos */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold">To-dos</h2>

        <div className="flex gap-2">
          <input
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && newTodo && createTodoMutation.mutate(newTodo)}
            placeholder="Add a task..."
            className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <button
            onClick={() => newTodo && createTodoMutation.mutate(newTodo)}
            disabled={!newTodo || createTodoMutation.isPending}
            className="rounded-md bg-foreground px-3 py-2 text-sm text-background disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {todosLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : todos?.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing to do. Add a task above.</p>
        ) : (
          <ul className="space-y-2">
            {todos?.map((todo) => (
              <li key={todo.id} className="flex items-center gap-3">
                <button
                  onClick={() => completeTodoMutation.mutate(todo.id)}
                  className="flex-shrink-0 rounded border border-border p-0.5 hover:bg-accent transition-colors"
                >
                  <CheckSquare className="h-4 w-4 text-muted-foreground" />
                </button>
                <span className="text-sm">{todo.title}</span>
                {todo.priority <= 2 && (
                  <span className="ml-auto text-xs text-orange-400">high</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
