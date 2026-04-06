import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { authService } from "../../services/authService";
import { getUserFacingApiError } from "../../utils/apiErrors";

const pageStyles = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: "24px",
  background:
    "radial-gradient(circle at center, rgba(251, 191, 36, 0.2), transparent 28%), linear-gradient(180deg, #fff7ed 0%, #f8fafc 100%)",
  fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
};

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get("token") || "", [searchParams]);
  const [status, setStatus] = useState(token ? "loading" : "missing");
  const [message, setMessage] = useState("Verifying your email address...");

  useEffect(() => {
    const runVerification = async () => {
      if (!token) {
        setStatus("missing");
        setMessage("Verification token is missing from the link.");
        return;
      }

      try {
        const response = await authService.verifyEmail(token);
        setStatus("success");
        setMessage(response.message);
      } catch (requestError) {
        setStatus("error");
        setMessage(
          getUserFacingApiError(
            requestError,
            "We could not verify your email. Please try again."
          )
        );
      }
    };

    runVerification();
  }, [token]);

  const accentColor =
    status === "success"
      ? "#166534"
      : status === "error" || status === "missing"
        ? "#b45309"
        : "#1d4ed8";

  return (
    <div style={pageStyles}>
      <div
        style={{
          width: "100%",
          maxWidth: "520px",
          padding: "34px",
          borderRadius: "24px",
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          border: "1px solid rgba(148, 163, 184, 0.22)",
          boxShadow: "0 24px 64px rgba(15, 23, 42, 0.12)",
          textAlign: "center",
        }}
      >
        <p
          style={{
            margin: 0,
            textTransform: "uppercase",
            letterSpacing: "0.14em",
            fontWeight: 700,
            fontSize: "12px",
            color: accentColor,
          }}
        >
          Email Verification
        </p>
        <h1 style={{ margin: "12px 0 10px", fontSize: "32px", color: "#0f172a" }}>
          {status === "success" ? "You're verified" : "Checking your link"}
        </h1>
        <p style={{ margin: 0, color: "#475569", lineHeight: 1.7 }}>{message}</p>

        <div
          style={{
            marginTop: "26px",
            display: "flex",
            gap: "12px",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <Link
            to="/login"
            style={{
              padding: "12px 18px",
              borderRadius: "999px",
              backgroundColor: "#0f172a",
              color: "#ffffff",
              textDecoration: "none",
              fontWeight: 700,
            }}
          >
            Go to login
          </Link>
          <Link
            to="/register"
            style={{
              padding: "12px 18px",
              borderRadius: "999px",
              backgroundColor: "#ffffff",
              color: "#0f172a",
              border: "1px solid #cbd5e1",
              textDecoration: "none",
              fontWeight: 700,
            }}
          >
            Back to register
          </Link>
        </div>
      </div>
    </div>
  );
}

export default VerifyEmail;
