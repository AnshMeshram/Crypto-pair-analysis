# Contributing to Crypto Pair Analytics

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-pair-analytics.git
   cd crypto-pair-analytics
   ```

3. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up your environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and modular

### Testing

- Test your changes locally before submitting
- Run `python check_db.py` to verify database integrity
- Test with `python run_ingest.py` for ingestion validation

### Commit Messages

- Use clear, descriptive messages
- Start with verb: "Add", "Fix", "Improve", "Refactor"
- Example: "Add Kalman filter for dynamic hedge estimation"

## Areas for Contribution

### High Priority

- ✅ Kalman filter implementation for dynamic hedge ratio
- ✅ Robust regression (Huber/Theil-Sen) for outlier handling
- ✅ Enhanced alert system with multiple rules
- ✅ Email/Telegram notifications

### Medium Priority

- 📊 Additional technical indicators (Bollinger Bands, RSI, MACD)
- 🔄 Support for more exchanges (Coinbase, Kraken, Bybit)
- 📈 Mini backtest module with performance metrics
- 🗂️ CSV historical data importer

### Low Priority

- 🎨 UI/UX improvements
- 📚 Additional documentation
- 🧪 Unit tests and CI/CD

## Pull Request Process

1. Update `README.md` with any new features or changes
2. Ensure all code passes local testing
3. Write a clear PR description explaining the changes
4. Reference any related issues (e.g., "Fixes #123")
5. Request review from maintainers

## Reporting Bugs

Found an issue? Please create a GitHub Issue with:

- 📝 Clear description of the bug
- 🔍 Steps to reproduce
- 🖼️ Screenshots if applicable
- 🖥️ Your system info (OS, Python version)

## Feature Requests

Have an idea? Open an Issue with:

- 💡 Description of the feature
- 📋 Use case and why it's useful
- 💬 Suggested implementation approach

## Questions?

- Check existing Issues for similar questions
- Review the README for common setup issues
- Create a Discussion or Issue for help

---

Thank you for contributing to make Crypto Pair Analytics better! 🚀
