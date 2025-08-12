# Savor 🍽️

Savor is a modern web application designed to revolutionize your kitchen experience by offering intelligent pantry management and personalized recipe suggestions. Say goodbye to food waste and the "what's for dinner?" dilemma!

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Technologies Used](#technologies-used)
* [Setup and Installation](#setup-and-installation)
* [Usage](#usage)

---

## Overview

Savor aims to provide users with a comprehensive tool to track their pantry inventory, discover new recipes based on available ingredients, and minimize food waste. This version of the application features a complete system for pantry management and integrates with AI (Gemini 2.5-flash) to provide real-time, personalized recipe generation.

---

## Features

* **Extensive Product Search Capabilities:** Quickly find food items by **barcode** or **product name** using the Open Food Facts API. 
* **Intelligent Recipe Generation:** Leveraging the Google Gemini AI, Savor generates unique, healthy, and easy-to-follow recipes based on the exact ingredients in your pantry.
* **Asynchronous Task Management:** Recipe generation is handled in the background by **Celery workers**. This ensures the application remains fast and responsive, preventing long loading times while the AI processes requests.
* **Dynamic Pantry Synchronization:** A smart system of middleware and signals ensures your recipe suggestions are always up-to-date. Recipes are automatically regenerated when a user:
    * Logs in or starts a new session.
    * Adds or removes an item from their pantry.
* **Local Data Caching:** Efficiently stores product details in a local database and a Redis cache to speed up subsequent searches and reduce external API calls.
* **API Rate Limit Adherence:** Implements server-side rate limiting to ensure the controlled consumption of external APIs.
* **Robust Error Handling:** Provides clear and informative error responses for various scenarios, including network issues, API errors, and rate limit excursions.
* **Secure User Authentication:** Features secure user registration, login, and logout to enable personalized pantry management.

---

## Technologies Used

* **Backend:**
    * **Python 3**
    * **Django 5.2.4**: The web framework
    * **Celery**: For asynchronous task processing
    * **Google Generative AI SDK**: To communicate with the Gemini AI
    * **`django-ratelimit`**: For API rate limiting
    * **`django-redis`**: Redis cache backend for Django
    * **`requests`**: For making HTTP requests to external APIs
* **Database:**
    * **SQLite3**: Default Django database (for development)
    * **Redis**: In-memory data store for caching, rate limit counters, and Celery broker
* **Frontend:**
    * **HTML5**
    * **CSS3**
    * **JavaScript (ES6+)**: For dynamic interactions, API calls (Fetch API), and webcam barcode scanning.

---