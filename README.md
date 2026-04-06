# BookMyDoctor

A full-stack, role-based appointment booking application for **BookMyDoctor** with three user types:
- `admin` - approves doctor accounts
- `doctor` - views own profile and slot status
- `patient` - browses doctors, views slots, and books appointments

The project keeps a clean authorization workflow and uses MongoDB for persistence.

## How It Works

### 1) Registration and approval flow
- Patient registers -> verifies email -> account becomes active.
- Doctor registers (with profile + working hours) -> verifies email -> account is pending approval.
- Admin approves doctor -> doctor can log in.

### 2) Slot generation
- Doctor working hours are stored in `doctors.everyday_timing`:
  - `start_time` (e.g. `09:00`)
  - `end_time` (e.g. `20:00`)
- Patient slot list is generated hour-by-hour in that range.

### 3) Booking and concurrency safety
- Booking creates a `confirmed` appointment in `appointments`.
- To prevent double booking of the same slot:
  - a unique partial index is enforced for `(doctor_id, date_key, start_time)` where `status = confirmed`
  - concurrent requests are handled so one succeeds and the other returns `409 Conflict`.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI (Python)
- Database: MongoDB
- Auth: JWT access + refresh tokens

## Database Collections

Only these collections are used:

1. `users`
2. `doctors`
3. `appointments`

## Project Structure

```text
BookMyDoctor/
  frontend/
    src/
      api/                # axios API clients (auth/admin/patient/doctor)
      services/           # service wrappers around API modules
      features/
        auth/             # register, login, verify email
        home/             # public landing page
        admin/            # admin dashboard + doctor approval
        patient/          # patient dashboard, doctors, slots, appointments
        doctor/           # doctor dashboard, profile, own slots
      routes/             # app route map
      utils/              # helpers (errors, time formatting, etc.)
  backend/
    app/
      api/routes/         # auth, admin, patient, doctor endpoints
      services/           # business logic layer
      repositories/       # Mongo data access
      schemas/            # request/response models
      models/             # domain models/enums
      config/             # settings, db, security, email
      middleware/         # request logging
      core/               # logger and shared internals
      main.py             # FastAPI app bootstrap
    race_slot_booking_test.py  # concurrency test script
  .env                    # root environment config for backend
```

## Environment Variables

Create `.env` in project root (already supported in code). Required keys:
- `MONGODB_URI`
- `JWT_SECRET_KEY`
- `REFRESH_TOKEN_SECRET_KEY`

Common optional keys:
- `MONGODB_DB_NAME`
- `INITIAL_ADMIN_NAME`
- `INITIAL_ADMIN_EMAIL`
- `INITIAL_ADMIN_PASSWORD`
- `FRONTEND_URL`
- SMTP keys for real email delivery

For frontend, create:
- `frontend/.env`
- `VITE_API_BASE_URL=http://localhost:8000/api/v1`

## Run the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs on `http://localhost:8000`.

Swagger docs:
- `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`.

## Useful Test Script (Race Condition)

To test same-slot concurrent booking with two patients:

```bash
python backend/race_slot_booking_test.py --email-1 <patient1_email> --password-1 <patient1_password> --email-2 <patient2_email> --password-2 <patient2_password>
```

Expected outcome:
- one request returns `201`
- the other returns `409` with slot already booked message

## License

This project is licensed under the MIT License. See `LICENSE`.
