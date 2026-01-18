# Contributing to Parkinson's Disease Diagnosis System

Thank you for your interest in contributing to our Parkinson's Disease Multi-Modal Diagnosis System! We welcome contributions from developers, researchers, and healthcare professionals.

## 🎯 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, browser, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Possible implementation** approach (if you have ideas)

### Pull Requests

We actively welcome pull requests! Here's how to contribute code:

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Parkinson-disease-diagonisis.git
cd Parkinson-disease-diagonisis
```

#### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/bug-description
```

#### 3. Set Up Development Environment

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

#### 4. Make Your Changes

- Write clean, readable code
- Follow existing code style and conventions
- Add comments for complex logic
- Update documentation if needed

#### 5. Test Your Changes

**Backend Tests:**
```bash
cd backend
pytest
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

**Manual Testing:**
- Start backend: `cd backend && uvicorn app.main:app --reload`
- Start frontend: `cd frontend && npm run dev`
- Test functionality in browser

#### 6. Commit Your Changes

```bash
git add .
git commit -m "type: brief description

Detailed explanation of what changed and why"
```

**Commit Message Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

#### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then go to GitHub and create a Pull Request with:
- **Clear title** describing the change
- **Description** of what changed and why
- **Reference to related issues** (e.g., "Fixes #123")
- **Screenshots** if UI changes
- **Testing notes** - how you tested the changes

## 🎨 Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and returns
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

**Example:**
```python
def analyze_handwriting(image_path: str, model_type: str = "cnn") -> dict:
    """
    Analyze handwriting sample for Parkinson's indicators.
    
    Args:
        image_path: Path to the handwriting image file
        model_type: Type of model to use ('cnn' or 'svm')
    
    Returns:
        Dictionary containing analysis results and confidence scores
    """
    # Implementation
    pass
```

### TypeScript/React (Frontend)

- Use functional components with hooks
- Use TypeScript interfaces for props and data structures
- Follow component naming: `PascalCase` for components, `camelCase` for functions
- Use meaningful variable names
- Keep components focused and single-purpose

**Example:**
```typescript
interface AnalysisResultProps {
  diagnosis: string;
  confidence: number;
  timestamp: Date;
}

export const AnalysisResult: React.FC<AnalysisResultProps> = ({ 
  diagnosis, 
  confidence, 
  timestamp 
}) => {
  // Implementation
};
```

## 🚀 Areas for Contribution

We especially welcome contributions in these areas:

### 🤖 Machine Learning
- Improve model accuracy and performance
- Add new analysis modalities
- Optimize model inference speed
- Implement model explainability features
- Create data augmentation techniques

### 🎨 Frontend/UI
- Improve user interface and experience
- Add mobile responsiveness
- Create new visualizations for results
- Improve accessibility (WCAG compliance)
- Add internationalization (i18n)

### 🔧 Backend/API
- Optimize API performance
- Improve error handling
- Add API rate limiting
- Enhance security features
- Write comprehensive tests

### 📊 Data & Datasets
- Contribute new datasets (with proper permissions)
- Improve data preprocessing pipelines
- Add data validation and cleaning tools
- Create data augmentation scripts

### 📚 Documentation
- Improve README and documentation
- Add code examples and tutorials
- Create video tutorials
- Translate documentation
- Write blog posts about the project

### 🧪 Testing
- Write unit tests
- Add integration tests
- Create end-to-end tests
- Improve test coverage
- Add performance benchmarks

## 🔒 Security

If you discover a security vulnerability, please **DO NOT** open a public issue. Instead, email the maintainers directly at the repository owner's GitHub email.

## 📋 Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventions
- [ ] No sensitive information (API keys, passwords) in code
- [ ] PR description clearly explains changes

## 🤝 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

All contributors will be recognized in our README.md file. Thank you for helping improve healthcare technology!

## 💬 Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub
- Create an issue with the "question" label
- Reach out to the maintainers

## 🎓 First Time Contributors

New to open source? Here are some good first issues to get started:
- Look for issues labeled `good first issue`
- Look for issues labeled `help wanted`
- Documentation improvements are always welcome
- Adding tests to existing code
- Fixing typos or improving code comments

Thank you for contributing to better Parkinson's disease diagnosis! 🧠💙
