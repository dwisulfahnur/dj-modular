# Django Modular Engine

A reusable Django application that provides a dynamic module system. It allows you to develop, register, install, and manage modules within your Django project, supporting a plug-and-play architecture.

## Running with Docker

This project can be run using Docker and Docker Compose, which simplifies setup and ensures consistent environments.

### Prerequisites

- Docker
- Docker Compose

### Getting Started

1. Clone this repository:
```bash
git clone https://github.com/dwisulfahnur/dj-modular
cd dj-modular
```

2. Build and start the containers:
```bash
docker compose up -d
```

3. Access the application at http://localhost:8000

### Running Tests

To run the tests using Docker:

```bash
docker compose run test
```

This will run the tests for the modular_engine app and generate a coverage report.

### Development

- The project code is mounted as a volume, so changes you make to the code will be reflected in the running application.
- The database data is persisted in a Docker volume.

### Common Commands

- Start the services: `docker compose up -d`
- Stop the services: `docker compose down`
- View logs: `docker compose logs -f web`
- Run a management command: `docker compose exec web python manage.py <command>`
- Run tests: `docker compose run test`
- Create a superuser: `docker compose exec web python manage.py createsuperuser`

## Testing from Browser

The application provides different interfaces and permissions for different user types. Follow these steps to test the application from a browser:

### Creating Users

#### Creating a Superuser (Admin)

Superusers have full access to the Django admin interface and all application features:

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to create a superuser account. You'll need to provide:
- Username
- Email address (optional)
- Password

#### Creating Management Users

Management users have access to the module management interface but not the full admin panel:

1. First, create a regular user:
```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('manager', 'manager@example.com', 'password')"
```

2. Then, add the user to the management group:
```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import Group, User; manager = User.objects.get(username='manager'); manager_group, _ = Group.objects.get_or_create(name='Product Managers'); manager_group.user_set.add(manager)"
```

#### Creating Basic Users

1. Basic users have limited access, only to features provided by installed modules:

```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('user', 'user@example.com', 'password')"
```

2. Then, add the user to the user groups:
```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import Group, User; user_basic = User.objects.get(username='user'); product_user_group, _ = Group.objects.get_or_create(name='Product Users'); product_user_group.user_set.add(user_basic)"
```

### Registering and Managing Modules

The application now includes enhanced module registration capabilities:

#### Viewing Available Modules

1. Log in as a superuser or manager user
2. Go to http://localhost:8000/module/ to view the module manager interface

#### Manual Module Registration

If modules from `settings.AVAILABLE_MODULES` aren't showing up, you can manually register them:

```bash
docker compose exec web python manage.py register_modules
```

This command will attempt to register all modules listed in `settings.AVAILABLE_MODULES` and provide detailed output about the process.

#### Troubleshooting Module Registration

If you encounter issues with module registration, check the following:

1. Ensure the module package is correctly structured with a `module.py` file
2. Verify that the module ID is correctly listed in `settings.AVAILABLE_MODULES`
3. Check the logs for any errors during module loading:
```bash
docker compose logs -f web
```

### Testing Different User Roles

1. **Admin (Superuser)**:
   - Login URL: http://localhost:8000/admin/

2. **Management User**:
   - Login URL: http://localhost:8000/login/
   - Access: Module management, all installed modules

3. **Basic User**:
   - Login URL: http://localhost:8000/login/
   - Access: Only installed modules based on permissions
   - For the product module: Can create, update, and view products

## More Information

See [README.modular_engine.md](README.modular_engine.md) for detailed documentation about the Django Modular Engine.
