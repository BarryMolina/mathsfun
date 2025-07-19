# MathsFun 🎯

An interactive command-line math practice application that makes learning addition fun and engaging!

## Features

- **5 Difficulty Levels**: From single-digit to three-digit addition with carrying
- **Flexible Sessions**: Choose unlimited practice or set a specific number of problems
- **Real-time Feedback**: Instant responses with encouraging messages
- **Performance Tracking**: Accuracy percentages, timing, and progress statistics
- **Interactive Commands**: Skip problems, stop sessions, or exit anytime
- **Clean Interface**: Emoji-enhanced CLI for a delightful user experience

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

## Usage

### Starting the Application

```bash
python3 cli.py
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

- **Language**: Python 3
- **Dependencies**: Standard library only (lightweight!)
- **Architecture**: Single-file CLI application
- **Platform**: Cross-platform (Windows, macOS, Linux)

## Deactivating Virtual Environment

When you're done practicing:

```bash
deactivate
```

---

**Happy practicing! 🎉 Mathematics is fun when you make it interactive!**