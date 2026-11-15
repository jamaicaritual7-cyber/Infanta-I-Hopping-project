# Four OOP Pillars in Infanta, I Hopping

The system uses object-oriented programming in the Flask application layer.

## 1. Encapsulation

Data and behavior are kept together inside classes. For example, `User` keeps password behavior inside `set_password()` and `check_password()`. `BoatCatalog` keeps boat query behavior inside a service class and protects its model dependency through `_boat_model`.

## 2. Abstraction

Complex operations are exposed through simple methods. `BoatCatalog.available_boats()` hides the database query details from route functions. `BookingStatus` defines the common interface required by every booking status.

## 3. Inheritance

`User` inherits from Flask-Login's `UserMixin`, gaining standard login behavior. `PendingStatus`, `ConfirmedStatus`, and `CancelledStatus` inherit from the abstract `BookingStatus` class.

## 4. Polymorphism

Every booking status class implements the same `label` and `badge_class` properties differently. The application can call those common properties through a `BookingStatus` reference without needing separate logic for each status. The implementation is in `services/booking_status_service.py`.

This structure keeps routes focused on HTTP requests, services focused on business rules, and models focused on database data.
