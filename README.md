# Org Management Service

A backend service built using FastAPI for managing organizations, users, and authentication. This project demonstrates API design, service-layer architecture, MongoDB integration using Motor, and Pydantic based request and response models.

## Features

- FastAPI-based RESTful backend
- MongoDB integration using Motor (asynchronous driver)
- User registration and authentication workflow
- Modular service architecture
- Pydantic models for validation
- Clean separation of concerns between models, service, and API layers
- Easily extendable structure for additional endpoints

## Technology Stack

- Python 3.8+
- FastAPI
- MongoDB
- Motor
- Pydantic
- Uvicorn

## Project Structure

assignment/
  main.py
  models.py
  service.py
  README.md

## Prerequisites

- Python 3.8 or higher
- MongoDB running locally on port 27017 or a remote MongoDB URI
- pip package manager


## Environment Variables (Optional)

Create a .env file if required:

MONGO_URI=mongodb://localhost:27017
DB_NAME=org_management

## Code Overview

main.py:
Initializes FastAPI application and routes.

models.py:
Defines Pydantic models for validation and API schemas.

service.py:
Contains business logic and MongoDB operations using Motor.

## Future Enhancements

- JWT-based authentication
- Organization role management
- Pagination and filtering
- Docker support
- Deployment on Render, Railway, or AWS

## License

This project is available under the MIT License.
