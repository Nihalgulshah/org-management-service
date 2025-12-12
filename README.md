Prerequisites
Python 3.8+

MongoDB running locally on port 27017

Steps
Clone the repository

Bash

git clone [https://github.com/your-repo/org-management-service.git](https://github.com/your-repo/org-management-service.git)
cd org-management-service
Install Dependencies

Bash

pip install fastapi uvicorn motor pydantic passlib[bcrypt] python-jose python-multipart
Run the Server

Bash

uvicorn main:app --reload
Access Documentation

Open your browser to http://127.0.0.1:8000/docs to view the interactive Swagger UI.