import { getDoctorProfile, getDoctorSlots } from "../api/doctorApi";

export const doctorService = {
  async getProfile() {
    return getDoctorProfile();
  },

  async getSlots(params) {
    return getDoctorSlots(params);
  },
};
