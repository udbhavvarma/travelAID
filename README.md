# travelAID
 Project for Information Integration and Applications Course (Monsoon 2024)

## Features

- **Personalized Trip Planning:** Tailor travel itineraries based on your interests and preferences.
- **Real-Time Recommendations:** Access up-to-date recommendations for attractions, dining, and accommodations.
- **Dynamic Search:** Quickly find flights, hotels, and tourist spots/restros using integrated search functions.
- **User Reviews & Ratings:** Benefit from a community-driven feedback system.

## Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript, React
- **Database:** PostgreSQL/MySQL/SQLite
- **APIs:** Integration with travel APIs (e.g., Skyscanner, Google Maps, Booking.com)

## Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

- Python 3.8 or higher
- Git
- A virtual environment tool such as `venv` or `conda`
- Node.js and npm (if working with a frontend framework)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/travelAID.git
   cd travelAID
   ```

2. **Set up a virtual environment and install Python dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **(Optional) Install frontend dependencies:**

   If your project includes a separate frontend:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project root with the necessary configuration details. For example:

   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://username:password@localhost/travelaid_db
   API_KEY=your_api_key_here
   ```

5. **Initialize the database:**

   If your project involves database migrations:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Usage

1. **Start the Backend:**

   ```bash
   flask run
   ```

2. **Start the Frontend (if applicable):**

   Open another terminal and run:

   ```bash
   cd frontend
   npm start
   ```

3. **Access the Application:**

   Open your browser and navigate to [http://localhost:5000](http://localhost:5000) (or the frontend URL if different).

