import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { authService } from "../../services/authService";
import { patientService } from "../../services/patientService";
import { formatRangeToAmPm } from "../../utils/timeFormat";
import { getUserFacingApiError } from "../../utils/apiErrors";

function PatientAppointmentsPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAppointments = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await patientService.getAppointments();
      setItems(response || []);
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Unable to load booked appointments right now."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const user = authService.getStoredUser();
    if (!user) {
      navigate("/login", { replace: true });
      return;
    }
    if (user.role !== "patient") {
      navigate("/", { replace: true });
      return;
    }
    loadAppointments();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  return (
    <div style={{ minHeight: "100vh", padding: "24px", fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", background: "#f8fafc" }}>
      <div style={{ maxWidth: "980px", margin: "0 auto" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "20px", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ margin: "0 0 8px", fontSize: "34px" }}>My booked slots</h1>
            <p style={{ margin: 0, color: "#475569" }}>All appointments booked by your account.</p>
          </div>
          <Link to="/patient/dashboard" style={{ color: "#0f766e", fontWeight: 700, textDecoration: "none" }}>
            Back to dashboard
          </Link>
        </header>

        {error ? <div style={{ padding: "12px", borderRadius: "12px", background: "#fef2f2", color: "#b91c1c", marginBottom: "12px" }}>{error}</div> : null}
        {loading ? <div>Loading appointments...</div> : null}

        {!loading && items.length === 0 ? (
          <div style={{ padding: "16px", borderRadius: "16px", background: "#fff", border: "1px solid #e2e8f0" }}>
            You have not booked any slot yet.
          </div>
        ) : null}

        {!loading && items.length > 0 ? (
          <div style={{ display: "grid", gap: "12px" }}>
            {items.map((item) => (
              <article key={item.id} style={{ padding: "16px", borderRadius: "14px", background: "#fff", border: "1px solid #e2e8f0" }}>
                <div style={{ fontWeight: 800, fontSize: "18px" }}>{item.doctor_name}</div>
                <div style={{ color: "#475569", marginTop: "4px" }}>{item.specialization}</div>
                <div style={{ marginTop: "8px", color: "#0f172a" }}>
                  {new Date(item.date).toDateString()} | {formatRangeToAmPm(item.start_time, item.end_time)}
                </div>
                <div style={{ marginTop: "8px", display: "inline-flex", padding: "4px 10px", borderRadius: "999px", background: "#ecfeff", color: "#155e75", fontWeight: 700 }}>
                  {item.status}
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default PatientAppointmentsPage;
