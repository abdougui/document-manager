# Document Upload and Categorization App

This application allows users to upload and read documents with specific allowed extensions. It uses OpenAI to detect the category of the document.

## Getting Started

### Backend Setup

1. Navigate to the backend folder:
    ```sh
    cd backend
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Rename `example.env` to `.env` and add your credentials.

4. run test and see results at least 18 should pass
    ```sh
    pytest
    ```

5. Run the application locally:
    ```sh
    flask run --reload
    ```

6. Alternatively, deploy it on AWS by following these steps:
    - Modify `template_example.yml` to `template.yml`.
    - Update the credentials.
    - Run the following commands:
        ```sh
        sam build
        sam deploy --guided
        ```
    - To test locally using Docker:
    - Make sure docker is running
    - Modify `env_example.json` to `env.json`.
    - Update the credentials.
        ```sh
        sam build
        sam local start-api --env-vars env.json
        ```
### Backend Endpoints

- `GET /documents` - Retrieves a list of all documents.
- `POST /upload` - Uploads a document (takes a file as a parameter).
- `POST /detect` - Detects the purpose of the text in the document.
- `DELETE /delete/<document_id>` - Detects the purpose of the text in the document.

## Allowed Extensions

Ensure that the documents you upload have the allowed extensions as specified in the application settings.

### Frontend Setup

1. Navigate to the frontend folder:
    ```sh
    cd frontend
    ```

2. Install the required dependencies:
    ```sh
    npm install
    ```

3. Modify the `.env` file:
    ```sh
    VITE_BASE_URL=YOUR ENDPOINT
    ```

4. Run the application locally:
    ```sh
    npm run dev
    ```

5. To build the application:
    ```sh
    npm run build
    ```

6. You will find the build results in the `dist` folder.