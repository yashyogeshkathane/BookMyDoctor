import apiClient from "./axios";

export const registerUser = async (payload) => {
  const response = await apiClient.post("/auth/register", payload);
  return response.data;
};

export const loginUser = async (payload) => {
  const response = await apiClient.post("/auth/login", payload);
  return response.data;
};

export const verifyEmailToken = async (token) => {
  const response = await apiClient.post("/auth/verify-email", { token });
  return response.data;
};

export const refreshAccessToken = async (refreshToken) => {
  const response = await apiClient.post("/auth/refresh", {
    refresh_token: refreshToken,
  });
  return response.data;
};

export const logoutUser = async (refreshToken) => {
  const response = await apiClient.post("/auth/logout", {
    refresh_token: refreshToken,
  });
  return response.data;
};
