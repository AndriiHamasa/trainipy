# Trainipy API

Trainipy is an API for managing train ticket orders. It allows users to view available trains, order tickets, and receive confirmation emails upon successful orders. The API is built using Django Rest Framework (DRF) and utilizes PostgreSQL for database management, Redis for task management, and Celery for asynchronous task processing.

## Technologies Used
- **Django Rest Framework (DRF)**: For building the API.
- **PostgreSQL**: For database management.
- **Redis**: For handling message brokering.
- **Celery**: For managing asynchronous tasks (like sending emails).

When a user orders tickets, a confirmation email is sent to their registered email address.

## Setup Instructions (without Docker)

To set up the project locally without Docker, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd trainipy

2. **Clone the repository**:
   ```bash
   python -m venv venv

3. **Activate the virtual environment:**:
   ```bash
   (On Windows) venv\Scripts\activate
   (On macOS/Linux) source venv/bin/activate

4. **Install the required packages:**:
   ```bash
   pip install -r requirements.txt

5. **Set up the environment variables: Copy the .env.sample file to a new file named .env and fill in the necessary configurations (such as database credentials, email settings, etc.).**:

6. **Run migrations:**:
   ```bash
   python manage.py migrate

7. **Run the development server:**:
   ```bash
   python manage.py runserver

8. **Run Celery worker: Open a new terminal and run:**:
   ```bash
   celery -A trainipy worker -l info


## Setup Instructions (with Docker)

To run the project using Docker, follow these steps:

1. **Build and start the containers**:
   ```bash
   docker-compose up --build

2. ### Accessing the API

The API will be accessible at [http://localhost:8001/api/](http://localhost:8001/api/).


