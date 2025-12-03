"""
Configuration constants for the BusFlow application.

This module contains all constant values used throughout the application,
including API keys, database configurations, and application settings.
Constants are written in UPPERCASE_WITH_UNDERSCORES as per naming convention.

:module: app.config
"""

# Supabase Configuration
SUPABASE_URL = 'https://eftbbsovpcapjhxpbeez.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmdGJic292cGNhcGpoeHBiZWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjk3OTEsImV4cCI6MjA4MDMwNTc5MX0.DTiQkls7wHuHL0cZJVT1yV2rFg_i8claBW49KM9a-vY'

# Flask Configuration
SECRET_KEY = 'busflow-secret-key-cse327-2024'

# User Roles
USER_ROLE = 'USER'
DRIVER_ROLE = 'DRIVER'
ADMIN_ROLE = 'ADMIN'

# Bus Status Options
BUS_STATUS_ACTIVE = 'ACTIVE'
BUS_STATUS_MAINTENANCE = 'MAINTENANCE'
BUS_STATUS_DECOMMISSIONED = 'DECOMMISSIONED'

# Booking Status Options
BOOKING_STATUS_CONFIRMED = 'CONFIRMED'
BOOKING_STATUS_CANCELLED = 'CANCELLED'

# All Available Bus Stops in the Network
ALL_BUS_STOPS = [
    'Gabtoli',
    'Mirpur 1',
    'Shyamoli',
    'Kolabagan',
    'Farmgate',
    'Karwan Bazar',
    'Shahbagh',
    'Science Lab',
    'New Market',
    'Motijheel',
    'Gulistan',
    'Mohakhali',
    'Banani',
    'Uttara',
    'Airport'
]

# Seat Configuration
MAX_SEATS_PER_BOOKING = 5
DEFAULT_TOTAL_SEATS = 40
DEFAULT_TICKET_PRICE = 50

# Seat Layout Configuration
SEAT_ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
LAST_ROW = 'K'
SEATS_PER_ROW = 4
LAST_ROW_SEATS = 5

