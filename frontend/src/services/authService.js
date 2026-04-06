import {
  loginUser,
  logoutUser,
  refreshAccessToken,
  registerUser,
  verifyEmailToken,
} from "../api/authApi";

const ACCESS_TOKEN_KEY = "cms_access_token";
const REFRESH_TOKEN_KEY = "cms_refresh_token";
const AUTH_USER_KEY = "cms_auth_user";

export const authService = {
  async register(payload) {
    return registerUser(payload);
  },

  async login(payload) {
    const data = await loginUser(payload);
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user));
    return data;
  },

  async refresh() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      throw new Error("Missing refresh token.");
    }

    const data = await refreshAccessToken(refreshToken);
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user));
    return data;
  },

  async verifyEmail(token) {
    return verifyEmailToken(token);
  },

  async logout() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      try {
        await logoutUser(refreshToken);
      } catch (_) {
        // Clear local session even if the server-side logout request fails.
      }
    }

    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  },

  getToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  getStoredUser() {
    const rawUser = localStorage.getItem(AUTH_USER_KEY);
    return rawUser ? JSON.parse(rawUser) : null;
  },
};
