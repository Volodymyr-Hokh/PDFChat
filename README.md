# PDF Chat Application

PDF Chat is an innovative Python application that allows users to interact with their PDF documents through a chat interface. The application utilizes advanced language models to analyze and respond to queries about the uploaded documents.

## Live Demo

You can try out the application at [pdfchat.xyz](https://pdfchat.xyz)

## Key Features

1. **User Authentication**
   - Secure login and registration system
   - Token-based authentication for API requests

2. **Document Management**
   - Upload PDF documents
   - View a list of uploaded documents
   - Delete documents when no longer needed

3. **Chat Interface**
   - Create multiple chat sessions for each document
   - Interact with the document content through natural language queries
   - Receive AI-generated responses based on the document content

4. **Document Analysis**
   - AI-powered analysis of PDF content
   - Extract relevant information based on user queries




## Getting Started

To run this API locally:

1. Clone the repository
2. Install the required dependencies from requirements.txt file
3. Set up your database and update the connection string in the configuration
4. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
5. Visit `http://localhost:8000/docs` to see the Swagger UI and test the API endpoints

---

Experience the future of document interaction at [pdfchat.xyz](https://pdfchat.xyz)!