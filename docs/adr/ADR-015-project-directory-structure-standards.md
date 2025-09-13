# Architecture Decision Record (ADR)

## ADR-015: Universal Project Directory Structure Standards

**Status:** Accepted  
**Date:** 13-09-25-13h-30m-00s  
**Session:** 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl  
**Todo:** Universal ADR coverage implementation  
**Deciders:** Will Robinson, Development Team

### Context

Software projects across different frameworks, languages, and domains consistently struggle with directory organization as codebases grow from initial prototypes to production systems. Common issues include:

- **Inconsistent Organization**: No standard approach to organizing code, assets, configurations, and documentation
- **Poor Scalability**: Flat directory structures that become unmaintainable as projects grow
- **Framework Confusion**: Different frameworks suggest different structures, creating team confusion
- **Discovery Problems**: Developers unable to quickly locate relevant files and functionality
- **Maintenance Overhead**: Poor structure increases refactoring difficulty and code navigation time
- **Cross-Project Inconsistency**: Each project using different organizational patterns

This problem occurs across all technology stacks (Python/Flask, Node.js/Express, Django, Ruby on Rails, etc.) and significantly impacts development productivity and codebase maintainability.

### Decision

**We will establish universal directory structure standards that apply across all projects regardless of framework or technology stack:**

1. **Functional Organization**: Organize by business functionality first, technical concerns second
2. **Separation of Concerns**: Clear boundaries between application logic, configuration, assets, and infrastructure
3. **Scalable Hierarchy**: Directory structure that grows naturally with project complexity
4. **Framework Agnostic**: Patterns that work across all web frameworks and project types
5. **Documentation Integration**: Documentation lives within the codebase in logical locations
6. **Environment Configuration**: Clear separation of environment-specific configurations

**Universal Directory Architecture:**
```
project/
├── app/                    # Application code (business logic)
├── config/                 # Configuration files
├── docs/                   # Documentation
├── infrastructure/         # Deployment, infrastructure, DevOps
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # Template files (if applicable)
├── tests/                  # Test suites
├── tools/                  # Development tools, scripts, utilities
└── [framework-specific]/   # Framework-required directories
```

### Rationale

**Primary drivers:**

- **Universal Applicability**: Structure works for all project types and technology stacks
- **Cognitive Load Reduction**: Consistent patterns reduce time to understand new codebases  
- **Scalability**: Structure accommodates projects from MVP to enterprise scale
- **Team Efficiency**: Standardized organization reduces onboarding time and increases productivity
- **Maintainability**: Clear separation of concerns simplifies refactoring and debugging
- **Cross-Project Knowledge Transfer**: Developers can navigate any project using the same mental model

**Technical benefits:**

- Clear separation between business logic and infrastructure concerns
- Predictable file location patterns reduce search and navigation time
- Modular organization enables easier testing and code reuse
- Documentation co-location with relevant code improves knowledge management
- Environment-specific configuration management reduces deployment issues

### Alternatives Considered

- **Option A: Framework-specific organization** - Rejected due to lack of consistency across projects
- **Option B: Flat directory structure** - Rejected due to poor scalability as projects grow  
- **Option C: Technical layer organization** - Rejected because it separates related business functionality
- **Option D: Domain-driven directory structure** - Considered but too complex for smaller projects

### Consequences

**Positive:**

- ✅ **Universal Standards**: Consistent organization across all projects regardless of technology
- ✅ **Improved Navigation**: Developers can quickly locate files using predictable patterns
- ✅ **Enhanced Scalability**: Structure grows naturally from small projects to large systems
- ✅ **Reduced Onboarding Time**: New team members understand project layout immediately
- ✅ **Better Maintainability**: Clear separation of concerns simplifies code maintenance
- ✅ **Cross-Team Collaboration**: Consistent patterns enable knowledge sharing across projects

**Negative:**

- ➖ **Migration Effort**: Existing projects may require significant restructuring
- ➖ **Framework Conflicts**: Some frameworks have strong opinions about directory structure
- ➖ **Initial Overhead**: Teams must learn and enforce new organizational patterns
- ➖ **Tool Configuration**: IDEs and tools may need reconfiguration for new structure

**Neutral:**

- 🔄 **Team Training**: All developers must understand and follow directory organization standards  
- 🔄 **Documentation Requirements**: Need comprehensive documentation of directory purposes and conventions
- 🔄 **Enforcement Mechanisms**: Require tooling or processes to maintain structural consistency

### Implementation Notes

**1. Universal Base Structure:**

```
project/
├── app/                          # Core application business logic
│   ├── models/                   # Data models, entities, domain objects
│   ├── services/                 # Business logic, use cases, application services
│   ├── controllers/              # Request handlers, route controllers, API endpoints
│   ├── repositories/             # Data access layer, database interactions
│   ├── utils/                    # Shared utilities, helpers, common functions
│   ├── middleware/               # Request/response middleware, filters, interceptors
│   ├── exceptions/               # Custom exception classes and error handling
│   └── __init__.py              # Application factory, initialization code
├── config/                       # Configuration management
│   ├── environments/             # Environment-specific configurations
│   │   ├── development.py       # Development environment settings
│   │   ├── production.py        # Production environment settings
│   │   ├── testing.py           # Test environment settings
│   │   └── staging.py           # Staging environment settings
│   ├── database.py              # Database configuration and connection settings
│   ├── logging.py               # Logging configuration and setup
│   ├── security.py              # Security settings, authentication, authorization
│   └── settings.py              # Base configuration class and common settings
├── docs/                         # Project documentation
│   ├── adr/                     # Architecture Decision Records
│   ├── api/                     # API documentation, OpenAPI specs
│   ├── deployment/              # Deployment guides and procedures
│   ├── development/             # Development setup and guidelines
│   ├── user/                    # User guides and manuals
│   └── README.md               # Main project documentation
├── infrastructure/               # Infrastructure as code, deployment
│   ├── docker/                  # Docker configurations, Dockerfiles
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── docker-compose.prod.yml
│   ├── kubernetes/              # Kubernetes manifests and configurations
│   ├── terraform/               # Infrastructure provisioning scripts
│   ├── ansible/                 # Configuration management playbooks
│   ├── scripts/                 # Deployment and automation scripts
│   │   ├── deploy.sh
│   │   ├── backup.sh
│   │   └── migrate.sh
│   └── monitoring/              # Monitoring and alerting configurations
├── static/                       # Static assets (web applications)
│   ├── css/                     # Stylesheets
│   │   ├── base/               # Base styles, resets, variables
│   │   ├── components/         # Component-specific styles
│   │   ├── layouts/            # Layout-specific styles
│   │   └── main.css            # Main stylesheet entry point
│   ├── js/                      # JavaScript files
│   │   ├── components/         # Reusable JavaScript components
│   │   ├── pages/              # Page-specific JavaScript
│   │   ├── utils/              # JavaScript utilities and helpers
│   │   └── main.js             # Main JavaScript entry point
│   ├── images/                  # Image assets
│   │   ├── icons/              # Icon files (SVG, PNG)
│   │   ├── photos/             # Photographic content
│   │   └── graphics/           # Graphics and illustrations
│   └── fonts/                   # Font files and typography assets
├── templates/                    # Template files (if using server-side rendering)
│   ├── base/                    # Base templates, core layout templates
│   ├── layouts/                 # Layout templates for different page types
│   ├── pages/                   # Page-specific templates
│   ├── components/              # Reusable template components
│   ├── macros/                  # Template macros and includes
│   │   ├── base/               # Core foundational macros
│   │   ├── ui/                 # UI component macros
│   │   ├── forms/              # Form-related macros
│   │   └── utilities/          # Helper and utility macros
│   └── emails/                  # Email template files
├── tests/                        # Test suites and testing utilities
│   ├── unit/                    # Unit tests organized by application module
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   ├── fixtures/                # Test data and fixtures
│   ├── mocks/                   # Mock objects and test doubles
│   └── conftest.py             # Test configuration and shared fixtures
├── tools/                        # Development tools, scripts, utilities
│   ├── scripts/                 # Automation scripts, data processing
│   │   ├── seed_data.py        # Database seeding scripts
│   │   ├── generate_docs.py    # Documentation generation
│   │   └── cleanup.py          # Maintenance and cleanup scripts
│   ├── linters/                 # Code quality and linting configurations
│   │   ├── .pylintrc           # Python linting rules
│   │   ├── .eslintrc.json      # JavaScript linting rules
│   │   └── .pre-commit-config.yaml # Pre-commit hooks configuration
│   ├── generators/              # Code generation tools and templates
│   └── analysis/                # Code analysis tools and reports
└── migrations/                   # Database migration files (if applicable)
    ├── versions/                # Individual migration files
    └── alembic.ini             # Migration tool configuration
```

**2. Framework-Specific Adaptations:**

**Flask Applications:**
```
project/
├── app/                     # Flask application package
│   ├── __init__.py         # Application factory
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # Blueprint route handlers
│   ├── services/           # Business logic services
│   └── utils/              # Flask utilities, decorators
├── instance/               # Flask instance folder (sensitive configs)
├── migrations/             # Flask-Migrate database migrations
└── wsgi.py                # WSGI application entry point
```

**Django Applications:**
```
project/
├── apps/                   # Django applications
│   ├── core/              # Core app with shared utilities
│   ├── users/             # User management app
│   └── [feature_apps]/    # Feature-specific Django apps
├── project/               # Django project configuration
│   ├── settings/          # Split settings by environment
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
└── locale/                # Internationalization files
```

**FastAPI Applications:**
```
project/
├── app/
│   ├── api/               # API route definitions
│   │   ├── endpoints/     # API endpoint handlers
│   │   └── dependencies/  # Dependency injection functions
│   ├── core/              # Core configuration and security
│   ├── models/            # Pydantic models, database models
│   └── services/          # Business logic services
└── alembic/               # Database migrations for FastAPI
```

**Node.js/Express Applications:**
```
project/
├── src/                   # Source code
│   ├── controllers/       # Express route handlers
│   ├── models/            # Data models (Mongoose, Sequelize)
│   ├── services/          # Business logic services
│   ├── middleware/        # Express middleware
│   └── utils/             # JavaScript utilities
├── public/                # Static assets (equivalent to static/)
└── views/                 # Template files (equivalent to templates/)
```

**3. Environment-Specific Configuration Management:**

```python
# config/environments/base.py
class BaseConfig:
    """Base configuration class with common settings"""
    APP_NAME = "Universal Application"
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Feature flags
    FEATURE_REGISTRATION = True
    FEATURE_API_VERSIONING = True

# config/environments/development.py
class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL', 'sqlite:///dev.db')
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific features
    DEBUG_TOOLBAR = True
    LIVE_RELOAD = True

# config/environments/production.py  
class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    DATABASE_URL = os.environ.get('PROD_DATABASE_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Performance settings
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

# config/settings.py
def get_config():
    """Factory function to return appropriate configuration"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'staging': StagingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)
```

**4. Documentation Organization Standards:**

```
docs/
├── adr/                         # Architecture Decision Records
│   ├── ADR-001-example.md      # Individual decision records
│   ├── ADR-002-database.md
│   └── template.md             # ADR template for consistency
├── api/                         # API documentation
│   ├── openapi.yaml            # OpenAPI specification
│   ├── endpoints/              # Detailed endpoint documentation
│   └── examples/               # API usage examples
├── deployment/                  # Deployment and operations
│   ├── production.md           # Production deployment guide
│   ├── monitoring.md           # Monitoring and alerting setup
│   └── troubleshooting.md      # Common issues and solutions
├── development/                 # Developer documentation
│   ├── setup.md               # Development environment setup
│   ├── contributing.md        # Contribution guidelines
│   ├── coding-standards.md    # Code style and standards
│   └── testing.md             # Testing guidelines and practices
├── user/                        # End user documentation
│   ├── user-guide.md          # User manual and guides
│   ├── faq.md                 # Frequently asked questions
│   └── tutorials/             # Step-by-step tutorials
└── README.md                   # Main project overview and quick start
```

**5. Asset Organization Patterns:**

```
static/
├── css/
│   ├── base/                   # Foundation styles
│   │   ├── reset.css          # CSS reset/normalize
│   │   ├── variables.css      # CSS custom properties
│   │   └── typography.css     # Base typography
│   ├── components/            # Component-specific styles
│   │   ├── buttons.css        # Button styles
│   │   ├── forms.css          # Form styles
│   │   ├── navigation.css     # Navigation styles
│   │   └── modals.css         # Modal styles
│   ├── layouts/               # Layout-specific styles
│   │   ├── dashboard.css      # Dashboard layout
│   │   ├── landing.css        # Landing page layout
│   │   └── admin.css          # Admin panel layout
│   ├── utilities/             # Utility classes
│   │   ├── spacing.css        # Margin/padding utilities
│   │   ├── colors.css         # Color utilities
│   │   └── display.css        # Display utilities
│   └── main.css              # Main CSS entry point
├── js/
│   ├── components/            # Reusable JavaScript components
│   │   ├── modal.js          # Modal functionality
│   │   ├── form-validator.js # Form validation
│   │   └── data-table.js     # Data table interactions
│   ├── pages/                # Page-specific JavaScript
│   │   ├── dashboard.js      # Dashboard functionality
│   │   ├── profile.js        # User profile page
│   │   └── settings.js       # Settings page
│   ├── utils/                # JavaScript utilities
│   │   ├── api-client.js     # API communication helper
│   │   ├── date-formatter.js # Date formatting utilities
│   │   └── dom-helpers.js    # DOM manipulation helpers
│   └── main.js              # Main JavaScript entry point
└── images/
    ├── icons/                 # Icon files
    │   ├── svg/              # SVG icons
    │   └── png/              # PNG icons for fallbacks
    ├── photos/               # Photographic content
    └── graphics/             # Graphics and illustrations
```

**6. Testing Organization Standards:**

```
tests/
├── unit/                      # Unit tests mirror app structure
│   ├── models/
│   │   ├── test_user.py      # Test user model
│   │   └── test_product.py   # Test product model
│   ├── services/
│   │   ├── test_auth_service.py
│   │   └── test_email_service.py
│   └── utils/
│       └── test_helpers.py
├── integration/               # Integration tests
│   ├── test_api_endpoints.py # API integration tests
│   ├── test_database.py      # Database integration tests
│   └── test_external_services.py
├── e2e/                      # End-to-end tests
│   ├── test_user_workflow.py # Complete user journeys
│   └── test_admin_workflow.py
├── fixtures/                 # Test data and fixtures
│   ├── sample_data.json     # Sample JSON data
│   ├── test_images/         # Test image files
│   └── database_fixtures.py # Database test fixtures
├── mocks/                    # Mock objects and test doubles
│   ├── mock_external_api.py # External API mocks
│   └── mock_services.py     # Service layer mocks
└── conftest.py              # Pytest configuration and shared fixtures
```

**7. Tool and Script Organization:**

```
tools/
├── scripts/                   # Automation and utility scripts
│   ├── seed_database.py      # Database seeding
│   ├── backup_data.py        # Data backup utilities
│   ├── generate_test_data.py # Test data generation
│   └── cleanup_logs.py       # Log cleanup and rotation
├── linters/                   # Code quality configurations
│   ├── .pylintrc            # Python linting rules
│   ├── .flake8             # Python style checking
│   ├── .eslintrc.json      # JavaScript linting rules
│   ├── .stylelintrc        # CSS linting rules
│   └── .pre-commit-config.yaml # Pre-commit hooks
├── generators/                # Code generation tools
│   ├── model_generator.py    # Generate model boilerplate
│   ├── api_generator.py      # Generate API endpoints
│   └── test_generator.py     # Generate test templates
├── analysis/                  # Code analysis and metrics
│   ├── complexity_report.py  # Code complexity analysis
│   ├── dependency_graph.py   # Dependency visualization
│   └── coverage_report.py    # Test coverage reporting
└── development/               # Development environment tools
    ├── setup_dev_env.py     # Development environment setup
    ├── reset_database.py    # Database reset for development
    └── run_tests.py         # Test execution wrapper
```

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-13h-30m-00s | 57ad43d3-ad12-46e8-8f3e-abd7c0ebc32c.jsonl | Universal ADR coverage | Initial creation | Document universal directory structure standards | Establish consistent organization patterns across all projects |

---

**Impact Assessment:** High - This establishes fundamental project organization standards that affect all development work.

**Review Required:** Mandatory - All team members and new projects must follow these directory structure standards.

**Next Steps:**
1. Create project templates that implement this directory structure by default
2. Migrate existing projects to follow these standards where practical
3. Establish tooling to validate and enforce directory structure compliance
4. Create IDE templates and snippets that support this organization pattern
5. Document framework-specific adaptations for common technology stacks