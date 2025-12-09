CREATE DATABASE flight_book;
USE flight_book;
CREATE TABLE flights (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    flight_no       VARCHAR(10)   NOT NULL,
    airline_name    VARCHAR(50)   NOT NULL,
    origin          VARCHAR(50)   NOT NULL,
    destination     VARCHAR(50)   NOT NULL,
    departure_time  DATETIME      NOT NULL,
    arrival_time    DATETIME      NOT NULL,
    duration_minutes INT          NOT NULL,
    base_fare       DECIMAL(10,2) NOT NULL,
    total_seats     INT           NOT NULL,
    seats_available INT           NOT NULL,
    CONSTRAINT check_seats CHECK (seats_available >= 0 AND seats_available <= total_seats));
CREATE INDEX flights_route_date ON flights (origin, destination, departure_time);
INSERT INTO flights(
    flight_no,
    airline_name,
    origin,
    destination,
    departure_time,
    arrival_time,
    duration_minutes,
    base_fare,
    total_seats,
    seats_available
)
VALUES
('FB101', 'SpiceJet', 'Mumbai', 'Delhi', '2025-11-25 08:00:00', '2025-11-25 10:05:00', 125, 6500.00, 180, 160),
('FB102', 'SpiceJet', 'Delhi', 'Mumbai', '2025-11-25 13:00:00', '2025-11-25 15:10:00', 130, 6200.00, 180, 180),
('FB201', 'IndiGo', 'Chennai', 'Delhi', '2025-11-25 09:30:00', '2025-11-25 12:15:00', 165, 7200.00, 200, 185),
('FB202', 'IndiGo', 'Delhi', 'Chennai', '2025-11-25 16:00:00', '2025-11-25 18:45:00', 165, 7100.00, 200, 200),
('FB301', 'AirIndia', 'Mumbai', 'Bangalore', '2025-11-25 11:00:00', '2025-11-25 13:15:00', 135, 5800.00, 150, 140),
('FB302', 'AirIndia', 'Bangalore', 'Mumbai', '2025-11-25 18:00:00', '2025-11-25 20:20:00', 140, 6000.00, 150, 150);
/*select * from flights;
select * from flights where base_fare<=6000;
select origin from flights group by origin;
select flight_no, airline_name from flights where total_seats=200;
select avg(base_fare) as avg_fare from flights where origin='Chennai' or destination='Chennai';
select flight_no,base_fare from flights order by base_fare asc;
select id from flights order by duration_minutes desc limit 3;
select origin,avg(base_fare) as avg_fare from flights group by origin having avg(base_fare)<7000;*/
Use flight_book;
CREATE TABLE fare_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL,
    recorded_at DATETIME NOT NULL,
    dynamic_price DECIMAL(10, 2) NOT NULL,
    seats_available INT NOT NULL,
    demand_level VARCHAR(10),
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);