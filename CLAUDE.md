# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MathsFun is a Python CLI application for interactive math practice, focusing on addition problems with configurable difficulty levels. The application uses a clean, modular architecture with separation of concerns across multiple files.

## Running the Application

```bash
# Run the main application
python3 main.py

# Install dependencies (if needed)
pip install -r requirements.txt
```

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run comprehensive test suite with runner
python run_tests.py

# Run specific test files
pytest tests/test_ui.py -v
pytest tests/test_addition.py -v
pytest tests/test_session.py -v
pytest tests/test_integration.py -v
```

## Code Architecture

### Module Structure

- **`main.py`**: Entry point with main application loop and menu handling
- **`ui.py`**: User interface functions for display and input handling
- **`addition.py`**: Addition-specific logic, problem generation, and quiz execution
- **`session.py`**: Session management, results display, and timing utilities

### Core Components

- **Main Application Flow**: `main()` function in `main.py` handles menu loop and navigation
- **Problem Generation**: `ProblemGenerator` class in `addition.py` manages on-demand problem creation
- **Quiz Engine**: `run_addition_quiz()` function manages timed quiz sessions with real-time feedback
- **UI Layer**: Clean separation of input/output functions in `ui.py`
- **Session Management**: Results display and timing in `session.py`

### Key Classes and Functions

- `ProblemGenerator` (addition.py): Central class for generating math problems with difficulty range support
- `generate_problem_by_difficulty()` (addition.py): Core problem generation logic based on difficulty level
- `run_addition_quiz()` (addition.py): Main quiz loop with timer, scoring, and user interaction
- `show_results()` (session.py): Comprehensive results display with accuracy metrics and performance feedback
- `get_user_input()` (ui.py): Centralized input handling with default value support

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

## Testing Strategy

- **pytest** as main testing framework with comprehensive test coverage
- **UI Testing**: Uses mocking for `input()` and `print()` interactions
- **Property-based Testing**: Uses Hypothesis for mathematical correctness
- **Integration Tests**: End-to-end user flow scenarios
- **Test Structure**: Organized in `tests/` directory with clear separation by module

## Development Notes

- Modular architecture with clear separation of concerns
- Uses only Python standard library (no external dependencies beyond testing)
- Extensive input validation and error handling throughout
- Unicode emojis used for enhanced user experience
- Comprehensive test coverage including UI, logic, and integration tests

## Code Style and Best Practices

- Always use descriptive filenames. Avoid generic names for shared modules like "common" or "utils"