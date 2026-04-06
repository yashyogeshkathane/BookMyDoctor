import {
  bookAppointment,
  getAvailableDoctors,
  getDoctorSlots,
  getPatientAppointments,
} from "../api/patientApi";

export const patientService = {
  async getDoctors(params) {
    return getAvailableDoctors(params);
  },

  async getSlots(params) {
    return getDoctorSlots(params);
  },

  async book(payload) {
    return bookAppointment(payload);
  },

  async getAppointments() {
    return getPatientAppointments();
  },
};
