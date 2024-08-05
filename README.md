# Messaging System API

This is a RESTful Django-based API for creating and retrieving messages between users.

## Features

- User authentication (sign up and log in) with email and password
- Sending messages to other users
- Retrieving message threads between the logged-in user and other users
- Searching for a word or phrase within a message thread

## Setup

### Prerequisites

- Python 3.x
- pip
- virtualenv

### Installation

1. Clone the repository:
    ```sh
    git clone git@github.com:syriine17/messaging_system.git
    cd messaging_system
    ```

2. Create and activate a virtual environment:
    ```sh
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS and Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser (optional, for accessing the Django admin panel):
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Testing

### Creating Test Data

To facilitate testing, you can use the custom management command provided to generate sample users, message threads, and messages. 

1. **Run the command to create test data:**
    ```sh
    python manage.py create_test_data
    ```

   This command performs the following actions:
   - **Creates Users:** Three users (`user1`, `user2`, and `user3`) with sample credentials.
   - **Creates Message Threads:** Three message threads with two random participants each.
   - **Creates Messages:** Five messages per thread with random content and senders.

### API Endpoints

- **Authentication:**
  - `POST /api/login/` - Log in and receive a token.
  - `POST /api/register/` - Register a new user.

- **Messages:**
  - `GET /api/messages/` - Retrieve messages in threads for the logged-in user.
  - `POST /api/send/` - Send a new message.

- **Message Threads:**
  - `GET /api/threads/` - Retrieve message threads for the logged-in user.

- **URL**: `/api/search/`
- **Method**: `GET`
- **Description**: Search for messages containing the specified query and optionally filter by thread.
- **Query Parameters**:
  - `q`: (Required) The term or phrase to search for within message contents.
  - `thread_id`: (Optional) Filter messages that belong to this specific thread.
- **Example Request**:
  - To search for messages containing the word "hello":  
    `GET /api/search/?q=hello`
  - To search for messages containing the word "hello" in a specific thread with ID 1:  
    `GET /api/search/?q=hello&thread_id=1`
- **Response**: A list of messages matching the search criteria, including details such as content, and threads.

### Running Tests

To ensure everything is working correctly, run the test suite:

```sh
python manage.py test

```

## Swagger Documentation
You can access the API documentation via Swagger at:

`http://localhost:8000/api/swagger/`
