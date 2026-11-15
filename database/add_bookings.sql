USE infanta_i_hopping;

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    boat_id INT NOT NULL,
    destination_id INT NOT NULL,
    trip_date DATE NOT NULL,
    passenger_count INT NOT NULL,
    special_request TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (boat_id) REFERENCES boats(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
);
