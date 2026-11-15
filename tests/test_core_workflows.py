import unittest
from datetime import date, timedelta

from app import create_app
from extensions import db
from forms.auth_forms import RegistrationForm
from models.booking import Booking
from models.boat import Boat
from models.destination import Destination
from models.user import User


class TestConfig:
    TESTING = True
    SECRET_KEY = "isolated-test-key"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class CoreWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.customer = User(
            full_name="Test Customer",
            email="customer@example.com",
            contact_number="09123456789",
            role="customer",
            is_verified=True,
        )
        self.other_customer = User(
            full_name="Other Customer",
            email="other@example.com",
            contact_number="09123456788",
            role="customer",
            is_verified=True,
        )
        self.admin = User(
            full_name="Test Admin",
            email="admin@example.com",
            contact_number="09123456787",
            role="admin",
            is_verified=True,
        )
        for user in (self.customer, self.other_customer, self.admin):
            user.set_password("TestPassword123")
        self.boat = Boat(
            name="Test Boat",
            fuel_type="Diesel",
            passenger_capacity=10,
            availability_status="available",
            is_active=True,
        )
        self.destination = Destination(
            name="Test Beach",
            municipality="Infanta",
            province="Quezon",
            is_active=True,
        )
        db.session.add_all([
            self.customer,
            self.other_customer,
            self.admin,
            self.boat,
            self.destination,
        ])
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def login_as(self, user):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user.id)
            session["_fresh"] = True

    def test_customer_can_submit_valid_booking(self):
        self.login_as(self.customer)
        trip_date = (date.today() + timedelta(days=2)).isoformat()

        response = self.client.post(
            "/booking/book",
            data={
                "destination_id": str(self.destination.id),
                "boat_id": str(self.boat.id),
                "trip_date": trip_date,
                "passenger_count": "4",
                "special_request": "Window-side seating",
            },
        )

        self.assertEqual(response.status_code, 302)
        booking = Booking.query.one()
        self.assertEqual(booking.user_id, self.customer.id)
        self.assertEqual(booking.status, "pending")
        self.assertEqual(booking.trip_date.isoformat(), trip_date)

    def test_boat_details_prefills_selected_available_boat(self):
        self.login_as(self.customer)
        response = self.client.get(f"/booking/book?boat_id={self.boat.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'<option selected value="{self.boat.id}">'.encode(),
            response.data,
        )

    def test_customer_dashboard_renders_booking_status_and_action(self):
        booking = Booking(
            booking_reference="BK-DASH1",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="confirmed",
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.get("/customer/bookings")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Confirmed", response.data)
        self.assertIn(b"View details", response.data)

    def test_customer_navigation_includes_my_bookings(self):
        self.login_as(self.customer)

        response = self.client.get("/customer/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My bookings", response.data)

    def test_customer_booking_summary_explains_confirmed_status(self):
        booking = Booking(
            booking_reference="BK-STATUS1",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="confirmed",
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.get(f"/booking/{booking.id}/summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your reservation is confirmed", response.data)

    def test_customer_cannot_see_another_customers_booking(self):
        booking = Booking(
            booking_reference="BK-ISOLATED1",
            user_id=self.other_customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.get(f"/booking/{booking.id}/summary")

        self.assertEqual(response.status_code, 404)

    def test_customer_can_cancel_own_pending_booking(self):
        booking = Booking(
            booking_reference="BK-CANCEL1",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.post(f"/booking/{booking.id}/cancel")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Booking, booking.id).status, "cancelled")

    def test_booking_rejects_boat_capacity_overage(self):
        self.login_as(self.customer)
        trip_date = (date.today() + timedelta(days=4)).isoformat()

        response = self.client.post(
            "/booking/book",
            data={
                "destination_id": str(self.destination.id),
                "boat_id": str(self.boat.id),
                "trip_date": trip_date,
                "passenger_count": "11",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.query.count(), 0)
        self.assertIn(b"Number must be between 1 and 10", response.data)

    def test_booking_rejects_conflicting_boat_date(self):
        trip_date = date.today() + timedelta(days=5)
        existing_booking = Booking(
            booking_reference="BK-CONFLICT1",
            user_id=self.other_customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=trip_date,
            passenger_count=2,
            status="confirmed",
        )
        db.session.add(existing_booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.post(
            "/booking/book",
            data={
                "destination_id": str(self.destination.id),
                "boat_id": str(self.boat.id),
                "trip_date": trip_date.isoformat(),
                "passenger_count": "4",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.query.count(), 1)
        self.assertIn(b"already has a booking for that date", response.data)

    def test_customer_cannot_access_admin_dashboard(self):
        self.login_as(self.customer)

        response = self.client.get("/admin/dashboard")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_mark_booking_completed(self):
        booking = Booking(
            booking_reference="BK-ISOLATED2",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="confirmed",
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.admin)
        response = self.client.post(f"/admin/bookings/{booking.id}/status/completed")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Booking, booking.id).status, "completed")

    def test_admin_can_view_booking_detail(self):
        booking = Booking(
            booking_reference="BK-DETAIL1",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            special_request="Please call before departure.",
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.admin)
        response = self.client.get(f"/admin/bookings/{booking.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please call before departure.", response.data)

    def test_admin_can_filter_bookings_by_status(self):
        pending_booking = Booking(
            booking_reference="BK-FILTER1",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="pending",
        )
        confirmed_booking = Booking(
            booking_reference="BK-FILTER2",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=4),
            passenger_count=2,
            status="confirmed",
        )
        db.session.add_all([pending_booking, confirmed_booking])
        db.session.commit()

        self.login_as(self.admin)
        response = self.client.get("/admin/bookings?status=confirmed")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BK-FILTER2", response.data)
        self.assertNotIn(b"BK-FILTER1", response.data)

    def test_customer_cannot_view_admin_booking_detail(self):
        booking = Booking(
            booking_reference="BK-DETAIL2",
            user_id=self.other_customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
        )
        db.session.add(booking)
        db.session.commit()

        self.login_as(self.customer)
        response = self.client.get(f"/admin/bookings/{booking.id}")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_boat_availability(self):
        self.login_as(self.admin)

        response = self.client.post(
            f"/admin/boats/{self.boat.id}/availability/maintenance"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Boat, self.boat.id).availability_status, "maintenance")

    def test_customer_cannot_update_boat_availability(self):
        self.login_as(self.customer)

        response = self.client.post(
            f"/admin/boats/{self.boat.id}/availability/unavailable"
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(db.session.get(Boat, self.boat.id).availability_status, "available")

    def test_unavailable_boats_are_hidden_from_customer_catalogue(self):
        from services.boat_service import BoatCatalog

        self.boat.availability_status = "maintenance"
        db.session.commit()
        self.assertEqual(BoatCatalog().available_boats(), [])
        self.assertIsNone(BoatCatalog().find_boat(self.boat.id))

    def test_admin_can_create_and_edit_boat(self):
        self.login_as(self.admin)
        response = self.client.post(
            "/admin/boats/new",
            data={
                "name": "New Island Boat",
                "fuel_type": "Diesel",
                "passenger_capacity": "12",
                "description": "A larger island-hopping boat.",
                "availability_status": "available",
                "is_active": "y",
            },
        )
        self.assertEqual(response.status_code, 302)
        boat = Boat.query.filter_by(name="New Island Boat").one()
        self.assertEqual(boat.passenger_capacity, 12)

        response = self.client.post(
            f"/admin/boats/{boat.id}/edit",
            data={
                "name": "Updated Island Boat",
                "fuel_type": "Gasoline",
                "passenger_capacity": "14",
                "description": "Updated description.",
                "availability_status": "maintenance",
                "is_active": "y",
            },
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(boat)
        self.assertEqual(boat.name, "Updated Island Boat")
        self.assertEqual(boat.availability_status, "maintenance")

    def test_customer_cannot_create_or_edit_boat(self):
        self.login_as(self.customer)
        response = self.client.get("/admin/boats/new")
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            f"/admin/boats/{self.boat.id}/edit",
            data={"name": "Tampered Boat"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(db.session.get(Boat, self.boat.id).name, "Test Boat")

    def test_customer_cannot_change_booking_status_directly(self):
        booking = Booking(
            booking_reference="BK-STATUS-OWNER",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()
        self.login_as(self.customer)
        response = self.client.post(f"/admin/bookings/{booking.id}/status/confirmed")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(db.session.get(Booking, booking.id).status, "pending")

    def test_admin_cannot_confirm_conflicting_booking(self):
        trip_date = date.today() + timedelta(days=6)
        existing_booking = Booking(
            booking_reference="BK-CONFIRMED-FIRST",
            user_id=self.other_customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=trip_date,
            passenger_count=2,
            status="confirmed",
        )
        pending_booking = Booking(
            booking_reference="BK-CONFIRM-CONFLICT",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=trip_date,
            passenger_count=2,
            status="pending",
        )
        db.session.add_all([existing_booking, pending_booking])
        db.session.commit()
        self.login_as(self.admin)
        response = self.client.post(
            f"/admin/bookings/{pending_booking.id}/status/confirmed"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Booking, pending_booking.id).status, "pending")

    def test_admin_status_lifecycle_rejects_terminal_reopen(self):
        booking = Booking(
            booking_reference="BK-TERMINAL",
            user_id=self.customer.id,
            boat_id=self.boat.id,
            destination_id=self.destination.id,
            trip_date=date.today() + timedelta(days=3),
            passenger_count=2,
            status="cancelled",
        )
        db.session.add(booking)
        db.session.commit()
        self.login_as(self.admin)
        response = self.client.post(f"/admin/bookings/{booking.id}/status/pending")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(Booking, booking.id).status, "cancelled")

    def test_registration_role_input_cannot_create_admin(self):
        with self.app.test_request_context("/auth/register", method="POST"):
            form = RegistrationForm(data={
                "full_name": "Example Customer",
                "email": "role-test@gmail.com",
                "contact_number": "09123456780",
                "password": "ValidPassword1",
                "confirm_password": "ValidPassword1",
                "role": "admin",
            })
            self.assertTrue(form.validate())
            self.assertFalse(hasattr(form, "role"))

    def test_registration_rejects_placeholder_phone_number(self):
        with self.app.test_request_context("/auth/register", method="POST"):
            form = RegistrationForm(data={
                "full_name": "Example Customer",
                "email": "sample@gmail.com",
                "contact_number": "09000000000",
                "password": "ValidPassword1",
                "confirm_password": "ValidPassword1",
            })

            self.assertFalse(form.validate())
            self.assertTrue(any("identical consecutive" in error for error in form.contact_number.errors))

    def test_unverified_login_redirects_to_otp_page(self):
        unverified_user = User(
            full_name="Unverified Customer",
            email="unverified@example.com",
            contact_number="09123456786",
            role="customer",
            is_verified=False,
        )
        unverified_user.set_password("ValidPassword1")
        db.session.add(unverified_user)
        db.session.commit()

        response = self.client.post(
            "/auth/login",
            data={"email": unverified_user.email, "password": "ValidPassword1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/verify-otp", response.headers["Location"])
        with self.client.session_transaction() as session:
            self.assertEqual(session["verification_user_id"], unverified_user.id)

    def test_admin_portal_login_is_separate_and_customer_is_forbidden(self):
        response = self.client.get("/auth/login?portal=admin")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Administrator login", response.data)

        response = self.client.post(
            "/auth/login?portal=admin",
            data={"email": self.customer.email, "password": "TestPassword123"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_login_from_admin_portal(self):
        response = self.client.post(
            "/auth/login?portal=admin",
            data={"email": self.admin.email, "password": "TestPassword123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/dashboard", response.headers["Location"])

    def test_first_admin_cli_requires_confirmation_and_hashes_password(self):
        runner = self.app.test_cli_runner()
        result = runner.invoke(
            args=["create-first-admin"],
            input="Owner Admin\nowner@example.com\n09123456789\ny\nSecureAdmin9\nSecureAdmin9\n",
        )
        self.assertEqual(result.exit_code, 0, result.output)
        admin = User.query.filter_by(email="owner@example.com").one()
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_verified)
        self.assertNotEqual(admin.password_hash, "SecureAdmin9")
        self.assertTrue(admin.check_password("SecureAdmin9"))

    def test_first_admin_cli_does_not_promote_existing_customer(self):
        runner = self.app.test_cli_runner()
        result = runner.invoke(
            args=["create-first-admin"],
            input="Owner Admin\ncustomer@example.com\n09123456789\ny\nSecureAdmin9\nSecureAdmin9\n",
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertEqual(User.query.filter_by(role="admin").count(), 0)
        self.assertEqual(db.session.get(User, self.customer.id).role, "customer")


if __name__ == "__main__":
    unittest.main()
