import React from "react";
import { badgeBase } from "../styles/theme";

const getStatusStyle = (status) => {
  switch (status) {
    case "ASSIGNED":
      return {
        background: "#fef3c7",
        color: "#92400e",
      };
    case "IN_PROGRESS":
      return {
        background: "#dbeafe",
        color: "#1d4ed8",
      };
    case "RESOLVED":
      return {
        background: "#dcfce7",
        color: "#166534",
      };
    default:
      return {
        background: "#e2e8f0",
        color: "#334155",
      };
  }
};

const StatusBadge = ({ status }) => {
  return (
    <span style={{ ...badgeBase, ...getStatusStyle(status) }}>{status}</span>
  );
};

export default StatusBadge;
