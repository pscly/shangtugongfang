import { describe, expect, it } from "vitest";

import { loadAuthState, saveAuthState } from "./auth";

describe("auth storage", () => {
  it("应该持久化 token、用户和工作区信息", () => {
    const payload = {
      accessToken: "token-1",
      user: { id: "u1", username: "alice", email: "alice@example.com", isSystemAdmin: false },
      workspace: { id: "w1", name: "测试工作区", role: "owner" },
    };

    saveAuthState(payload);

    expect(loadAuthState()).toEqual(payload);
  });
});
