USE infanta_i_hopping;

-- The boat name and operating details remain subject to operator confirmation.
INSERT INTO boats
    (name, fuel_type, passenger_capacity, description, photograph_path, is_active, availability_status)
SELECT
    'Habbagat',
    'Diesel',
    10,
    'A safe and reliable boat for island-hopping and beach adventures.',
    '/static/images/boats/actual_boat_photo.avif',
    1,
    'available'
WHERE NOT EXISTS (
    SELECT 1 FROM boats WHERE name = 'Habbagat'
);
