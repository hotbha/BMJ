# Delivery Domain

## Overview
The Delivery Domain manages serviceability checks, delivery slot availability, and user address management for the BookMyJuice platform.

## Database Tables

### service_areas
Pincode-based serviceability configuration.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| pincode | VARCHAR(10) | Serviceable pincode (unique) |
| city | VARCHAR(100) | City name |
| state | VARCHAR(100) | State name |
| is_serviced | BOOLEAN | Whether this pincode is active for delivery |
| cutoff_time | TIME | Order cutoff time for same-day delivery |
| min_lead_hours | INT | Minimum lead time in hours |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

### delivery_slots
Available delivery time windows for each service area.

The `delivery_slots` table provides granular time-window selection (pre-booking specific 2-hour delivery windows) for each service area. The table schema and APIs are fully operational for time-window based delivery scheduling.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| service_area_id | BIGINT (FK) | References service_areas.id |
| slot_date | DATE | Delivery date |
| start_time | TIME | Slot start time |
| end_time | TIME | Slot end time |
| max_orders | INT | Maximum orders allowed |
| current_orders | INT | Current booked orders |
| is_active | BOOLEAN | Whether the slot is active |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

### user_addresses
Multi-address management for users.

The `user_addresses` table supports multiple delivery addresses per user. Users can add, edit, delete, and set default addresses. The "Add Address" button is always available for adding new addresses. Address is captured during signup as part of the registration flow.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| user_id | BIGINT (FK) | References users.id |
| label | VARCHAR(50) | Address label (Home, Work, Other) |
| full_name | VARCHAR(100) | Recipient full name |
| phone | VARCHAR(20) | Recipient phone number |
| address_line1 | VARCHAR(255) | Primary address |
| address_line2 | VARCHAR(255) | Secondary address (optional) |
| landmark | VARCHAR(255) | Nearby landmark (optional) |
| city | VARCHAR(100) | City |
| state | VARCHAR(100) | State |
| pincode | VARCHAR(10) | Pincode/ZIP |
| latitude | DECIMAL(10,8) | Latitude coordinate (optional) |
| longitude | DECIMAL(11,8) | Longitude coordinate (optional) |
| is_default | BOOLEAN | Whether this is the default address |
| delivery_instructions | TEXT | Special delivery instructions (optional) |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

## Entities

- **ServiceAreaEntity** (service_areas) - Pincode serviceability configuration
- **DeliverySlotEntity** (delivery_slots) - Delivery time slot management
- **UserAddressEntity** (user_addresses) - User delivery addresses

## Repositories

| Repository | Methods |
|------------|---------|
| ServiceAreaRepository | findByPincode, findByCity, findByIsServicedTrue |
| DeliverySlotRepository | findByServiceAreaIdAndSlotDateAndIsActiveTrue, findByServiceAreaIdAndSlotDateBetweenAndIsActiveTrue, findBySlotDateAfterAndIsActiveTrue |
| UserAddressRepository | findByUserId, findByUserIdAndIsDefaultTrue, setDefaultFalseForUser (custom JPQL) |

## API Endpoints (Public)

### Service Areas
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/service-areas?pincode= | Check serviceability by pincode (returns 404 if not found) |
| GET | /api/v1/delivery/service-areas/city/{city} | Find service areas by city |

### Delivery Slots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/slots?serviceAreaId=&date= | Get available slots for area on date (YYYY-MM-DD) |
| GET | /api/v1/delivery/slots/range?serviceAreaId=&startDate=&endDate= | Get slots for a date range |

## API Endpoints (Authenticated - USER/MODERATOR/ADMIN)

### Addresses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/addresses | Get current user addresses |
| POST | /api/v1/delivery/addresses | Add a new address |
| PUT | /api/v1/delivery/addresses/{id} | Update an existing address |
| DELETE | /api/v1/delivery/addresses/{id} | Delete an address |
| PATCH | /api/v1/delivery/addresses/{id}/default | Set address as default |

## DTOs

- **AddressRequest** - Input DTO for creating/updating addresses
- **AddressResponse** - Output DTO with address data (includes fromEntity factory)
- **DeliverySlotResponse** - Output DTO with slot data including computed `available` field (available = currentOrders < maxOrders && isActive)

## Relationships

```
service_areas 1---* delivery_slots
users 1---* user_addresses
```
