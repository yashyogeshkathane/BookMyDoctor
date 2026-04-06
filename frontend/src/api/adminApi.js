import apiClient from "./axios";

export const getPendingDoctors = async ({ page, pageSize }) => {
  const response = await apiClient.get("/admins/doctors/pending", {
    params: {
      page,
      page_size: pageSize,
    },
  });
  return response.data;
};

export const approveDoctor = async (userId) => {
  const response = await apiClient.post(`/admins/doctors/${userId}/approve`);
  return response.data;
};
