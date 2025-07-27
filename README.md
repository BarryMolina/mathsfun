# MathsFun 🎯

An interactive command-line math practice application that makes learning addition fun and engaging!

## Features

- **5 Difficulty Levels**: From single-digit to three-digit addition with carrying
- **Flexible Sessions**: Choose unlimited practice or set a specific number of problems
- **Real-time Feedback**: Instant responses with encouraging messages
- **Performance Tracking**: Accuracy percentages, timing, and progress statistics
- **Addition Fact Mastery**: Track individual fact performance and mastery levels
- **User Authentication**: Google OAuth for personalized learning
- **Interactive Commands**: Skip problems, stop sessions, or exit anytime
- **Clean Interface**: Emoji-enhanced CLI for a delightful user experience
- **Local Development**: Complete offline development environment with local Supabase

## Installation

### Prerequisites
- Python 3.6 or higher

### Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd mathsfun
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   
   **For Local Development (Recommended)**:
   ```bash
   # Prerequisites: Docker Desktop must be running
   
   # Start local Supabase stack
   supabase start
   
   # Copy local environment configuration
   cp .env.local .env
   ```
   
   **For Production Use**:
   ```bash
   # Create .env file with your Supabase credentials
   echo "SUPABASE_URL=your_supabase_url" > .env
   echo "SUPABASE_ANON_KEY=your_supabase_anon_key" >> .env
   ```

## Usage

### Starting the Application

```bash
python3 main.py
```

### Main Menu

When you start MathsFun, you'll see the main menu:
- **1. Addition** - Start addition practice
- **Type 'exit'** - Quit the application

### Setting Up a Practice Session

1. **Choose Difficulty Range**
   - Select your lowest difficulty level (1-5)
   - Select your highest difficulty level (1-5)
   - The app will randomly generate problems within this range

2. **Set Number of Problems**
   - Enter `0` for unlimited practice (recommended for open-ended sessions)
   - Enter any positive number for a fixed-length quiz

### Difficulty Levels

| Level | Description |
|-------|-------------|
| 1 | Two single-digit numbers (0-9) |
| 2 | Two two-digit numbers, no carrying |
| 3 | Two two-digit numbers with carrying |
| 4 | Two three-digit numbers, no carrying |
| 5 | Two three-digit numbers with carrying |

### During Practice

- **Enter your answer** as a number
- **Commands available**:
  - `next` - Skip the current problem
  - `stop` - End session and see results
  - `exit` - Quit the application

### Example Session

```
🎯 Welcome to MathsFun! 🎯
Let's make math practice fun and interactive!

📚 Main Menu:
1. Addition

Type 'exit' to quit the application
Select an option: 1

🔢 Addition Mode Selected!

🎚️  Difficulty Levels:
1. Two single-digit numbers
2. Two two-digit numbers, no carrying
3. Two two-digit numbers with carrying
4. Two three-digit numbers, no carrying
5. Two three-digit numbers with carrying

Enter lowest difficulty level (default: 1): 2
Enter highest difficulty level (default: 5): 4
Number of problems (0 for unlimited) (default: 0): 10

📋 Settings:
   Difficulty: 2 to 4
   Problems: 10

✅ Ready to start! 10 problems prepared.
Press Enter when you're ready to start the timer and begin...

🎯 Timer started! You have 10 problems to solve.
Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)

📝 Problem 1/10: 45 + 23
Your answer: 68
✅ Correct! Great job!

📝 Problem 2/10: 156 + 321
Your answer: 477
✅ Correct! Great job!
```

## Results and Feedback

After completing a session, you'll see detailed results including:
- Total problems presented
- Correct answers and accuracy percentage
- Time taken and average time per problem
- Motivational feedback based on performance
- Number of problems skipped

## Tips for Best Experience

1. **Start with lower difficulties** and gradually increase as you improve
2. **Use unlimited mode** for relaxed practice sessions
3. **Set specific problem counts** for timed challenges
4. **Don't worry about mistakes** - the app provides the correct answer and encourages you to keep going!

## Technical Details

- **Language**: Python 3.8+
- **Architecture**: Clean layered architecture with dependency injection
- **Database**: Supabase (PostgreSQL) with local development support
- **Authentication**: OAuth 2.0 with PKCE (Google)
- **Testing**: Comprehensive test suite with pytest
- **Platform**: Cross-platform (Windows, macOS, Linux)

## Development

For local development, see the complete setup instructions in [CLAUDE.md](CLAUDE.md) including:
- Local Supabase stack setup
- Environment configuration  
- Testing procedures
- Code quality tools

### Quick Start for Developers

```bash
# Clone and setup
git clone <repository-url>
cd mathsfun
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start local development environment
supabase start
cp .env.local .env

# Run tests
pytest

# Start application
python3 main.py
```

## Deactivating Virtual Environment

When you're done practicing:

```bash
deactivate
```

---

**Happy practicing! 🎉 Mathematics is fun when you make it interactive!**