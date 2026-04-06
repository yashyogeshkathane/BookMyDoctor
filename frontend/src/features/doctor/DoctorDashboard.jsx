import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { authService } from "../../services/authService";
import { doctorService } from "../../services/doctorService";
import { formatRangeToAmPm } from "../../utils/timeFormat";
import { getUserFacingApiError } from "../../utils/apiErrors";

const toDateInput = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

function DoctorDashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [date, setDate] = useState(toDateInput(new Date()));
  const [slots, setSlots] = useState([]);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(true);
  const [error, setError] = useState("");

  const loadProfile = async () => {
    setLoadingProfile(true);
    try {
      const response = await doctorService.getProfile();
      setProfile(response);
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Unable to load doctor profile."));
    } finally {
      setLoadingProfile(false);
    }
  };

  const loadSlots = async () => {
    setLoadingSlots(true);
    try {
      const response = await doctorService.getSlots({ date });
      setSlots(response.slots || []);
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Unable to load slot overview."));
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  useEffect(() => {
    const user = authService.getStoredUser();
    if (!user) {
      navigate("/login", { replace: true });
      return;
    }
    if (user.role !== "doctor") {
      navigate("/", { replace: true });
      return;
    }
    loadProfile();
    loadSlots();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const handleLogout = async () => {
    await authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div style={{ minHeight: "100vh", padding: "24px", background: "#f8fafc", fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "20px", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ margin: "0 0 8px", fontSize: "36px" }}>Doctor Dashboard</h1>
            <p style={{ margin: 0, color: "#475569" }}>View your profile and slot status (booked vs available).</p>
          </div>
          <button type="button" onClick={handleLogout}>Logout</button>
        </header>

        {error ? <div style={{ padding: "12px", borderRadius: "12px", background: "#fef2f2", color: "#b91c1c", marginBottom: "12px" }}>{error}</div> : null}

        <section style={{ padding: "18px", borderRadius: "16px", background: "#fff", border: "1px solid #e2e8f0", marginBottom: "16px" }}>
          {loadingProfile ? <div>Loading profile...</div> : null}
          {!loadingProfile && profile ? (
            <>
              <h2 style={{ marginTop: 0 }}>{profile.name}</h2>
              <div style={{ color: "#475569", marginBottom: "4px" }}>{profile.specialization}</div>
              <div style={{ color: "#475569", marginBottom: "4px" }}>Experience: {profile.experience_years} years</div>
              <div style={{ color: "#475569", marginBottom: "4px" }}>Consultation fee: {profile.consultation_fees}</div>
              <div style={{ color: "#334155", fontWeight: 700 }}>
                Working hours: {formatRangeToAmPm(profile.everyday_timing?.start_time, profile.everyday_timing?.end_time)}
              </div>
            </>
          ) : null}
        </section>

        <section style={{ padding: "18px", borderRadius: "16px", background: "#fff", border: "1px solid #e2e8f0" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px", marginBottom: "12px" }}>
            <h2 style={{ margin: 0 }}>My Slots</h2>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label htmlFor="doctor-slot-date">Date</label>
              <input id="doctor-slot-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} />
              <button type="button" onClick={loadSlots}>Load</button>
            </div>
          </div>

          {loadingSlots ? <div>Loading slots...</div> : null}

          {!loadingSlots && slots.length === 0 ? <div>No slots found for this date.</div> : null}

          {!loadingSlots && slots.length > 0 ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "10px" }}>
              {slots.map((slot) => (
                <article key={slot.start_time} style={{ padding: "12px", borderRadius: "12px", border: "1px solid #e2e8f0", background: slot.status === "booked" ? "#fff7ed" : "#ecfdf5" }}>
                  <div style={{ fontWeight: 700 }}>{formatRangeToAmPm(slot.start_time, slot.end_time)}</div>
                  <div style={{ marginTop: "6px", fontWeight: 700, color: slot.status === "booked" ? "#9a3412" : "#166534" }}>
                    {slot.status.toUpperCase()}
                  </div>
                  {slot.status === "booked" ? (
                    <div style={{ marginTop: "6px", color: "#475569" }}>
                      {slot.patient_name || "Patient"} {slot.patient_email ? `(${slot.patient_email})` : ""}
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}

export default DoctorDashboard;
