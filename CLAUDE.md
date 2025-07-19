# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based math problem generator that uses AI to create educational addition problems. The application generates math problems of varying difficulty levels using prompt templates and AI chat completion.

## Architecture

### Core Components

- **main.py**: Entry point that orchestrates the math problem generation workflow
- **chatter.py**: AI client wrapper that handles communication with language models (supports OpenAI, X.AI/Grok)
- **jinja_helper.py**: Template processing utility for rendering prompt templates with dynamic data
- **prompts/**: Directory containing Jinja2 templates for AI prompts
- **responses/**: Directory containing example AI responses

### Template System

The application uses a two-layer template system:
1. **Prompt Templates** (`prompts/`): Jinja2 templates that generate structured prompts for the AI
2. **Response Templates** (`responses/`): Example AI responses that demonstrate expected output format

The current implementation focuses on addition problems with 5 difficulty levels (single-digit to three-digit with carrying).

### AI Integration

The `chatter` module provides a flexible AI client that supports multiple providers:
- Default: X.AI/Grok (grok-3-mini model)
- Alternative: OpenAI (GPT-3.5-turbo, GPT-4-turbo-preview)

## Environment Setup

- Requires `OPENAI_KEY` environment variable in `.env` file
- Uses python-dotenv for environment variable loading

## Common Development Tasks

### Running the Application
```bash
python main.py
```

### Key Dependencies
- openai: AI API client
- jinja2: Template rendering
- python-dotenv: Environment variable management

### Template Development
- Prompt templates are in `prompts/` directory using Jinja2 syntax
- Variables are passed from main.py data dictionary
- Response format is structured with XML-like tags for parsing

## AI Model Configuration

The application defaults to X.AI's Grok model but can be configured to use OpenAI models by modifying the `chatter()` function call in main.py:
- For OpenAI: `chatter(api_key, model=GPT3_TURBO, url=OPENAI_URL)`
- For Grok (default): `chatter(api_key, model=GROK_3_MINI, url=XAI_URL)`