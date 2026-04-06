export function getUserFacingApiError(error, fallbackMessage) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status && status >= 500) {
    return fallbackMessage;
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return fallbackMessage;
}
