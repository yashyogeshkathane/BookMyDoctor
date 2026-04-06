import { Route, Routes } from "react-router-dom";

import AdminDashboard from "../features/admin/AdminDashboard";
import ManageDoctors from "../features/admin/ManageDoctors";
import Login from "../features/auth/Login";
import Register from "../features/auth/Register";
import LandingPage from "../features/home/LandingPage";
import VerifyEmail from "../features/auth/VerifyEmail";
import DoctorDashboard from "../features/doctor/DoctorDashboard";
import PatientDashboard from "../features/patient/PatientDashboard";
import DoctorsListPage from "../features/patient/DoctorsListPage";
import DoctorSlotsPage from "../features/patient/DoctorSlotsPage";
import PatientAppointmentsPage from "../features/patient/PatientAppointmentsPage";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />
      <Route path="/admin/manage-doctors" element={<ManageDoctors />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
      <Route path="/patient/dashboard" element={<PatientDashboard />} />
      <Route path="/patient/doctors" element={<DoctorsListPage />} />
      <Route path="/patient/doctors/:doctorId/slots" element={<DoctorSlotsPage />} />
      <Route path="/patient/appointments" element={<PatientAppointmentsPage />} />
    </Routes>
  );
}

export default AppRoutes;
