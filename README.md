# Online-cinema-project
FastAPI PostgreSQL and Docker based digital platform that allows users to select, watch, and purchase access to movies and other video materials

Online Cinema API allows users to browse and purchase movies, leave reviews, manage their watchlist, and place orders. The platform supports three user roles with different levels of access, and is fully containerized with Docker for easy deployment.


## Tech Stack

**FastAPI**  - Async web framework 
**PostgreSQL**  - Primary database
**SQLAlchemy 2.0**  - Async ORM
**Docker & Docker Compose** - Containerization 
**Poetry** - Dependency management
**JWT (python-jose)** - Authentication
**bcrypt**  -Password hashing 
**Pytest + pytest-asyncio**  - Testing
**Redis**  - Caching & background tasks
**Celery**  - Async task queue


## Project Structure
Online-cinema-project/
├── src/
│   ├── auth/              # Authentication, users, JWT tokens
│   │   ├── models.py      # User, UserGroup, Token models
│   │   ├── schemas.py     # Pydantic validation schemas
│   │   ├── service.py     # Business logic
│   │   └── router.py      # API endpoints
│   ├── movies/            # Movies catalog
│   ├── reactions/         # Likes, comments, ratings
│   ├── favorites/         # User favorites list
│   ├── cart/              # Shopping cart
│   ├── orders/            # Order management
│   └── core/              # Shared utilities
│       ├── config.py      # App configuration
│       ├── database.py    # Database connection
│       ├── security.py    # Password hashing, JWT
│       ├── dependencies.py # FastAPI dependencies
│       └── seed.py        # Initial data seeding
├── tests/
│   ├── unit/              # Unit tests (security, utils)
│   └── integration/       # Integration tests (endpoints)
├── main.py                # Application entry point
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Application container
├── pyproject.toml         # Dependencies (Poetry)
├── pytest.ini             # Test configuration
└── .env.example           # Environment variables template


## Git Flow

This project follows a feature-branch workflow:

- `main` — production-ready code
- `develop` — integration branch for completed features
- `feature/*` — individual feature branches, merged into develop via Pull Requests

Branches used in this project:
- `feature/auth` — user authentication and JWT tokens
- `feature/movies-catalog` — movies catalog with filters and search
- `feature/reactions` — likes, comments and ratings
- `feature/favorites` — user favorites list
- `feature/cart` — shopping cart
- `feature/orders` — order management

Each feature branch was developed independently, covered with tests, and merged into `develop` via a Pull Request before being released to `main`.


## Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/cinema_db

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (for account activation and password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Application
APP_HOST=http://localhost:8000
```

**Note:** For Gmail, you need to create an [App Password](https://myaccount.google.com/apppasswords) instead of using your regular password.


## API Reference

Full interactive documentation is available at `http://localhost:8080/docs` via Swagger UI.
### Authentication

**POST /auth/register**
Creates a new user account. Sends an activation link to the provided email. Password must be at least 8 characters and contain uppercase, lowercase, digit and special character.

**GET /auth/activate/{token}**
Activates a user account using the token received by email. Token is valid for 24 hours.

**POST /auth/resend-activation**
Resends the activation email if the previous token has expired.

**POST /auth/login**
Authenticates the user and returns a pair of JWT tokens — access token (30 min) and refresh token (7 days).

**POST /auth/logout**
Invalidates the refresh token so it cannot be used again.

**POST /auth/refresh**
Issues a new access token using a valid refresh token.

**GET /auth/me**
Returns the profile of the currently authenticated user. Requires a valid access token.

**POST /auth/change-password**
Changes the password for the authenticated user. Requires the current password and a new password.

**POST /auth/password-reset/request**
Sends a password reset link to the provided email if the account exists and is active.

**POST /auth/password-reset/confirm**
Sets a new password using the reset token received by email.

**PUT /auth/admin/change-group**
Changes the role of a user. Admin access only.

### Movies

**GET /movies/**
Returns a paginated list of movies. Supports the following query parameters:
- `page` — page number, default is 1
- `limit` — items per page, default is 10, maximum is 100
- `search` — search by movie title
- `year` — filter by release year
- `imdb` — filter by minimum IMDb rating
- `genre_id` — filter by genre
- `sort_by` — sort results by price, year or imdb rating

**GET /movies/{id}**
Returns detailed information about a specific movie including genres, directors, stars and certification.

**POST /movies/**
Creates a new movie in the catalog. Moderator access only.

**DELETE /movies/{id}**
Removes a movie from the catalog. Moderator access only.

### Reactions

**POST /reactions/like**
Allows an authenticated user to like or dislike a movie. Calling this endpoint again updates the existing reaction.

**GET /reactions/likes/{movie_id}**
Returns the total number of likes and dislikes for a specific movie.

**POST /reactions/comment**
Adds a comment to a movie. Supports nested replies by providing a parent_id.

**GET /reactions/comments/{movie_id}**
Returns all top-level comments for a movie, each including their replies.

**POST /reactions/rate**
Allows an authenticated user to rate a movie on a scale from 1 to 10. Calling this endpoint again updates the existing rating.

**GET /reactions/rating/{movie_id}**
Returns the average rating for a specific movie based on all user ratings.

### Favorites

**GET /favorites/**
Returns the authenticated user's favorites list. Supports the same filtering and sorting options as the movies catalog.

**POST /favorites/**
Adds a movie to the authenticated user's favorites list. Returns an error if the movie is already in favorites.

**DELETE /favorites/{movie_id}**
Removes a specific movie from the authenticated user's favorites list.

### Cart

**GET /cart/**
Returns the current user's shopping cart with all items.

**POST /cart/**
Adds a movie to the cart. Returns an error if the movie is already in the cart.

**DELETE /cart/{movie_id}**
Removes a specific movie from the cart.

**DELETE /cart/**
Clears all items from the cart.

### Orders

**POST /orders/**
Creates a new order from all movies currently in the cart. The cart is cleared after the order is created. Returns an error if the cart is empty.

**GET /orders/**
Returns all orders for the authenticated user, sorted by creation date (newest first). Each order includes status, total amount and list of purchased movies.

**POST /orders/{id}/cancel**
Cancels a pending order. Only orders with status "pending" can be canceled.

## Testing

The project has **70% test coverage** across 44 tests.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

 ## Author

 Anastasiia Tarasenko