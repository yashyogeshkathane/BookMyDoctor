export const formatToAmPm = (time24) => {
  if (!time24 || typeof time24 !== "string" || !time24.includes(":")) {
    return time24 || "";
  }

  const [hourPart, minutePart] = time24.split(":");
  const hour = Number.parseInt(hourPart, 10);
  const minute = Number.parseInt(minutePart, 10);
  if (!Number.isFinite(hour) || !Number.isFinite(minute)) {
    return time24;
  }

  const suffix = hour >= 12 ? "PM" : "AM";
  const hour12 = hour % 12 === 0 ? 12 : hour % 12;
  return `${hour12}:${String(minute).padStart(2, "0")} ${suffix}`;
};

export const formatRangeToAmPm = (start, end) =>
  `${formatToAmPm(start)} - ${formatToAmPm(end)}`;
