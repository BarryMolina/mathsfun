# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MathsFun is a Python CLI application for interactive math practice, focusing on addition problems with configurable difficulty levels. The application uses a clean, layered architecture with dependency injection, Supabase integration for data persistence, and comprehensive testing.

## Running the Application

### Production Setup

```bash
# Setup virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment (requires Supabase credentials)
# Create .env file with SUPABASE_URL and SUPABASE_ANON_KEY

# Run the main application
python3 main.py
```

### Local Development Setup

For local development with Supabase, you can run a complete local stack:

```bash
# Prerequisites: Docker Desktop must be running

# Start local Supabase stack (first time may take a few minutes)
supabase start

# Copy local environment configuration
cp .env.local .env

# The application will automatically detect local environment and connect to:
# - Local API: http://127.0.0.1:54321
# - Local Database: postgresql://postgres:postgres@127.0.0.1:54322/postgres
# - Local Studio: http://127.0.0.1:54323

# Run the application
python3 main.py

# Stop local Supabase when done
supabase stop
```

#### Local Development Benefits

- 🚀 **Faster iteration** - No network latency
- 💰 **Cost-effective** - No production quota usage  
- 🔒 **Safe testing** - Isolated environment for experiments
- 📴 **Offline development** - Work without internet
- 🧪 **Consistent testing** - Reproducible environment with seed data

#### Local Environment URLs

When running locally, these services are available:
- **API URL**: http://127.0.0.1:54321
- **Studio (Admin UI)**: http://127.0.0.1:54323  
- **Database**: postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Email Testing**: http://127.0.0.1:54324

#### Switching Between Environments

The application automatically detects your environment based on the `ENVIRONMENT` variable in your `.env` file:

- **Local Development**: `ENVIRONMENT=local` (uses `.env.local` configuration)
- **Production**: `ENVIRONMENT=production` or unset (uses production Supabase credentials)

## Testing

```bash
# Run all tests (preferred method)
pytest

# Run tests with coverage (configured in pytest.ini)
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m repository        # Repository layer tests
pytest -m ui                 # UI tests only
pytest -m security          # Security tests only
pytest -m slow              # Slow tests only

# Run specific test files
pytest tests/test_ui.py -v
pytest tests/test_addition.py -v
pytest tests/test_session.py -v
pytest tests/integration/ -v

# Note: run_tests.py is for user convenience only
```

## Code Architecture

### Layered Architecture

The application follows a clean layered architecture with dependency injection, organized in a `src/` directory:

**Core Layers:**

- **Presentation**: `src/presentation/` - User interface and controllers
  - `cli/` - CLI interface (`main.py`, `ui.py`)
  - `controllers/` - Business flow controllers (`addition.py`, `addition_tables.py`, `session.py`)
- **Domain**: `src/domain/` - Business logic and models
  - `models/` - Domain entities (`User`, `QuizSession`, `ProblemAttempt`, `AdditionFactPerformance`, `MasteryLevel`)
  - `services/` - Business logic layer (`UserService`, `QuizService`, `AdditionFactService`)
- **Infrastructure**: `src/infrastructure/` - External services and data access
  - `database/` - Data persistence (`supabase_manager.py`, `repositories/`)
  - `storage/` - Local storage (`session_storage.py`)
  - `auth/` - Authentication (`auth.py`)
- **Configuration**: `src/config/` - Dependency injection (`container.py`)

**Entry Points:**

- **`main.py`** (root): Simple entry point that imports from `src/presentation/cli/main.py`
- **`src/presentation/cli/main.py`**: Main application loop and menu handling

### Core Components

- **Main Application Flow**: `main()` function handles menu loop and dependency injection setup
- **Problem Generation**: `ProblemGenerator` class in `addition.py` manages on-demand problem creation
- **Quiz Engine**: `run_addition_quiz()` function manages timed quiz sessions with real-time feedback
- **User Management**: `UserService` handles authentication and user profile management
- **Data Persistence**: Repository pattern with Supabase for user profiles and quiz sessions
- **Session Management**: Results display, timing, and local session storage

### Key Classes and Functions

**Domain/Business Logic:**

- `ProblemGenerator` (src/presentation/controllers/addition.py): Central class for generating math problems
- `UserService` (src/domain/services/): User authentication, profile management, and caching
- `QuizService` (src/domain/services/): Quiz session management and business logic
- `AdditionFactService` (src/domain/services/): Addition fact performance tracking and analytics
- `User`, `QuizSession`, `ProblemAttempt` (src/domain/models/): Core domain entities
- `AdditionFactPerformance`, `MasteryLevel` (src/domain/models/): Fact tracking domain entities

**Core Functions:**

- `run_addition_quiz()` (src/presentation/controllers/addition.py): Main quiz loop with timer, scoring, and user interaction
- `run_addition_table_quiz()` (src/presentation/controllers/addition_tables.py): Addition tables quiz with fact tracking
- `show_results()` (src/presentation/controllers/session.py): Comprehensive results display with accuracy metrics
- `show_results_with_fact_insights()` (src/presentation/controllers/addition_tables.py): Enhanced results with fact-specific insights
- `get_user_input()` (src/presentation/cli/ui.py): Centralized input handling with default value support
- `Container` (src/config/container.py): Dependency injection setup and wiring

### Difficulty Levels

The application supports 5 difficulty levels with specific mathematical constraints:

1. Single-digit numbers (0-9)
2. Two-digit numbers without carrying
3. Two-digit numbers with carrying required
4. Three-digit numbers without carrying
5. Three-digit numbers with carrying required

### Features

- Unlimited or fixed-count problem sessions
- Real-time problem generation based on difficulty range
- Comprehensive timing and accuracy tracking
- Interactive commands during quiz (next, stop, exit)
- Performance feedback with motivational messages
- **Addition Fact Performance Tracking**: Individual fact mastery tracking with personalized insights

### Addition Fact Performance Tracking

The application includes a comprehensive fact tracking system for addition tables that provides personalized learning insights:

**Key Features:**
- **Individual Fact Tracking**: Tracks performance for each unique addition fact (e.g., "7+8", "3+5")
- **Mastery Progression**: Three-level progression system (Learning → Practicing → Mastered)
- **Performance Analytics**: Accuracy, response times, and improvement tracking over time
- **Personalized Recommendations**: Identifies weak facts needing practice and celebrates mastered facts
- **Session Insights**: Enhanced results display with fact-specific analysis

**Architecture Components:**
- `AdditionFactPerformance` model: Domain entity tracking individual fact performance
- `MasteryLevel` enum: Learning progression states with clear criteria
- `AdditionFactService`: Business logic for tracking, analytics, and recommendations
- `AdditionFactRepository`: Data access layer with CRUD operations and analytics queries
- Enhanced quiz integration: Seamless tracking during addition tables practice

**Mastery Determination Logic:**
- **Learning**: < 80% accuracy OR < 5 attempts
- **Practicing**: 80-94% accuracy with 5+ attempts  
- **Mastered**: 95%+ accuracy with 10+ attempts

**User Experience:**
- Non-intrusive tracking during normal quiz flow
- Enhanced results display with actionable insights
- Practice recommendations based on performance patterns
- Progress visualization and motivation through mastery celebrations
- Sign-in encouragement for users not yet authenticated

## Testing Strategy

- **pytest** as main testing framework with comprehensive test coverage
- **UI Testing**: Uses mocking for `input()` and `print()` interactions
- **Property-based Testing**: Uses Hypothesis for mathematical correctness
- **Integration Tests**: End-to-end user flow scenarios
- **Test Structure**: Organized in `tests/` directory with clear separation by module

## Development Notes

- Clean layered architecture with dependency injection pattern
- Supabase integration for user management and data persistence
- Repository pattern for data access abstraction
- Service layer for business logic separation
- Comprehensive testing with pytest markers for different test types
- OAuth authentication flow with local callback server
- Session caching for improved user experience

## Code Style and Best Practices

- Always use descriptive filenames. Avoid generic names for shared modules like "common" or "utils"

## Development Guidelines

- Always run tests using "pytest" (configured in pytest.ini with coverage and markers)
- Use dependency injection through the Container class for new components
- Follow the layered architecture: place files in appropriate `src/` subdirectories
- Follow the repository pattern for data access in `src/infrastructure/database/repositories/`
- Keep business logic in service classes in `src/domain/services/`
- Place UI controllers in `src/presentation/controllers/`
- Use pytest markers for test categorization (unit, integration, repository, etc.)
- Mirror the source structure in the `tests/` directory

## Code Quality and Maintenance

- After writing or editing a python file, run the `mypy` command for static type checking
- Always run `black src/ tests/` after writing or editing a file to ensure consistent formatting 

## Deployment and Environment Notes

- This project uses supabase but the local docker environment isn't set up up. However, you have access to the supabase MCP server so use that for anything db-related.

## Development Workflow Guidelines

- Use git flow best practices when implementing changes:
  - Make small, focused commits with short, concise commit messages
  - Ensure you are on an appropriately named branch
  - If you are unsure if the requested changes belong on the current branch, verify with the user before continuing