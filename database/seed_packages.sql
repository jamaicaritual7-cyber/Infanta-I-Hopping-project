USE infanta_i_hopping;

INSERT INTO packages (name, municipality, package_type, route_status) VALUES
('Dero Beach', 'Infanta', 'nearby', 'proposed'),
('Sabangan Beach', 'Infanta', 'nearby', 'proposed'),
('BIPCO Mangrove Eco-Park', 'Infanta', 'nearby', 'proposed'),
('Baluti Island', 'Real', 'nearby', 'proposed'),
('Tulaog Beach & Cave', 'General Nakar', 'nearby', 'proposed'),
('Sulok Beach', 'General Nakar', 'nearby', 'proposed'),
('Polillo Island-Hopping Package', 'Polillo', 'extended', 'quotation_required'),
('Panukulan Island-Hopping Package', 'Panukulan', 'extended', 'quotation_required'),
('Burdeos Island-Hopping Package', 'Burdeos', 'extended', 'quotation_required');

INSERT INTO pricing (package_id, amount, price_type)
SELECT id, CASE name
    WHEN 'Dero Beach' THEN 4500 WHEN 'Sabangan Beach' THEN 4000
    WHEN 'BIPCO Mangrove Eco-Park' THEN 3500 WHEN 'Baluti Island' THEN 4500
    WHEN 'Tulaog Beach & Cave' THEN 5500 WHEN 'Sulok Beach' THEN 4500
    WHEN 'Polillo Island-Hopping Package' THEN 10000 WHEN 'Panukulan Island-Hopping Package' THEN 12000
    WHEN 'Burdeos Island-Hopping Package' THEN 15000 END, 'provisional'
FROM packages;
