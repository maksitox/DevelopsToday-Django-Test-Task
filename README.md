# Travel Planner

A RESTful API for managing travel projects and places, integrated with the Art Institute of Chicago API.

## Features
- **Travel Projects**: Create, list, update, and delete projects.
- **Places**: Add places from Art Institute of Chicago, track "visited" status.
- **Completion**: Projects are automatically marked as completed when all places are visited.
- **Validation**: Ensures places exist in the external API and prevents deletion of projects with visited places.

## Setup & Running

### Requirements
- Docker & Docker Compose
- Or Python 3.11+

### with Docker (Recommended)
1. Clone the repository.
2. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Build and run:
   ```bash
   docker-compose up --build
   ```
4. Access the API at `http://localhost:8000/api/`.

### Local Development
1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (or use default settings).
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Run server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Projects
- `GET /api/projects/`: List all projects.
- `POST /api/projects/`: Create a project.
  - Body: `{"name": "Trip", "initial_places": [{"external_id": 129884}]}`
- `GET /api/projects/{id}/`: Get project details.
- `DELETE /api/projects/{id}/`: Delete project (if no visited places).
- `POST /api/projects/{id}/places/`: Add a place.
  - Body: `{"external_id": 129884}`
- `GET /api/projects/{id}/places/`: List places in project.

### Places
- `GET /api/places/{id}/`: Get place details.
- `PATCH /api/places/{id}/`: Update place (e.g., mark visited).
  - Body: `{"visited": true, "notes": "Loved it!"}`

## Testing
Run tests using Docker:
```bash
docker-compose run --rm web python manage.py test api
```

## Postman Collection
A Postman collection is included in `travel_planner.postman_collection.json`. Import it into Postman to test the API.
