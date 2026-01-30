# Contributing to Ethiopia Financial Inclusion Forecast

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the issue tracker
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (Python version, OS)

### Submitting Changes

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project's coding standards:
   - Use OOP principles where appropriate
   - Add docstrings to new functions/classes
   - Follow PEP 8 style guidelines
   - Write unit tests for new functionality

3. **Test your changes**:
   ```bash
   pytest
   pytest --cov=src --cov-report=html
   ```

4. **Format and lint**:
   ```bash
   black .
   flake8 src
   ```

5. **Commit with descriptive messages**:
   ```bash
   git commit -m "feat: add new feature description"
   ```

6. **Push and create a Pull Request**:
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use Black (line length: 88)
- **Linting**: Use Flake8
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

## Testing

- Write unit tests for all new functionality
- Aim for >80% code coverage
- Tests should be in `tests/` directory
- Use descriptive test names

## Project Structure

- `src/`: Source code organized by functionality
- `tests/`: Unit tests
- `notebooks/`: Jupyter notebooks for analysis
- `dashboard/`: Streamlit dashboard application
- `reports/`: Generated reports and visualizations

## Questions?

Feel free to open an issue for questions or discussions about contributions.
