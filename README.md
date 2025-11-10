🚦 Road Safety Chatbot

![alt text](https://img.shields.io/badge/license-MIT-green.svg)

![alt text](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

![alt text](https://img.shields.io/badge/status-in%20development-orange.svg)

An intelligent conversational assistant designed to raise awareness and educate on road safety.

This project is a chatbot platform engineered to provide accurate, context-aware information about traffic laws, road hazards, and best safety practices.

![alt text](https://raw.githubusercontent.com/open-webui/open-webui/main/docs/assets/images/screenshot-chat-light.png)



## Table of Contents

    About The Project

    Project Architecture

    Key Features

    Prerequisites

    Installation with Docker

    Configuration

    Usage

    Contributing

    License

    Acknowledgements

### About The Project

This project aims to enhance awareness and education regarding road safety and its associated risks. While it is currently a functional shell in terms of content, the complete infrastructure is in place for future development.

The system integrates a Retrieval-Augmented Generation (RAG) pipeline and a database to support its responses with factual, document-based knowledge. It leverages the Qwen Large Language Model (LLM) and the Open WebUI interface to deliver a seamless and intuitive user experience. The entire architecture is fully containerized using Docker, ensuring streamlined deployment and environment consistency.


### Project Architecture

The project is structured as a multi-service Docker application, where each component has a distinct role:
code Code

    
road-safety-llm/
│
├── docker-compose.yml     # Orchestrates all services
├── README.md              # This file
│
├── ui/                    # Frontend service (Open WebUI)
│   ├── Dockerfile
│   └── ...
│
├── llm/                   # Service for the LLM (Qwen via VLLM)
│   ├── Dockerfile
│   └── ...
│
├── rag/                   # Service for RAG and embeddings
│   ├── Dockerfile
│   └── ...
│
├── db/                    # Database service (e.g., PostgreSQL/ChromaDB)
│   ├── Dockerfile
│   └── ...
│
└── proxy/                 # Reverse Proxy service (Nginx)
    └── nginx.conf

  

    ui: Manages the user-facing interface.

    llm: Hosts and serves the Qwen language model for text generation.

    rag: Handles the creation of embeddings (BGE-M3) from source documents and retrieves relevant information for the LLM.

    db: Stores application data, conversation history, and potentially the embedding vectors.

    proxy: Acts as a single entry point for all services, managing requests and routing.

### Key Features

    Intuitive Web Interface: Powered by Open Web UI (React-based) for a modern and responsive chat experience.

    Advanced Conversational AI: Driven by the Qwen language model for natural and relevant responses.

    Accurate & Contextual Answers: Features a RAG system with the BGE-M3 embedding model to ground responses in a custom knowledge base.

    Easy & Isolated Deployment: Fully containerized with Docker and Docker Compose for a one-command setup.

    Scalable & Extensible: The modular architecture allows for the easy addition of new knowledge and features.

### Prerequisites

Before you begin, ensure you have the following tools installed on your system:

    Git

    Docker

    Docker Compose (typically included with Docker Desktop)

### Installation with Docker

Follow these steps to get the project running locally.

Clone the repository:
    
    
git clone https://github.com/YOUR_USERNAME/road-safety-llm.git
cd road-safety-llm

  

Set up environment variables:
The project uses an .env file for configuration management. Copy the example file to create your own.
    
cp .env.example .env


Open the .env file and customize the variables as needed (e.g., ports, model names).

Launch the containers with Docker Compose:
This command will build the service images (if they don't exist) and start all containers in the background.


    
docker-compose up -d --build

  
    The --build flag forces a rebuild of the images if you have modified a Dockerfile.

    The -d flag runs the containers in detached mode.

Check the logs (Optional):
To ensure all services have started correctly, you can view the logs.


    
docker-compose logs -f

  

Shut down the application:
To stop all project-related containers, use the following command:


        
    docker-compose down

      

### Configuration

The primary project configuration is handled through the .env file at the root of the project. Key variables you may want to adjust include:
code Dotenv

    
# .env.example

# Nginx Proxy Configuration
WEB_UI_PORT=3000

# Model Configuration
LLM_MODEL_NAME=Qwen/Qwen1.5-7B-Chat
EMBEDDING_MODEL_NAME=BAAI/bge-m3

# Database Configuration
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=roadsafety_db

  

### Usage

    Once the application is running via docker-compose up, open your web browser.

    Navigate to: http://localhost:3000 (or the port you specified in your .env file).

    On your first visit, Open WebUI will prompt you to create an administrator account.

    After logging in, you can begin interacting with the chatbot.

Note: As this project is currently a "shell," its knowledge is limited to the base Qwen model's pre-trained data. To enhance its capabilities, the RAG system must be populated with relevant documents (e.g., traffic codes, safety manuals, prevention articles).


### Contributing

Contributions are welcome! If you would like to improve this project, please follow these steps:

    Fork the project.

    Create your feature branch (git checkout -b feature/AmazingFeature).

    Commit your changes (git commit -m 'Add some AmazingFeature').

    Push to the branch (git push origin feature/AmazingFeature).

    Open a Pull Request.

Potential areas for contribution include:

    Adding documents to the RAG knowledge base.

    Improving data processing and ingestion scripts.

    Optimizing Docker configurations.

    Developing new features in the user interface.

### License

This project is distributed under the MIT License. See the LICENSE file for more information.

### Acknowledgements

    To the Open WebUI community for their user interface.
    https://github.com/open-webui/open-webui.git

    To the creators of the Qwen and BGE-M3 models.

    To the Docker community.