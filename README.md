# OCR Receipt Processor

<img width="1434" height="808" alt="Image" src="https://github.com/user-attachments/assets/c7eb7a7b-0ec3-4ce0-844c-1fe3b0a28c5c" />

A comprehensive OCR (Optical Character Recognition) system for processing receipts and bills with advanced search, sorting, and analytics capabilities.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: Upload images (JPG, PNG), PDFs, and text files
- **Advanced OCR**: Extract structured data using Tesseract OCR
- **Smart Classification**: Automatically categorize receipts based on content
- **Data Extraction**: Extract vendor, amount, date, and line items

### Advanced Search & Analytics
- **6 Search Algorithms**: Linear, Binary, Hash, Fuzzy, Range, and Pattern search
- **4 Sorting Algorithms**: QuickSort, MergeSort, TimSort, and HeapSort
- **Statistical Aggregations**: Sum, Mean, Median, Mode, Variance, Standard Deviation
- **Time Series Analysis**: Daily, weekly, and monthly aggregations
- **Histogram Generation**: Data distribution analysis

### User Interface
- **FastAPI Backend**: RESTful API with automatic documentation
- **Streamlit Dashboard**: Interactive web interface with real-time analytics
- **Export Capabilities**: CSV and JSON export functionality
- **Real-time Statistics**: Live updates of receipt analytics

## 📁 Project Structure

```
ocr-receipt-processor/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── search.py
│   │   │   ├── analytics.py
│   │   │   └── export.py
│   │   └── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   ├── extraction_service.py
│   │   └── analytics_service.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── search_algorithms.py
│   │   ├── sort_algorithms.py
│   │   └── aggregation_algorithms.py
│   └── dashboard/
│       ├── __init__.py
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── upload_page.py
│       │   ├── view_page.py
│       │   ├── search_page.py
│       │   ├── analytics_page.py
│       │   └── export_page.py
│       └── main.py
├── data/
│   └── receipts.db
├── scripts/
│   ├── start_system.py
│   └── setup_database.py
├── requirements.txt
├── .gitignore
├── README.md
```

## 🛠️ Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR**: Required for text extraction
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ocr-receipt-processor.git
   cd ocr-receipt-processor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python scripts/setup_database.py
   ```

4. **Start the system**
   ```bash
   python scripts/start_system.py
   ```

5. **Access the application Locally**
   - **API Documentation**: http://localhost:8001/docs
   - **Dashboard**: http://localhost:8501

## 🏗️ Architecture

### System Design

The application follows a **modular microservices architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   SQLite        │
│   Dashboard     │◄──►│   Backend       │◄──►│   Database      │
│   (Frontend)    │    │   (API Layer)   │    │   (Data Layer)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User          │    │   Business      │    │   Data          │
│   Interface     │    │   Logic         │    │   Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

#### 1. **API Layer** (`app/api/`)
- **FastAPI Framework**: High-performance async API
- **RESTful Endpoints**: Upload, search, sort, analytics, export
- **Automatic Documentation**: Interactive API docs with Swagger UI
- **CORS Support**: Cross-origin resource sharing enabled

#### 2. **Core Services** (`app/services/`)
- **OCR Service**: Text extraction from images/PDFs
- **Extraction Service**: Structured data parsing
- **Analytics Service**: Statistical computations

#### 3. **Algorithm Engine** (`app/algorithms/`)
- **Search Algorithms**: 6 different search implementations
- **Sort Algorithms**: 4 different sorting implementations
- **Aggregation Functions**: Statistical analysis tools

#### 4. **Dashboard** (`app/dashboard/`)
- **Streamlit Interface**: Interactive web dashboard
- **Real-time Updates**: Live data visualization
- **Multi-page Navigation**: Organized feature access

## 🔍 Algorithm Details

### Search Algorithms

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| **Linear Search** | O(n) | Simple sequential search |
| **Binary Search** | O(log n) | Sorted data lookup |
| **Hash Search** | O(1) average | Fast exact matching |
| **Fuzzy Search** | O(n*m) | Approximate matching |
| **Range Search** | O(n) | Numeric range queries |
| **Pattern Search** | O(n) | Regex pattern matching |

### Sorting Algorithms

| Algorithm | Time Complexity | Space Complexity | Stability |
|-----------|----------------|------------------|-----------|
| **QuickSort** | O(n log n) avg | O(log n) | No |
| **MergeSort** | O(n log n) | O(n) | Yes |
| **TimSort** | O(n log n) | O(n) | Yes |
| **HeapSort** | O(n log n) | O(1) | No |

### Aggregation Functions

- **Statistical**: Sum, Mean, Median, Mode, Variance, Standard Deviation
- **Distribution**: Histogram generation with customizable bins
- **Time Series**: Daily, weekly, monthly aggregations
- **Advanced**: Custom window functions and rolling statistics

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload and process receipt |
| `GET` | `/receipts` | Get all receipts |
| `PATCH` | `/receipts/{id}` | Update receipt |
| `POST` | `/search` | Advanced search |
| `POST` | `/sort` | Advanced sorting |
| `POST` | `/aggregate` | Statistical aggregation |
| `GET` | `/statistics` | System statistics |
| `GET` | `/algorithms` | Available algorithms |

### Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/export/csv` | Export data as CSV |
| `GET` | `/export/json` | Export data as JSON |

## 🎯 User Journeys

### 1. **Receipt Upload Journey**
```
User uploads receipt → OCR processing → Data extraction → 
Classification → Database storage → Success confirmation
```

### 2. **Search & Analysis Journey**
```
User selects search criteria → Algorithm execution → 
Results filtering → Data visualization → Export options
```

### 3. **Analytics Journey**
```
User selects aggregation → Statistical computation → 
Chart generation → Trend analysis → Report export
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./data/receipts.db

# API Settings
API_HOST=localhost
API_PORT=8001

# Dashboard Settings
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8501

# OCR Settings
TESSERACT_PATH=/usr/local/bin/tesseract
```

### Performance Tuning

- **Database Indexing**: Automatic index creation for search optimization
- **Memory Management**: Efficient data structures for large datasets
- **Caching**: In-memory caching for frequently accessed data
- **Async Processing**: Non-blocking operations for better responsiveness

### Production Considerations

- **Database**: Consider PostgreSQL for production use
- **File Storage**: Implement cloud storage (AWS S3, Google Cloud)
- **Security**: Add authentication and authorization
- **Monitoring**: Implement logging and health checks
- **Scaling**: Use load balancers and multiple instances

## 📈 Performance Metrics

### Benchmarks

| Operation | Average Time | Memory Usage |
|-----------|--------------|--------------|
| Receipt Upload | 2-5 seconds | 50-100 MB |
| Search (1000 records) | 10-50ms | 10-20 MB |
| Sort (1000 records) | 5-20ms | 5-10 MB |
| Analytics | 100-500ms | 20-50 MB |

### Optimization Strategies

- **Indexed Queries**: Database indexes for faster searches
- **Algorithm Selection**: Automatic algorithm choice based on data size
- **Memory Pooling**: Reusable memory allocation
- **Lazy Loading**: On-demand data loading

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests for new functionality**
5. **Run the test suite**
6. **Submit a pull request**

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Documentation**: Use docstrings for all functions
- **Type Hints**: Include type annotations
- **Error Handling**: Comprehensive exception handling

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tesseract OCR**: Open-source OCR engine
- **FastAPI**: Modern web framework for APIs
- **Streamlit**: Rapid web app development
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization

**Made with ❤️ for efficient receipt processing** 
