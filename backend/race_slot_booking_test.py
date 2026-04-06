import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def http_json(method: str, url: str, payload: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = Request(url=url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(raw)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8") or "{}"
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"detail": raw}
        return exc.code, body
    except URLError as exc:
        return 0, {"detail": f"Connection error: {exc}"}


def login(base_url: str, email: str, password: str) -> str:
    status, body = http_json(
        "POST",
        f"{base_url}/auth/login",
        {"email": email, "password": password},
    )
    if status != 200:
        raise RuntimeError(f"Login failed ({status}): {body}")
    token = body.get("access_token")
    if not token:
        raise RuntimeError(f"Login succeeded but token missing: {body}")
    return token


def pick_slot(base_url: str, token: str, target_date: str) -> tuple[str, str]:
    status, body = http_json("GET", f"{base_url}/patients/doctors?page=1&page_size=10", token=token)
    if status != 200:
        raise RuntimeError(f"Fetching doctors failed ({status}): {body}")
    doctors = body.get("items") or []
    if not doctors:
        raise RuntimeError("No doctors available to test with.")
    doctor_id = doctors[0]["doctor_id"]

    status, body = http_json(
        "GET",
        f"{base_url}/patients/doctors/{doctor_id}/slots?date={target_date}",
        token=token,
    )
    if status != 200:
        raise RuntimeError(f"Fetching slots failed ({status}): {body}")
    slots = body.get("slots") or []
    if not slots:
        raise RuntimeError("No available slots for selected date.")
    return doctor_id, slots[0]["start_time"]


def book_once(base_url: str, token: str, payload: dict, gate: threading.Event) -> tuple[int, dict]:
    gate.wait()
    return http_json("POST", f"{base_url}/patients/appointments", payload, token=token)


def main() -> None:
    parser = argparse.ArgumentParser(description="Race test for same doctor slot booking.")
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1", help="Backend API base URL.")
    parser.add_argument("--email-1", required=True, help="Patient 1 email.")
    parser.add_argument("--password-1", required=True, help="Patient 1 password.")
    parser.add_argument("--email-2", required=True, help="Patient 2 email.")
    parser.add_argument("--password-2", required=True, help="Patient 2 password.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Booking date YYYY-MM-DD.")
    args = parser.parse_args()

    print("Logging in two different patients...")
    token_a = login(args.base_url, args.email_1, args.password_1)
    token_b = login(args.base_url, args.email_2, args.password_2)

    print("Selecting doctor and slot...")
    doctor_id, start_time = pick_slot(args.base_url, token_a, args.date)
    payload = {
        "doctor_id": doctor_id,
        "date": args.date,
        "start_time": start_time,
        "reason": "Race condition test",
    }
    print(f"Target: doctor={doctor_id}, date={args.date}, slot={start_time}")

    gate = threading.Event()
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(book_once, args.base_url, token_a, payload, gate)
        fut_b = pool.submit(book_once, args.base_url, token_b, payload, gate)
        gate.set()
        result_a = fut_a.result()
        result_b = fut_b.result()

    (status_a, body_a), (status_b, body_b) = result_a, result_b
    print(f"\nRequest A ({args.email_1}):", status_a, body_a)
    print(f"Request B ({args.email_2}):", status_b, body_b)

    statuses = sorted([status_a, status_b])
    if statuses == [201, 409]:
        if status_a == 201:
            winner, loser = args.email_1, args.email_2
        else:
            winner, loser = args.email_2, args.email_1
        print(f"\nWinner: {winner} (appointment booked)")
        print(f"Loser : {loser} (slot already booked)")
        print("\nPASS: Concurrency handling works (one booked, one conflict).")
    else:
        print("\nCHECK: Expected [201, 409], got", statuses)


if __name__ == "__main__":
    main()



#python backend/race_slot_booking_test.py --email-1 <patient1_email> --password-1 <patient1_password> --email-2 <patient2_email> --password-2 <patient2_password>