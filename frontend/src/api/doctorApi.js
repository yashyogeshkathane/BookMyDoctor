import apiClient from "./axios";

export const getDoctorProfile = async () => {
  const response = await apiClient.get("/doctors/me");
  return response.data;
};

export const getDoctorSlots = async ({ date }) => {
  const response = await apiClient.get("/doctors/slots", {
    params: { date },
  });
  return response.data;
};
