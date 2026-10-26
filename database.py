
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rural_services.db")

DISTRICTS = [
    "Ariyalur",
    "Chennai",
    "Coimbatore",
    "Madurai",
    "Salem",
    "Vellore",
    "Tiruchirappalli",
    "Thanjavur",
    "Tirunelveli",
    "Erode",
    "Dindigul",
    "Thiruvannamalai"
]

# District Collector Office contacts.
# Verify the numbers using the official district websites.
DISTRICT_CONTACTS = {
    "Ariyalur": "04329-228336",
    "Chennai": "044-25228025",
    "Coimbatore": "0422-2301114",
    "Madurai": "0452-2531110",
    "Salem": "0427-2452244",
    "Vellore": "0416-2252345",
    "Tiruchirappalli": "0431-2415358",
    "Thanjavur": "04362-230102",
    "Tirunelveli": "0462-2501222",
    "Erode": "0424-2266700",
    "Dindigul": "0451-2461199",
    "Thiruvannamalai": "04175-233333"
}

# General helpline numbers
EMERGENCY_CONTACTS = {
    "Ambulance": "108",
    "Emergency": "112",
    "Health Helpline": "104"
}

# Agriculture Department official website
AGRICULTURE_WEBSITE = (
    "https://tnagriculture.in/Agritech_new/home/contact/en"
)

# Agriculture Department contact number.
# This is a general department contact, not a district office number.
AGRICULTURE_CONTACT = "044-28583323"


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create districts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        # Create services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                contact TEXT DEFAULT 'Not provided'
            )
        """)

        # Insert districts without duplicates
        for district in DISTRICTS:
            cursor.execute("""
                INSERT OR IGNORE INTO districts (name)
                VALUES (?)
            """, (district,))

        # Add or update service information for each district
        for district in DISTRICTS:

            collector_contact = DISTRICT_CONTACTS.get(
                district,
                "Check official district website"
            )

            services = [
                (
                    district,
                    "Healthcare",
                    "Healthcare Services",
                    "Government hospitals and Primary Health Centres. "
                    "For local medical facility details, contact the "
                    "district health department.",
                    "Health Helpline: 104 | Ambulance: 108"
                ),
                (
                    district,
                    "Education",
                    "Educational Services",
                    "For government schools, colleges and education "
                    "schemes, contact the district education office.",
                    "Collector Office: " + collector_contact
                ),
                (
                    district,
                    "Agriculture",
                    "Agricultural Services",
                    "For farmer assistance, agricultural schemes and "
                    "local agriculture office information, contact "
                    "the Agriculture Department.",
                    "Agriculture Department: "
                    + AGRICULTURE_CONTACT
                    + " | Website: "
                    + AGRICULTURE_WEBSITE
                ),
                (
                    district,
                    "Agriculture",
                    "Agriculture Office",
                    "Contact the Agriculture Department for information "
                    "about local agriculture offices and farmer services.",
                    "Agriculture Department: "
                    + AGRICULTURE_CONTACT
                    + " | Website: "
                    + AGRICULTURE_WEBSITE
                ),
                (
                    district,
                    "Government Office",
                    "District Collector Office",
                    "Contact the district administration for official "
                    "district-level information.",
                    collector_contact
                ),
                (
                    district,
                    "Emergency",
                    "Emergency Helplines",
                    "General emergency and health helpline information.",
                    "Ambulance: 108 | Emergency: 112 | Health: 104"
                )
            ]

            for service in services:

                cursor.execute("""
                    SELECT id FROM services
                    WHERE district = ?
                      AND category = ?
                      AND title = ?
                """, (
                    service[0],
                    service[1],
                    service[2]
                ))

                existing = cursor.fetchone()

                if existing:
                    # Update the existing record
                    cursor.execute("""
                        UPDATE services
                        SET description = ?,
                            contact = ?
                        WHERE id = ?
                    """, (
                        service[3],
                        service[4],
                        existing[0]
                    ))

                else:
                    # Insert a new record
                    cursor.execute("""
                        INSERT INTO services
                        (
                            district,
                            category,
                            title,
                            description,
                            contact
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, service)

        conn.commit()

        print("Database updated successfully!")
        print("12 districts checked.")
        print("Healthcare contacts updated.")
        print("Education services updated.")
        print("Agriculture Office and Services updated.")
        print("Emergency contacts updated.")

    except sqlite3.Error as error:
        conn.rollback()
        print("Database error:", error)

    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
