import axios from "axios";

import { loadAuthState } from "../app/auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/",
});

api.interceptors.request.use((config) => {
  const auth = loadAuthState();
  if (auth?.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  if (auth?.workspace?.id) {
    config.headers["X-Workspace-Id"] = auth.workspace.id;
  }
  return config;
});

export async function unwrap<T>(promise: Promise<{ data: { data: T } }>): Promise<T> {
  const response = await promise;
  return response.data.data;
}
