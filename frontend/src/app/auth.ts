export type UserSummary = {
  id: string;
  username: string;
  email: string;
  isSystemAdmin: boolean;
};

export type WorkspaceSummary = {
  id: string;
  name: string;
  role: string;
};

export type AuthState = {
  accessToken: string;
  user: UserSummary;
  workspace: WorkspaceSummary | null;
};

const STORAGE_KEY = "shangtugongfang.auth";
let memoryValue: string | null = null;

function getStorage() {
  const storage = globalThis.localStorage as Storage | undefined;
  if (storage && typeof storage.getItem === "function" && typeof storage.setItem === "function") {
    return storage;
  }
  return {
    getItem: () => memoryValue,
    setItem: (_key: string, value: string) => {
      memoryValue = value;
    },
    removeItem: () => {
      memoryValue = null;
    },
  };
}

export function saveAuthState(state: AuthState): void {
  getStorage().setItem(STORAGE_KEY, JSON.stringify(state));
}

export function loadAuthState(): AuthState | null {
  const raw = getStorage().getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  return JSON.parse(raw) as AuthState;
}

export function clearAuthState(): void {
  getStorage().removeItem(STORAGE_KEY);
}
