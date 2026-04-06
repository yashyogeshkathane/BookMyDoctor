import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import { authService } from "../../services/authService";

const pageStyles = {
  minHeight: "100vh",
  padding: "24px",
  background:
    "radial-gradient(circle at top left, rgba(15, 118, 110, 0.24), transparent 26%), radial-gradient(circle at bottom right, rgba(14, 116, 144, 0.18), transparent 28%), linear-gradient(140deg, #f4f9f7 0%, #e0f2fe 50%, #fff7ed 100%)",
  fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  color: "#0f172a",
};

const shellStyles = {
  maxWidth: "1180px",
  margin: "0 auto",
};

const pillStyles = {
  display: "inline-block",
  padding: "8px 14px",
  borderRadius: "999px",
  backgroundColor: "rgba(15, 118, 110, 0.1)",
  color: "#0f766e",
  fontSize: "12px",
  fontWeight: 800,
  textTransform: "uppercase",
  letterSpacing: "0.14em",
};

const heroCardStyles = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1.25fr) minmax(280px, 0.9fr)",
  gap: "24px",
  padding: "32px",
  borderRadius: "32px",
  backgroundColor: "rgba(255, 255, 255, 0.92)",
  boxShadow: "0 24px 64px rgba(15, 23, 42, 0.12)",
  border: "1px solid rgba(15, 118, 110, 0.12)",
};

const featureCardStyles = {
  padding: "26px",
  borderRadius: "26px",
  backgroundColor: "rgba(255, 255, 255, 0.9)",
  boxShadow: "0 18px 44px rgba(15, 23, 42, 0.08)",
  border: "1px solid rgba(148, 163, 184, 0.16)",
  display: "grid",
  gap: "16px",
};

const primaryActionStyles = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "14px 20px",
  borderRadius: "14px",
  background: "linear-gradient(135deg, #0f766e 0%, #14532d 100%)",
  color: "#ffffff",
  textDecoration: "none",
  fontWeight: 700,
};

const secondaryActionStyles = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "14px 20px",
  borderRadius: "14px",
  backgroundColor: "#ffffff",
  color: "#0f172a",
  textDecoration: "none",
  fontWeight: 700,
  border: "1px solid #cbd5e1",
};

function PatientDashboard() {
  const navigate = useNavigate();
  const storedUser = authService.getStoredUser();

  useEffect(() => {
    if (!storedUser) {
      navigate("/login", { replace: true });
      return;
    }
    if (storedUser.role !== "patient") {
      navigate("/", { replace: true });
    }
  }, [navigate, storedUser]);

  if (!storedUser || storedUser.role !== "patient") {
    return null;
  }

  const handleLogout = async () => {
    await authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div style={pageStyles}>
      <div style={shellStyles}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "16px",
            marginBottom: "28px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div style={pillStyles}>Patient</div>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            style={{
              padding: "14px 20px",
              borderRadius: "14px",
              backgroundColor: "#ffffff",
              color: "#b91c1c",
              border: "1px solid #fecaca",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </header>

        <section style={heroCardStyles}>
          <div>
            <h1 style={{ margin: "0 0 16px", fontSize: "clamp(2.5rem, 5vw, 4.2rem)", lineHeight: 1.02 }}>
              Welcome, {storedUser.name}
            </h1>
            <p style={{ margin: "0 0 24px", fontSize: "18px", lineHeight: 1.75, color: "#475569", maxWidth: "640px" }}>
              Browse available doctors, view their slots, and book your appointment in a few clicks.
            </p>
          </div>
          <div style={{ display: "grid", gap: "16px", alignContent: "start" }}>
            <div style={{ padding: "24px", borderRadius: "24px", background: "linear-gradient(180deg, #0f172a 0%, #134e4a 100%)", color: "#ffffff", minHeight: "220px" }}>
              <div style={{ fontSize: "13px", textTransform: "uppercase", letterSpacing: "0.14em", opacity: 0.76 }}>
                Booking flow
              </div>
              <div style={{ marginTop: "18px", fontSize: "28px", fontWeight: 800 }}>
                Doctors {"->"} Slots {"->"} Confirmed Appointment
              </div>
              <div style={{ marginTop: "12px", lineHeight: 1.7, color: "rgba(255,255,255,0.78)" }}>
                Available slots are generated from doctor working hours and hide already-booked timings.
              </div>
            </div>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "20px",
            marginTop: "24px",
          }}
        >
          <article style={{ ...featureCardStyles, background: "linear-gradient(135deg, rgba(15, 118, 110, 0.12) 0%, rgba(20, 83, 45, 0.08) 100%)" }}>
            <div>
              <h2 style={{ margin: "0 0 10px", fontSize: "26px" }}>All doctors</h2>
              <p style={{ margin: 0, color: "#475569", lineHeight: 1.75 }}>
                Open the doctor directory, pick a doctor, check available slots, and book instantly.
              </p>
            </div>
            <Link to="/patient/doctors" style={primaryActionStyles}>
              View doctors
            </Link>
          </article>
          <article style={featureCardStyles}>
            <div>
              <h2 style={{ margin: "0 0 10px", fontSize: "26px" }}>View booked slots</h2>
              <p style={{ margin: 0, color: "#475569", lineHeight: 1.75 }}>
                Open your appointment list and see all slots booked by your account with doctor details.
              </p>
            </div>
            <Link to="/patient/appointments" style={secondaryActionStyles}>
              View my appointments
            </Link>
          </article>
        </section>
      </div>
    </div>
  );
}

export default PatientDashboard;
