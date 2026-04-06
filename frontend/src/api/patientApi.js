import apiClient from "./axios";

export const getAvailableDoctors = async ({ page, pageSize }) => {
  const response = await apiClient.get("/patients/doctors", {
    params: {
      page,
      page_size: pageSize,
    },
  });
  return response.data;
};

export const getDoctorSlots = async ({ doctorId, date }) => {
  const response = await apiClient.get(`/patients/doctors/${doctorId}/slots`, {
    params: { date },
  });
  return response.data;
};

export const bookAppointment = async (payload) => {
  const response = await apiClient.post("/patients/appointments", payload);
  return response.data;
};

export const getPatientAppointments = async () => {
  const response = await apiClient.get("/patients/appointments");
  return response.data;
};
