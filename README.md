# Ant Colony Management System

A Python web service built with TDD and BDD methodologies for managing an ant colony with limited capacity. Each ant has a lifespan of 1 minute and 30 seconds (90 seconds), and the system enforces a maximum number of live ants at any given time.

## Features

- **Ant Lifecycle Management**: Ants automatically die after 90 seconds
- **Colony Capacity Control**: Maximum number of live ants is configurable
- **Automatic Cleanup**: Dead ants are automatically cleaned up when creating new ones
- **RESTful API**: Full CRUD operations for ant management
- **Docker Support**: Containerized deployment with Docker and docker-compose
- **Comprehensive Testing**: Unit tests (pytest) and BDD tests (Behave)

## Project Structure

```
ColoniaHormigasTDD/
├── src/
│   ├── __init__.py
│   ├── ant.py              # Ant model with 90-second lifespan
│   ├── colony.py           # Colony management with capacity control
│   └── main.py             # FastAPI web service
├── tests/
│   ├── __init__.py
│   ├── test_ant.py         # Unit tests for Ant model
│   ├── test_colony.py      # Unit tests for Colony management
│   └── test_api.py         # API integration tests
├── features/
│   ├── ant_colony.feature  # BDD feature specifications
│   └── steps/
│       └── colony_steps.py # BDD step definitions
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── Makefile
└── README.md
```

## API Endpoints

### Core Endpoints

- `GET /` - Health check and service info
- `POST /ants` - Create a new ant (if capacity allows)
- `GET /ants` - Get all alive ants
- `GET /ants/{ant_id}` - Get specific ant by ID
- `GET /colony/status` - Get colony status and statistics

### Management Endpoints

- `POST /colony/cleanup` - Manually trigger dead ant cleanup
- `PUT /colony/config?max_ants={number}` - Configure maximum colony capacity

## Installation & Usage

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run unit tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Run BDD tests:**
   ```bash
   behave features/
   ```

4. **Start the development server:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker

1. **Build and run with Docker:**
   ```bash
   docker build -t ant-colony-api .
   docker run -p 8000:8000 ant-colony-api
   ```

2. **Or use docker-compose:**
   ```bash
   docker-compose up -d
   ```

3. **For production with nginx:**
   ```bash
   docker-compose --profile production up -d
   ```

### Using Makefile

```bash
# Install dependencies
make install

# Run all tests
make test

# Run development server
make run-dev

# Build Docker image
make build

# Run with Docker
make run

# Start with docker-compose
make docker-up

# View logs
make docker-logs

# Clean up
make clean
```

## API Usage Examples

### Create an Ant
```bash
curl -X POST http://localhost:8000/ants
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "birth_time": "2023-10-20T10:30:00.000000",
  "is_alive": true,
  "age_seconds": 0.001
}
```

### Get Colony Status
```bash
curl http://localhost:8000/colony/status
```

Response:
```json
{
  "total_ants": 5,
  "alive_ants": 3,
  "dead_ants": 2,
  "max_ants": 10,
  "can_create_more": true
}
```

### Configure Colony Capacity
```bash
curl -X PUT "http://localhost:8000/colony/config?max_ants=5"
```

## Testing

The project uses both TDD and BDD approaches:

### Unit Tests (TDD)
- **Ant Model Tests**: Lifecycle, unique IDs, lifespan verification
- **Colony Tests**: Capacity management, cleanup, status reporting
- **API Tests**: HTTP endpoints, error handling, integration scenarios

### BDD Tests (Behave)
- **Feature**: Ant Colony Management
- **Scenarios**:
  - Creating ants with capacity limits
  - Automatic ant death after 90 seconds
  - Dead ant cleanup and capacity management
  - Colony status reporting

## Key Design Decisions

1. **90-Second Lifespan**: Each ant lives exactly 1 minute 30 seconds from creation
2. **Automatic Cleanup**: Dead ants are cleaned up when new ants are created
3. **Capacity Enforcement**: No new ants can be created when at maximum capacity
4. **Real-time Status**: Colony status reflects current state including dead ants
5. **RESTful Design**: Standard HTTP methods and status codes
6. **Stateless Service**: Each API call is independent (except for ant storage)

## Configuration

Default settings:
- Maximum ants: 10
- Ant lifespan: 90 seconds
- Server port: 8000

These can be modified through environment variables or API calls.

## Development

This project follows TDD/BDD principles:

1. **Test First**: All features developed with tests written first
2. **Red-Green-Refactor**: TDD cycle for unit tests
3. **Behavior Driven**: BDD scenarios for user stories
4. **Continuous Integration**: Tests must pass before deployment

## Docker Production Deployment

The included `docker-compose.yml` supports production deployment with nginx:

```bash
docker-compose --profile production up -d
```

This provides:
- Load balancing with nginx
- Health checks
- Automatic restarts
- Reverse proxy setup

## License

This project is for educational purposes demonstrating TDD/BDD practices in Python web services.