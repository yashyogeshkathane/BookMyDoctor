import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { authService } from "../../services/authService";
import { patientService } from "../../services/patientService";
import { formatRangeToAmPm } from "../../utils/timeFormat";
import { getUserFacingApiError } from "../../utils/apiErrors";

const toDateInput = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

function DoctorSlotsPage() {
  const { doctorId } = useParams();
  const navigate = useNavigate();
  const [date, setDate] = useState(toDateInput(new Date()));
  const [doctorName, setDoctorName] = useState("Doctor");
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadSlots = async () => {
    if (!doctorId) return;
    setLoading(true);
    setError("");
    try {
      const response = await patientService.getSlots({ doctorId, date });
      setDoctorName(response.doctor_name);
      setSlots(response.slots || []);
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Unable to load slots for this doctor."));
      setSlots([]);
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
    loadSlots();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doctorId, navigate]);

  const headingDate = useMemo(() => new Date(date).toDateString(), [date]);

  const handleBook = async (slot) => {
    if (!doctorId) return;
    setBooking(slot.start_time);
    setError("");
    setMessage("");
    try {
      const response = await patientService.book({
        doctor_id: doctorId,
        date,
        start_time: slot.start_time,
        reason: "",
      });
      setMessage(`Appointment confirmed for ${formatRangeToAmPm(response.start_time, response.end_time)}.`);
      await loadSlots();
    } catch (requestError) {
      setError(getUserFacingApiError(requestError, "Could not book this slot. Please try another one."));
    } finally {
      setBooking("");
    }
  };

  return (
    <div style={{ minHeight: "100vh", padding: "24px", fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", background: "#f8fafc" }}>
      <div style={{ maxWidth: "980px", margin: "0 auto" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "18px", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ margin: "0 0 8px", fontSize: "34px" }}>{doctorName} - Slots</h1>
            <p style={{ margin: 0, color: "#475569" }}>{headingDate}</p>
          </div>
          <Link to="/patient/doctors" style={{ color: "#0f766e", fontWeight: 700, textDecoration: "none" }}>
            Back to doctors
          </Link>
        </header>

        <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "14px", flexWrap: "wrap" }}>
          <label htmlFor="slot-date" style={{ fontWeight: 600 }}>Select date</label>
          <input id="slot-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} />
          <button type="button" onClick={loadSlots}>Load slots</button>
        </div>

        {error ? <div style={{ padding: "12px", borderRadius: "12px", background: "#fef2f2", color: "#b91c1c", marginBottom: "12px" }}>{error}</div> : null}
        {message ? <div style={{ padding: "12px", borderRadius: "12px", background: "#ecfdf5", color: "#166534", marginBottom: "12px" }}>{message}</div> : null}
        {loading ? <div>Loading slots...</div> : null}

        {!loading && slots.length === 0 ? (
          <div style={{ padding: "16px", borderRadius: "16px", background: "#fff", border: "1px solid #e2e8f0" }}>
            No available slots for this date.
          </div>
        ) : null}

        {!loading && slots.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px" }}>
            {slots.map((slot) => (
              <article key={slot.start_time} style={{ padding: "14px", borderRadius: "14px", background: "#fff", border: "1px solid #e2e8f0" }}>
                <div style={{ fontWeight: 700 }}>{formatRangeToAmPm(slot.start_time, slot.end_time)}</div>
                <button
                  type="button"
                  disabled={booking === slot.start_time}
                  onClick={() => handleBook(slot)}
                  style={{ marginTop: "10px", width: "100%", border: "none", borderRadius: "10px", padding: "10px", color: "#fff", fontWeight: 700, background: "linear-gradient(135deg, #0f766e 0%, #14532d 100%)", cursor: "pointer" }}
                >
                  {booking === slot.start_time ? "Booking..." : "Book slot"}
                </button>
              </article>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default DoctorSlotsPage;
