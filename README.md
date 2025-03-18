# Django Modular Engine

A demo Django application that provides a dynamic module system, enabling plug-and-play module development, registration, installation, and management within your Django project.

## Table of Contents

- [Getting Started](#getting-started)
  - [Running with a Virtual Environment](#running-with-a-virtual-environment)
  - [Running with Docker](#running-with-docker)
- [User Management](#user-management)
  - [Creating Users](#creating-users)
  - [Testing Different User Roles](#testing-different-user-roles)
- [Module Management](#module-management)
  - [Viewing Available Modules](#viewing-available-modules)
  - [Troubleshooting Module Registration](#troubleshooting-module-registration)
- [More Information](#more-information)

## Getting Started

### Running with a Virtual Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/dwisulfahnur/dj-modular
   cd dj-modular
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp env.example .env
   ```
   Customize `.env` as needed.

5. **Apply Migrations & Run the Server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. **Run Tests**
   ```bash
   python manage.py test
   ```

7. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Running with Docker

#### Prerequisites

- Docker & Docker Compose

#### Steps

1. **Clone the Repository & Configure Environment**
   ```bash
   git clone https://github.com/dwisulfahnur/dj-modular
   cd dj-modular
   cp env.example .env
   ```

2. **Build and Start Containers**
   ```bash
   docker compose up -d
   ```

3. **Access the Application** at [http://localhost:8000](http://localhost:8000)

4. **Run Tests**
   ```bash
   docker compose run test
   ```

5. **Common Docker Commands**
   - Start services: `docker compose up -d`
   - Stop services: `docker compose down`
   - View logs: `docker compose logs -f web`
   - Run Django commands: `docker compose exec web python manage.py <command>`
   - Create a superuser: `docker compose exec web python manage.py createsuperuser`

## User Management

### Creating Users

#### Superuser (Admin)
```bash
./manage.py createsuperuser

# with docker
docker compose exec web python manage.py createsuperuser
```

#### Management Users
1. Create a user via Django Admin (`/admin/`).
2. Assign the user to the "Product Managers" group.

### Testing Different User Roles

- **Admin (Superuser):** `/admin/`
- **Management User:** `/login/` (Access: Module management, all installed modules)
- **Basic User:** `/login/` (Access: Installed modules based on permissions)

## Module Management

### Viewing Available Modules

- Login as a superuser or manager.
- Navigate to `/module/` to view module manager interface.

### Troubleshooting Module Registration

1. Ensure the module contains a `module.py` file.
2. Verify the module ID is in `settings.AVAILABLE_MODULES`.
3. Check logs for errors:
   ```bash
   docker compose logs -f web
   ```
