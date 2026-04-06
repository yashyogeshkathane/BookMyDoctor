import { approveDoctor, getPendingDoctors } from "../api/adminApi";

export const adminService = {
  async getPendingDoctors(params) {
    return getPendingDoctors(params);
  },

  async approveDoctor(userId) {
    return approveDoctor(userId);
  },
};
