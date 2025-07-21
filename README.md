# Savor 

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

Savor aims to provide users with a comprehensive tool to track their pantry inventory, discover new recipes based on available ingredients, and minimize food waste. This initial version focuses on robust product identification and management as the foundation for future recipe generation capabilities.

---

## Features

* **Intelligent Product Search:** Quickly find food items by **barcode** or **product name** using the Open Food Facts API.
* **Local Data Caching:** Efficiently stores product details in a local database to speed up subsequent searches and reduce external API calls.
* **API Rate Limit Adherence:** Implements server-side rate limiting using `django-ratelimit` to ensure respectful and controlled consumption of external APIs, preventing blocks due to excessive requests.
* **Robust Error Handling:** Provides clear and informative error responses for various scenarios, including network issues, API errors, and rate limit excursions.
* **User Authentication (Under Development):** Secure user registration, login, and logout to enable personalized pantry management.

---

## Technologies Used

* **Backend:**
    * **Python 3**
    * **Django 5.2.4**: The web framework
    * **`django-ratelimit`**: For API rate limiting
    * **`django-redis`**: Redis cache backend for Django
    * **`requests`**: For making HTTP requests to external APIs
* **Database:**
    * **SQLite3**: Default Django database (for development)
    * **Redis**: In-memory data store for caching and rate limit counters
* **Frontend:**
    * **HTML5**
    * **CSS3**
    * **JavaScript (ES6+)**: For dynamic interactions and API calls (Fetch API)

---