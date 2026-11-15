USE infanta_i_hopping;

INSERT INTO destinations
(name, municipality, province, latitude, longitude, straight_line_distance_km, straight_line_distance_nm, google_maps_url, coordinate_source, verification_status)
VALUES
('Dero Beach', 'Infanta', 'Quezon', 14.6934099, 121.6725540, 5.0, 2.7, 'https://maps.app.goo.gl/8wu4kERPgz8EiaW99', 'Project-provided preliminary coordinate', 'preliminary'),
('Sabangan Beach', 'Infanta', 'Quezon', 14.6999359, 121.6908671, 4.4, 2.4, 'https://maps.app.goo.gl/gD5m9CY3uhNieqd38', 'Project-provided preliminary coordinate', 'preliminary'),
('BIPCO Mangrove Eco-Park', 'Infanta', 'Quezon', 14.6836590, 121.6368560, 7.5, 4.1, NULL, 'Project-provided BIPCO reference coordinate', 'unverified'),
('Baluti Island', 'Real', 'Quezon', 14.6839600, 121.6177300, 8.9, 4.8, NULL, 'Project-provided preliminary coordinate', 'unverified'),
('Tulaog Beach & Cave', 'General Nakar', 'Quezon', 14.8533574, 121.6129500, 14.7, 7.9, 'https://maps.app.goo.gl/KCGg2AiqF1R4CHHfA', 'Project-provided preliminary coordinate', 'preliminary'),
('Sulok Beach', 'General Nakar', 'Quezon', 14.7944433, 121.6236620, 8.7, 4.7, NULL, 'Project-provided preliminary coordinate', 'unverified'),
('Pulong Kukok', 'Polillo', 'Quezon', 14.7060000, 121.9670000, 31.2, 16.8, 'https://www.google.com/search?kgmid=%2Fg%2F11fjmn7p5t', 'Project-provided provisional reference', 'preliminary'),
('Bato Beach', 'Polillo', 'Quezon', 14.6286375, 121.9318594, 29.8, 16.1, 'https://www.google.com/search?kgmid=%2Fg%2F11sxy7h3z_', 'Project-provided preliminary coordinate', 'unverified'),
('Gumatong Shoal', 'Panukulan', 'Quezon', 15.0591625, 121.8541719, 40.4, 21.8, 'https://www.google.com/search?kgmid=%2Fg%2F11js_8mj7f', 'Project-provided preliminary coordinate', 'unverified'),
('Pinagbanderahan Beach Resort', 'Panukulan', 'Quezon', 14.9245875, 121.8065469, 24.9, 13.4, 'https://www.google.com/search?kgmid=%2Fg%2F11jgt61q72', 'Project-provided preliminary coordinate', 'unverified'),
('Puting Bato Beach Camp', 'Burdeos', 'Quezon', 14.9162125, 122.0015781, 39.9, 21.6, 'https://www.google.com/search?kgmid=%2Fg%2F11c7wff3sm', 'Project-provided preliminary coordinate', 'unverified'),
('Anilon Island', 'Burdeos', 'Quezon', 14.9140665, 122.0281469, 42.3, 22.9, NULL, 'Project-provided preliminary coordinate', 'unverified');
