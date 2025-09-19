

Technology Stack & Architecture

This project is built with a modern, decoupled architecture to ensure scalability and performance.

-   **Backend:** A high-performance REST API built with **FastAPI**, providing a robust foundation for data processing and AI integration.
-   **Frontend:** An interactive, multi-page web application created with **Streamlit**, designed for rapid data visualization and user interaction.
-   **Database:** **SQLite** is used for lightweight, persistent storage of threat intelligence data.
-   **Core AI Engine:** Powered by **Google's Gemini 1.5 Flash**, which provides the state-of-the-art natural language processing for threat analysis, summarization, and quiz generation.
-   **Data Ingestion:** A Python script using the `requests` and `feedparser` libraries to pull in real-time data from public sources.

!
*Architecture Diagram: Data is ingested, processed by the FastAPI/AI backend, and displayed on the Streamlit frontend.*
