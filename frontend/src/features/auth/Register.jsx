import { useState } from "react";
import { Link } from "react-router-dom";

import { authService } from "../../services/authService";
import { getUserFacingApiError } from "../../utils/apiErrors";

const initialFormState = {
  name: "",
  email: "",
  phone: "",
  password: "",
  role: "patient",
  specialization: "",
  experience_years: "0",
  consultation_fees: "0",
  working_from_hour: "9",
  working_from_period: "AM",
  working_to_hour: "8",
  working_to_period: "PM",
};

const pageStyles = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: "24px",
  background:
    "radial-gradient(circle at top, rgba(15, 118, 110, 0.24), transparent 30%), linear-gradient(135deg, #f4f9f7 0%, #dff4ec 52%, #fef7ed 100%)",
  fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
};

const cardStyles = {
  width: "100%",
  maxWidth: "520px",
  padding: "32px",
  borderRadius: "24px",
  backgroundColor: "rgba(255, 255, 255, 0.92)",
  boxShadow: "0 24px 60px rgba(15, 23, 42, 0.14)",
  border: "1px solid rgba(15, 118, 110, 0.12)",
};

const inputStyles = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "14px",
  border: "1px solid #cbd5e1",
  fontSize: "15px",
  outline: "none",
  boxSizing: "border-box",
  backgroundColor: "#ffffff",
};

const labelStyles = {
  display: "grid",
  gap: "8px",
  color: "#0f172a",
  fontWeight: 600,
  fontSize: "14px",
};

const buttonStyles = {
  width: "100%",
  padding: "14px 18px",
  border: "none",
  borderRadius: "14px",
  background: "linear-gradient(135deg, #0f766e 0%, #14532d 100%)",
  color: "#ffffff",
  fontSize: "16px",
  fontWeight: 700,
  cursor: "pointer",
};

function Register() {
  const [form, setForm] = useState(initialFormState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  const to24HourString = (hour12, period) => {
    const normalizedHour = Number.parseInt(hour12, 10);
    if (!Number.isFinite(normalizedHour) || normalizedHour < 1 || normalizedHour > 12) {
      return "00:00";
    }
    let hour24 = normalizedHour % 12;
    if (period === "PM") {
      hour24 += 12;
    }
    return `${String(hour24).padStart(2, "0")}:00`;
  };

  const toMinutes = (hour12, period) => {
    const normalizedHour = Number.parseInt(hour12, 10);
    if (!Number.isFinite(normalizedHour) || normalizedHour < 1 || normalizedHour > 12) {
      return null;
    }
    let hour24 = normalizedHour % 12;
    if (period === "PM") {
      hour24 += 12;
    }
    return hour24 * 60;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(null);

    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      password: form.password,
      role: form.role,
    };

    if (form.role === "doctor") {
      const exp = Number.parseInt(form.experience_years, 10);
      const fees = Number.parseFloat(form.consultation_fees);
      const fromMinutes = toMinutes(form.working_from_hour, form.working_from_period);
      const toMinutesValue = toMinutes(form.working_to_hour, form.working_to_period);

      if (!form.specialization.trim()) {
        setError("Specialization is required for doctor registration.");
        setLoading(false);
        return;
      }
      if (!Number.isFinite(exp) || exp < 0) {
        setError("Experience is required and must be 0 or more years.");
        setLoading(false);
        return;
      }
      if (!Number.isFinite(fees) || fees < 0) {
        setError("Consultation fee is required and must be 0 or more.");
        setLoading(false);
        return;
      }
      if (fromMinutes === null || toMinutesValue === null) {
        setError("Working hours are required for doctor registration.");
        setLoading(false);
        return;
      }
      if (fromMinutes === toMinutesValue) {
        setError("Work from and work to time cannot be the same.");
        setLoading(false);
        return;
      }
      if (toMinutesValue <= fromMinutes) {
        setError("Work to time must be later than work from time.");
        setLoading(false);
        return;
      }
      if (toMinutesValue - fromMinutes < 7 * 60) {
        setError("Doctor working hours must have at least 7 hours difference.");
        setLoading(false);
        return;
      }

      payload.doctor_profile = {
        specialization: form.specialization.trim(),
        experience_years: exp,
        consultation_fees: fees,
        everyday_timing: {
          start_time: to24HourString(form.working_from_hour, form.working_from_period),
          end_time: to24HourString(form.working_to_hour, form.working_to_period),
        },
      };
    }

    try {
      const response = await authService.register(payload);
      setSuccess(response);
      setForm(initialFormState);
    } catch (requestError) {
      setError(
        getUserFacingApiError(
          requestError,
          "Something went wrong while creating your account. Please try again."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyles}>
      <div style={cardStyles}>
        <div style={{ marginBottom: "24px" }}>
          <p
            style={{
              margin: 0,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              fontSize: "12px",
              color: "#0f766e",
              fontWeight: 700,
            }}
          >
            Hospital appointment booking
          </p>
          <h1 style={{ margin: "10px 0 8px", fontSize: "32px", color: "#0f172a" }}>
            Create your account
          </h1>
          <p style={{ margin: 0, color: "#475569", lineHeight: 1.6 }}>
            Register as a patient or doctor. Verify your email to continue. Doctors must be approved
            by an admin before they can sign in.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "18px" }}>
          <label style={labelStyles}>
            Full name
            <input
              style={inputStyles}
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Your name"
              required
            />
          </label>

          <label style={labelStyles}>
            Email address
            <input
              style={inputStyles}
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
          </label>

          <label style={labelStyles}>
            Phone
            <input
              style={inputStyles}
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="10+ digits"
              required
              minLength={10}
            />
          </label>

          <label style={labelStyles}>
            Password
            <input
              style={inputStyles}
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Minimum 8 characters"
              required
            />
          </label>

          <label style={labelStyles}>
            I am a
            <select
              style={inputStyles}
              name="role"
              value={form.role}
              onChange={handleChange}
              required
            >
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
            </select>
          </label>

          {form.role === "doctor" ? (
            <>
              <label style={labelStyles}>
                Specialization
                <input
                  style={inputStyles}
                  type="text"
                  name="specialization"
                  value={form.specialization}
                  onChange={handleChange}
                  placeholder="e.g. Cardiology"
                  required
                />
              </label>
              <label style={labelStyles}>
                Experience (years)
                <input
                  style={inputStyles}
                  type="number"
                  name="experience_years"
                  value={form.experience_years}
                  onChange={handleChange}
                  min={0}
                  step="1"
                  required
                />
              </label>
              <label style={labelStyles}>
                Consultation fees
                <input
                  style={inputStyles}
                  type="number"
                  name="consultation_fees"
                  value={form.consultation_fees}
                  onChange={handleChange}
                  min={0}
                  step="0.01"
                  required
                />
              </label>
              <label style={labelStyles}>
                Working hours from
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <select
                    style={inputStyles}
                    name="working_from_hour"
                    value={form.working_from_hour}
                    onChange={handleChange}
                    required
                  >
                    {Array.from({ length: 12 }, (_, i) => String(i + 1)).map((hour) => (
                      <option key={`from-${hour}`} value={hour}>
                        {hour}
                      </option>
                    ))}
                  </select>
                  <select
                    style={inputStyles}
                    name="working_from_period"
                    value={form.working_from_period}
                    onChange={handleChange}
                    required
                  >
                    <option value="AM">AM</option>
                    <option value="PM">PM</option>
                  </select>
                </div>
              </label>
              <label style={labelStyles}>
                Working hours to
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <select
                    style={inputStyles}
                    name="working_to_hour"
                    value={form.working_to_hour}
                    onChange={handleChange}
                    required
                  >
                    {Array.from({ length: 12 }, (_, i) => String(i + 1)).map((hour) => (
                      <option key={`to-${hour}`} value={hour}>
                        {hour}
                      </option>
                    ))}
                  </select>
                  <select
                    style={inputStyles}
                    name="working_to_period"
                    value={form.working_to_period}
                    onChange={handleChange}
                    required
                  >
                    <option value="AM">AM</option>
                    <option value="PM">PM</option>
                  </select>
                </div>
              </label>
            </>
          ) : null}

          {error ? (
            <div
              style={{
                padding: "12px 14px",
                borderRadius: "14px",
                backgroundColor: "#fef2f2",
                color: "#b91c1c",
                border: "1px solid #fecaca",
              }}
            >
              {error}
            </div>
          ) : null}

          {success ? (
            <div
              style={{
                padding: "14px",
                borderRadius: "16px",
                backgroundColor: "#ecfdf5",
                color: "#166534",
                border: "1px solid #bbf7d0",
                lineHeight: 1.7,
              }}
            >
              <strong>{success.message}</strong>
              <div style={{ marginTop: "8px" }}>
                Verification email sent: {success.verification_email_sent ? "Yes" : "No"}
              </div>
              <div style={{ marginTop: "8px" }}>
                {success.user.role === "doctor"
                  ? "After you verify your email, an admin must approve your doctor account before you can sign in."
                  : "After you verify your email, your patient account becomes active and you can sign in."}
              </div>
            </div>
          ) : null}

          <button type="submit" disabled={loading} style={buttonStyles}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p style={{ margin: "22px 0 0", color: "#475569", textAlign: "center" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#0f766e", fontWeight: 700 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
