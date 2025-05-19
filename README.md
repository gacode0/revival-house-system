# Revival House Global Church Management System

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

A secure backend API for managing church operations, departments, and member authentication.

## Features

- JWT Authentication
- User Management (Registration/Profile Updates)
- Department Management
- Password Reset via Email
- MongoDB Database Integration

## Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **Database**: MongoDB (Atlas or Local)
- **Authentication**: JWT, OAuth2
- **Email**: SMTP (Gmail/Mailtrap)
- **Tools**: Pydantic, Motor (async MongoDB), FastAPI-Mail

## API Endpoints

### Authentication
| Method | Endpoint                | Description                     |
|--------|-------------------------|---------------------------------|
| POST   | `/auth/register`        | Register new user               |
| POST   | `/auth/login`           | Login and get access token      |
| PATCH  | `/auth/users/{user_id}` | Update user profile             |

### Password Reset
| Method | Endpoint                      | Description                     |
|--------|-------------------------------|---------------------------------|
| POST   | `/auth/password-reset/request`| Request password reset token    |
| POST   | `/auth/password-reset/confirm`| Confirm password reset          |

### Departments
| Method | Endpoint                      | Description                     |
|--------|-------------------------------|---------------------------------|
| POST   | `/departments/`               | Create new department           |
| GET    | `/departments/`               | List all departments            |
| POST   | `/departments/{id}/members/{user_id}` | Add member to department |

## Setup Instructions

### Prerequisites
- Python 3.10+
- MongoDB (Local or Atlas URI)
- Gmail account (for email functionality)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/revival-house-system.git
   cd revival-house-system