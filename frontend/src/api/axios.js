import axios from "axios";

const ACCESS_TOKEN_KEY = "cms_access_token";
const REFRESH_TOKEN_KEY = "cms_refresh_token";
const AUTH_USER_KEY = "cms_auth_user";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  // ❌ REMOVE default Content-Type
});

apiClient.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  // 🔥 IMPORTANT: Let axios handle FormData automatically
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

    if (
      error.response?.status !== 401 ||
      !refreshToken ||
      originalRequest?._retry ||
      originalRequest?.url?.includes("/auth/login") ||
      originalRequest?.url?.includes("/auth/register") ||
      originalRequest?.url?.includes("/auth/verify-email") ||
      originalRequest?.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const refreshResponse = await axios.post(
        `${apiClient.defaults.baseURL}/auth/refresh`,
        { refresh_token: refreshToken },
        {
          headers: {
            "Content-Type": "application/json", // ✅ OK here (JSON request)
          },
        }
      );

      const {
        access_token: newAccessToken,
        refresh_token: newRefreshToken,
        user,
      } = refreshResponse.data;

      localStorage.setItem(ACCESS_TOKEN_KEY, newAccessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));

      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

      return apiClient(originalRequest);
    } catch (refreshError) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(AUTH_USER_KEY);

      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;