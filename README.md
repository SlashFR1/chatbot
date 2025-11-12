# 🎰 Jackbot 🎰

![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Status](https://img.shields.io/badge/status-in%20development-orange.svg)

An intelligent conversational assistant designed to provide accurate, context-aware information about French administrative law and government processes.

**Jackbot** is a versatile chatbot platform that helps users navigate French legal and administrative requirements with ease. The platform is highly customizable—simply modify the `systemPrompt` constant in `script.js` to adapt Jackbot to different domains, industries, or use cases. For optimal responses, provide detailed system prompts that include role descriptions, examples, and personality traits.



## Table of Contents

- [About The Project](#about-the-project)
- [Project Architecture](#project-architecture)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation with Docker](#installation-with-docker)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

### About The Project

This project provides a comprehensive chatbot solution for navigating French administrative law and government processes. The complete infrastructure is in place for production deployment.

The system integrates a **Retrieval-Augmented Generation (RAG)** pipeline with a vector database to ground responses in verified, document-based knowledge. It leverages the **Qwen Large Language Model (LLM)** and the **BGE-M3 embedding model** to deliver seamless, contextually accurate responses. The entire architecture is containerized using **Docker**, ensuring streamlined deployment and environment consistency across all platforms.


### Project Architecture

The project is structured as a multi-service Docker application, where each component has a distinct role:

```
jackbot/
├── docker-compose.yml      # Orchestrates all services
├── README.md               # This file
├── front/                  # Frontend service (static files)
│   ├── index.html
│   ├── script.js
│   └── style.css
├── rag/                    # RAG service (embeddings & retrieval)
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── db/                     # Database service (ChromaDB)
│   └── Dockerfile
└── nginx.conf              # Nginx configuration (reverse proxy)
```

**Service Descriptions:**

- **front**: Serves the user-facing web interface (HTML, CSS, JavaScript).
- **llm**: Hosts and serves the Qwen language model for text generation via Ollama.
- **rag**: Provides RAG capabilities—handles document vectorization using BGE-M3 and similarity search via ChromaDB API.
- **db**: Stores embeddings and conversation history in ChromaDB (vector database).
- **nginx**: Acts as the reverse proxy, routing requests to appropriate services.

### Key Features

- **Intuitive Web Interface**: A modern and responsive chat experience for seamless user interactions.
- **Advanced Conversational AI**: Powered by the Qwen language model for natural and contextually relevant responses.
- **Accurate & Contextual Answers**: Features a RAG system with the BGE-M3 embedding model to ground responses in custom knowledge base.
- **Easy & Isolated Deployment**: Fully containerized with Docker and Docker Compose for one-command setup.
- **Scalable & Extensible**: Modular architecture allows for easy addition of new knowledge and features.
- **Highly Customizable**: Adapt Jackbot to different domains by modifying the system prompt in `script.js`.

### Prerequisites

Before you begin, ensure you have the following tools installed on your system:

- **Git**
- **Docker**
- **Docker Compose** (typically included with Docker Desktop)

### Installation with Docker

Follow these steps to get the project running locally.

**Step 1: Clone the repository**

```bash
git clone https://github.com/SlashFR1/chatbot.git
cd chatbot
```

**Step 2: Launch the containers with Docker Compose**

This command will build the service images (if they don't exist) and start all containers in the background.

```bash
docker-compose up -d --build
```

- The `--build` flag forces a rebuild of the images if you have modified a Dockerfile.
- The `-d` flag runs the containers in detached mode.

**Step 3: Check the logs (Optional)**

To ensure all services have started correctly, you can view the logs:

```bash
docker-compose logs -f
```

**Step 4: Shut down the application**

To stop all project-related containers, use the following command:

```bash
docker-compose down
```

### Configuration

You can configure Jackbot by modifying the `systemPrompt` constant in `script.js`. For best results, provide a detailed system prompt that describes the chatbot's role, personality, and specific expertise.

You can also upgrade to a different version of Qwen if you want improved responses. Simply update the model name in your Docker environment or docker-compose configuration.

**Example Configuration Variables:**

```env
# Nginx Proxy Configuration
WEB_UI_PORT=8080

# Model Configuration
LLM_MODEL_NAME=Qwen/Qwen3:0.6b
EMBEDDING_MODEL_NAME=BAAI/bge-m3

# Database Configuration
DB_HOST=db
DB_PORT=8000
```

**Advanced Configuration:**

The system uses the following components, which can be customized:

- **ChromaDB Service**: Launches as a client-server instance. Data is persisted in a Docker volume for durability across restarts.
- **RAG Service**: Powered by FastAPI (Python). On startup, it loads the BGE-M3 model into memory and exposes endpoints for:
  - **Adding Documents**: Vectorizes text using BGE-M3 and stores embeddings in ChromaDB.
  - **Querying**: Vectorizes user queries and performs similarity search to retrieve the most relevant documents from ChromaDB.

### Usage

1. Once the application is running via `docker-compose up`, open your web browser.
2. Navigate to `http://localhost:8080`.
3. Begin interacting with Jackbot.

**Note**: As this project is currently a "shell," its knowledge is limited to the base Qwen model's pre-trained data. To enhance its capabilities, the RAG system must be populated with relevant documents (e.g., law codes, administrative guides, safety manuals, and reference materials).
### Contributing

Contributions are welcome! If you would like to improve this project, please follow these steps:

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Potential areas for contribution include:

- Adding documents to the RAG knowledge base.
- Improving data processing and ingestion scripts.
- Optimizing Docker configurations.
- Developing new features in the user interface.

### Acknowledgements

- To the creators of the Qwen and BGE-M3 models.
- To the Docker community.
- To the FastAPI and ChromaDB communities for their excellent tools.





