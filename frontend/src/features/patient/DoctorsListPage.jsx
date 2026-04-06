import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { authService } from "../../services/authService";
import { patientService } from "../../services/patientService";
import { formatRangeToAmPm } from "../../utils/timeFormat";
import { getUserFacingApiError } from "../../utils/apiErrors";

const pageStyles = {
  minHeight: "100vh",
  padding: "24px",
  background:
    "radial-gradient(circle at top left, rgba(15, 118, 110, 0.24), transparent 26%), radial-gradient(circle at bottom right, rgba(14, 116, 144, 0.18), transparent 28%), linear-gradient(140deg, #f4f9f7 0%, #e0f2fe 50%, #fff7ed 100%)",
  fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  color: "#0f172a",
};

const shellStyles = { maxWidth: "1120px", margin: "0 auto" };

function DoctorsListPage() {
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 8, totalPages: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDoctors = async (pageToLoad = 1) => {
    setLoading(true);
    setError("");
    try {
      const response = await patientService.getDoctors({ page: pageToLoad, pageSize: pagination.pageSize });
      setDoctors(response.items);
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        totalPages: response.total_pages,
        total: response.total,
      });
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Unable to load doctors right now."));
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
    loadDoctors(1);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  return (
    <div style={pageStyles}>
      <div style={shellStyles}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "22px", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ margin: "0 0 8px", fontSize: "38px" }}>Available doctors</h1>
            <p style={{ margin: 0, color: "#475569" }}>
              Choose a doctor to view hourly appointment slots.
            </p>
          </div>
          <Link to="/patient/dashboard" style={{ textDecoration: "none", fontWeight: 700, color: "#0f766e" }}>
            Back to dashboard
          </Link>
        </header>

        {error ? <div style={{ padding: "12px", borderRadius: "12px", background: "#fef2f2", color: "#b91c1c", marginBottom: "12px" }}>{error}</div> : null}
        {loading ? <div>Loading doctors...</div> : null}

        {!loading && doctors.length === 0 ? (
          <div style={{ padding: "16px", borderRadius: "16px", background: "#fff", border: "1px solid #e2e8f0" }}>
            No doctors available right now.
          </div>
        ) : null}

        {!loading && doctors.length > 0 ? (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
              {doctors.map((doctor) => (
                <article key={doctor.doctor_id} style={{ padding: "20px", borderRadius: "20px", background: "#fff", border: "1px solid #e2e8f0", boxShadow: "0 10px 24px rgba(15,23,42,0.06)" }}>
                  <h2 style={{ margin: "0 0 10px", fontSize: "24px" }}>{doctor.name}</h2>
                  <p style={{ margin: "0 0 6px", color: "#475569" }}>{doctor.specialization}</p>
                  <p style={{ margin: "0 0 6px", color: "#475569" }}>Experience: {doctor.experience_years} years</p>
                  <p style={{ margin: "0 0 10px", color: "#475569" }}>Fee: {doctor.consultation_fees}</p>
                  <p style={{ margin: "0 0 14px", color: "#334155", fontWeight: 600 }}>
                    Hours: {formatRangeToAmPm(doctor.everyday_timing?.start_time, doctor.everyday_timing?.end_time)}
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate(`/patient/doctors/${doctor.doctor_id}/slots`)}
                    style={{ width: "100%", border: "none", borderRadius: "12px", padding: "12px", color: "#fff", fontWeight: 700, background: "linear-gradient(135deg, #0f766e 0%, #14532d 100%)", cursor: "pointer" }}
                  >
                    View slots
                  </button>
                </article>
              ))}
            </div>

            <div style={{ marginTop: "18px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>Page {pagination.page} of {pagination.totalPages || 1}</div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button type="button" disabled={pagination.page <= 1} onClick={() => loadDoctors(pagination.page - 1)}>
                  Previous
                </button>
                <button type="button" disabled={pagination.totalPages === 0 || pagination.page >= pagination.totalPages} onClick={() => loadDoctors(pagination.page + 1)}>
                  Next
                </button>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default DoctorsListPage;
