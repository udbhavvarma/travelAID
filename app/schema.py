mediated_schema = {
    "hotels": {
        "columns": [
            "address",
            "city",
            "country",
            "hotel_description",
            "hotel_facilities",
            "hotel_star_rating",
            "property_id",
            "property_name",
            "room_count",
            "room_type",
            "site_review_rating",
            "sitename",
            "state",
            "price"
        ],
        "sources": [
            {
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "bookingcomdata",
                "table": "hotels"
            },
            {
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "goibibodata",
                "table": "hotels"
            }
        ]
    },

    "flights": {
        "columns": [
            "flight_date",
            "airline",
            "flight_num",
            "class",
            "dep_city",
            "dep_time",
            "arr_city",
            "arr_time",
            "duration",
            "price",
            "stops",
            "flight_id"
        ], 
        "sources": [
            {
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "bookingcomdata",
                "table": "flights"
            },
            {
                            
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "goibibodata",
                "table": "flights"
            
            }
    
        ]
    },

    "tourist_spots": {
        "columns": [
            "spot_id",
            "name_spot",
            "type_spot",
            "description_spot",
            "location_address",
            "location_locality",
            "location_city",
            "contact_phone",
            "contact_email",
            "contact_website",
            "category",
            "rating_average",
            "pricing_currency",
            "pricing_price_level",
            "accessibility_wheelchair_accessible",
            "accessibility_braille_menu",
            "accessibility_service_animals_allowed",
            "accessibility_elevator_available",
            "accessibility_accessible_restrooms",
            "amenities_wifi",
            "amenities_parking_available",
            "amenities_outdoor_seating",
            "amenities_live_music",
            "sitename"
        ],

        "sources": [
            {
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "bookingcomdata",
                "table": "tourist_spots"
            },
            {
                            
                "host": "127.0.0.1",
                "user": "root",
                "password": "7117",
                "database": "goibibodata",
                "table": "tourist_spots"

            }
        ]
    }        
}
