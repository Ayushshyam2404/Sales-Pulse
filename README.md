# Sales Pulse

**Sales Pulse** is a proprietary sales reporting dashboard developed for Orange Falcon. Designed specifically for the hospitality sector, this application provides a centralized interface for tracking property revenue, occupancy metrics, pipeline development, and contract segmentation (RFP vs. LNR).

The system utilizes a local database architecture to ensure data persistence and features a responsive, dark-themed user interface optimized for both screen viewing and high-resolution PDF export.

---

## System Overview

Sales Pulse serves as a business intelligence tool to visualize key performance indicators (KPIs) for hotel sales teams.

### Key Capabilities

*   **Performance Monitoring:** Real-time visualization of Total Revenue and Rooms Booked against operational metrics.
*   **Pipeline Analysis:** Comparative tracking of active proposals versus signed contracts to assess conversion efficiency.
*   **Activity Segmentation:** Quantifiable breakdown of sales efforts, distinguishing between Corporate and Construction accounts.
*   **Source Logic:** Detailed analysis of business sources, tracking the ratio between Request for Proposals (RFPs) and Locally Negotiated Rates (LNRs).
*   **Automated Analytics:** Algorithmic generation of executive summaries based on the most recent dataset.
*   **Print Optimization:** Built-in CSS media queries transform the interface into a ink-efficient, white-background layout for PDF reporting.

---

## Technical Specifications

The application is built on a lightweight, robust stack designed for ease of deployment and maintenance.

*   **Backend Framework:** Python (Flask)
*   **Database:** SQLite (Relational mapping via SQLAlchemy)
*   **Frontend:** HTML5, CSS3, JavaScript
*   **Data Visualization:** Chart.js
*   **Environment:** Cross-platform (Windows/macOS/Linux)

---

## Installation and Setup

Follow the instructions below to deploy the application in a local development environment.

### Prerequisites
*   Python 3.8 or higher
*   pip (Python Package Installer)

### 1. Clone the Repository
Clone the source code to your local machine:
```bash
git clone https://github.com/YOUR_USERNAME/falcon-sales-report.git
cd falcon-sales-report
2. Install Dependencies
Install the required Python packages using the provided requirements file:
code
Bash
pip install -r requirements.txt
3. Initialize the Application
Run the main application script. On the first launch, the system will automatically generate the SQLite database file (data.sqlite) and populate it with default structure.
code
Bash
python app.py
4. Access the Dashboard
The application will be served locally. Open a web browser and navigate to:
http://127.0.0.1:5000
Configuration
Branding Customization
The application supports custom branding assets located in the static/ directory.
Logo: Replace static/logo.png with your organization's logo. A transparent PNG is recommended for optimal integration with the dark theme.
Favicon: Replace static/favicon.ico with your organization's browser icon.
Database Management
The application uses data.sqlite for storage. This file is generated in the root directory. To reset the system to its initial state, delete this file and restart the application; a new database will be created automatically.
Usage Guide
Data Visualization: Upon loading, the dashboard retrieves and displays the most recent data entry from the database.
Updating Metrics: Click the "Update Data" button to open the input modal. All fields are required to ensure accurate chart generation.
Exporting Reports: Click the "Download PDF" button. The system utilizes the browser's native print engine to generate a formatted PDF. Ensure the destination is set to "Save as PDF" within the print dialog.
Copyright
© Orange Falcon. All rights reserved.