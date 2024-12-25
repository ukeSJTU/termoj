# ACM-OJ CLI Tool

A command-line interface tool for interacting with SJTU's ACM Online Judge platform. Built with Python, this tool allows you to manage problems, submit solutions, and track your submissions directly from your terminal.

## Features

- 🔐 **Secure Authentication** - Login using personal access tokens
- 📝 **Problem Management**
  - Browse and search through available problems
  - View detailed problem descriptions and requirements
  - Filter problems by various criteria
- 📤 **Solution Submission**
  - Submit solutions in multiple programming languages
  - Quick submission status checks
  - Real-time submission status updates
- 📊 **Submission Tracking**
  - View detailed test case results
  - Track submission history
  - Filter submissions by problem or language
- 👤 **User Management**
  - View profile information
  - Check authentication status

## Installation

```bash
pip install termoj
```

For development installation:

```bash
git clone https://github.com/ukeSJTU/termoj.git
cd termoj
pip install -e ".[dev]"  # Installs with development dependencies
```

## Getting Started

1. **Get Your Access Token**

   - Log in to the SJTU ACM-OJ platform
   - Navigate to Profile → API
   - Generate a new personal access token

2. **Login to CLI**

   ```bash
   termoj auth login YOUR_TOKEN
   ```

3. **Verify Authentication**
   ```bash
   termoj auth whoami
   ```

## Usage Examples

### Managing Problems

```bash
# List all available problems
termoj problems list

# Search for specific problems
termoj problems list --search "dynamic programming"

# View detailed problem information
termoj problems show 1000
```

### Submitting Solutions

```bash
# Submit a solution
termoj problems submit 1000 solution.cpp --language cpp

# Watch submission status in real-time
termoj submissions status 42 --watch
```

### Tracking Submissions

```bash
# List your recent submissions
termoj submissions list

# Filter submissions
termoj submissions list --problem 1000 --language cpp

# View detailed submission results
termoj submissions show 42
```

### Course Management

```bash
# List enrolled courses
termoj courses list

# View course details
termoj courses show COURSE_ID
```

## Requirements

- Python 3.9 or higher
- Internet connection for API access
- Personal access token from SJTU ACM-OJ platform

## Error Handling

The CLI provides clear error messages for common issues:

- Invalid authentication token
- Network connectivity problems
- Invalid command syntax
- Server-side errors

## Contributing

Contributions are welcome! The project uses:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- pytest for testing

To contribute:

1. Fork the repository
2. Create your feature branch
3. Run tests: `pytest` or `make test`
4. Submit a pull request

## License

This project is licensed under the terms included in the [LICENSE](./LICENSE) file.

## Support

For issues and feature requests, please use the GitHub issue tracker.
