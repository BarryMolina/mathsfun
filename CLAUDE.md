# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MathsFun is a Python CLI application for interactive math practice, focusing on addition problems with configurable difficulty levels. The application uses a clean, object-oriented design with a single-file architecture.

## Running the Application

```bash
# Run the main application
python3 cli.py

# Install dependencies (if needed)
pip install -r requirements.txt
```

## Code Architecture

### Core Components

- **Main Application Flow**: `main()` function handles the primary menu loop and user navigation
- **Problem Generation**: `ProblemGenerator` class manages on-demand problem creation with configurable difficulty ranges
- **Difficulty System**: Five difficulty levels from single-digit addition to three-digit numbers with carrying
- **Interactive Quiz Engine**: `run_quiz()` function manages the timed quiz session with real-time feedback

### Key Classes and Functions

- `ProblemGenerator`: Central class for generating math problems on-demand with difficulty range support
- `generate_problem_by_difficulty()`: Core problem generation logic based on difficulty level
- `run_quiz()`: Main quiz loop with timer, scoring, and user interaction
- `show_results()`: Comprehensive results display with accuracy metrics and performance feedback

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

## Development Notes

- The application is contained in a single file (`cli.py`) for simplicity
- Uses only Python standard library (no external dependencies beyond what's in requirements.txt)
- Object-oriented design with clear separation between problem generation and quiz management
- Extensive input validation and error handling throughout
- Unicode emojis used for enhanced user experience