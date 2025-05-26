# uHomes London Student Accomodation Price Tracker & Dashboard

This project provides an automated system to scrape accommodation prices from uhomes.com for London, track price changes (especially discounts), and visualize the data through an interactive Streamlit dashboard.

## Features

* **Automated Scraping:** Uses Playwright to scrape data from the JavaScript-powered uhomes.com website.
* **Scheduled Runs:** Leverages GitHub Actions to run the scraper automatically on a defined schedule (e.g., daily).
* **Price Tracking:** Compares newly scraped data with previously stored prices to identify new listings, removed listings, and price changes/discounts.
* **Logging:** Records detected price changes and new listings to a log file.
* **Data Persistence:** Stores the latest prices in a JSON file within the GitHub repository.
* **Interactive Dashboard:** Uses Streamlit to display the latest listings, filter them, and visualize price distributions.
* **Free Hosting:** Designed to run entirely on free tiers using GitHub Actions and Streamlit Cloud.

## Architecture Overview

The system is composed of several key components that work together to automate the process:

1.  **GitHub Repository:** Acts as the central hub, storing all the code (`price_tracker.py`, `dashboard.py`), dependencies (`requirements.txt`), and the scraped data (`uhomes_prices.json`, `discounts.log`).
2.  **GitHub Actions:** Serves as the automation engine. A scheduled workflow checks out the code, sets up the environment, runs the Playwright scraper, and pushes the updated data files back to the repository.
3.  **uHomes Website:** The target website from which accommodation data is scraped.
4.  **Streamlit Cloud:** Hosts the `dashboard.py` application, pulling the code and the latest `uhomes_prices.json` file from the GitHub repository to display an interactive web dashboard.
5.  **User:** Interacts with the Streamlit dashboard via a web browser.

## Architecture Diagram

Here is a visual representation of how these components interact:
![mermaid (1)](https://github.com/user-attachments/assets/a2945fcd-67ab-42f1-8b46-a4d599b9d933)


## How it Works - The Workflow

1.  **Schedule Trigger:** Based on the `cron` schedule defined in `.github/workflows/price_check.yml`, GitHub Actions initiates a new workflow run.
2.  **Setup:** GitHub Actions spins up a virtual runner (Ubuntu), checks out the code from your repository, installs Python, and installs all dependencies listed in `requirements.txt` (including Playwright and its browsers).
3.  **Scrape & Compare:** The `price_tracker.py` script is executed:
    * It loads the `uhomes_prices.json` file (if it exists) from the checked-out code.
    * It launches Playwright (headlessly).
    * It navigates to the specified Uhomes URL.
    * It handles cookie banners and pop-ups.
    * It scrapes the current listings' names, addresses, prices, and links.
    * It compares the newly scraped prices with the old prices.
    * It logs any new listings, removed listings, or price changes (especially discoun

## How it Works - The Workflow

1.  **Schedule Trigger:** Based on the `cron` schedule defined in `.github/workflows/price_check.yml`, GitHub Actions initiates a new workflow run.
2.  **Setup:** GitHub Actions spins up a virtual runner (Ubuntu), checks out the code from your repository, installs Python, and installs all dependencies listed in `requirements.txt` (including Playwright and its browsers).
3.  **Scrape & Compare:** The `price_tracker.py` script is executed:
    * It loads the `uhomes_prices.json` file (if it exists) from the checked-out code.
    * It launches Playwright (headlessly).
    * It navigates to the specified Uhomes URL.
    * It handles cookie banners and pop-ups.
    * It scrapes the current listings' names, addresses, prices, and links.
    * It compares the newly scraped prices with the old prices.
    * It logs any new listings, removed listings, or price changes (especially discounts) to `discounts.log` and the console.
4.  **Push Data:** If any data files (`uhomes_prices.json`, `discounts.log`) have been created or modified, the GitHub Actions workflow commits these changes and pushes them back to your GitHub repository.
5.  **Deploy/Update Dashboard:** Streamlit Cloud is linked to your GitHub repository. When changes are pushed (or when the app starts/refreshes), it pulls the latest version.
6.  **View Dashboard:** The user opens the Streamlit Cloud URL. The `dashboard.py` script runs, loads the latest `uhomes_prices.json`, and displays the interactive dashboard with tables, metrics, and charts.

## Setup & Usage

### Prerequisites

* A GitHub Account
* A Streamlit Cloud Account
* Git installed locally (optional, can use GitHub website)
* Python 3.8+ installed locally (for testing/development)

### Steps

1.  **Fork/Clone Repository:** Get a copy of this repository on your GitHub account and clone it locally.
2.  **Install Locally (Optional):**
    * Create a virtual environment: `python -m venv venv`
    * Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
    * Install dependencies: `pip install -r requirements.txt`
    * Install Playwright browsers: `playwright install --with-deps`
    * Run `price_tracker.py` once to test and generate initial data.
    * Run `streamlit run dashboard.py` to test the dashboard locally.
3.  **Set up GitHub Actions:**
    * Ensure the `.github/workflows/price_check.yml` file exists and is configured with your desired schedule.
    * Ensure the workflow has `permissions: contents: write` to push data back.
    * Push the repository to GitHub.
4.  **Set up Streamlit Cloud:**
    * Connect your GitHub account to Streamlit Cloud.
    * Deploy a new app, pointing it to your repository and `dashboard.py`.
    * Ensure the app is deployed as 'Public' if using the free tier (and your repo is public).

## Files in this Repository

* **`price_tracker.py`**: The main Python script responsible for scraping Uhomes, comparing prices, and saving results.
* **`dashboard.py`**: The Python script for the Streamlit web application.
* **`requirements.txt`**: Lists all Python dependencies needed for the project.
* **`.github/workflows/price_check.yml`**: The GitHub Actions workflow file that defines the scheduled task.
* **`uhomes_prices.json`**: (Generated) Stores the latest scraped price data.
* **`discounts.log`**: (Generated) Logs detected price changes.
* **`README.md`**: This file!
