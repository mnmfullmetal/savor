# Savor

Savor is a web application designed to revolutionise your kitchen experience by offering intelligent pantry management, detailed product insights, and personalised recipe suggestions. It connects to the Open Food Facts API for comprehensive product data and uses AI for dynamic recipe generation, all wrapped in a secure, multi-lingual user experience.

Video Demo: 

## Table of Contents

* [Distinctiveness and Complexity](#distinctiveness-and-complexity)
* [Technologies Used](#technologies-used)
* [What's contained in each file you created](#whats-contained-in-each-file-you-created)
* [Usage](#usage)
* [ Additional Information](#additional-information)

---

## Distinctiveness and Complexity

Savor satisfies the distinctiveness and complexity requirements by significantly exceeding the scope of any of the previous assignments, with its own unique design and challenges that came with it. Attempting to emulate Icarus, I nearly destroyed myself through my hubris. To my dismay, what was meant to be a cute, 6 week solo project morphed into a 12 week nightmare that had me questioning my sanity and will to live at times. I wish I could say that I have learned my lesson, time will tell. 

* **Distinctiveness:** Unlike "Commerce" (an e-commerce site) or "Network" (a social media site), Savor is a **data-driven utility application**. Its purpose is not to facilitate transactions between users or to host content like posts. Instead, it acts as a sophisticated personal tool that integrates multiple third-party services (Open Food Facts, Google Gemini) to provide a unique service: intelligent pantry management. While other CS50W projects focus on self-contained systems, Savor is an application focused on external data retrieval, processing, and presentation through intergrated systems..

* **Complexity:** The project's complexity is not in simple CRUD operations (like posting or bidding) but in its underlying architecture. It orchestrates asynchronous tasks, manages a multi-layered cache (Redis), handles real-time external API data, and supports full **internationalisation** for 33 languages. This architecture is necessary to handle tasks like AI recipe generation, which would time out a standard web request. This requires a stack (Django, Celery, Redis) far more complex than the standard Django/SQLite applications built in the course.

The key features and design choices that demonstrate this (perhaps masochistic) complexity are as follows:

### Key Features
* **Pantry & Product Management:** Users can add products (found via search or scan) to their personal pantry and receive aggregated **Nutri-Score** and **Eco-Score** calculations.
* **Advanced Search & Scanning:** Implements basic text search (OFF API v1), barcode search (v2), advanced text search (v1 with parameters) and autocomplete search suggestions for when the user is typing in the search form (v3 taxonomies). It also integrates `html5-qrcode` for live camera-based scanning.
* **Intelligent & Personalised Experience:** Generates AI recipes based on pantry contents and allows users to set detailed preferences for allergies, dietary needs, language, and UI behaviour via their settings.
* **Full Internationalisation (i18n):** The application is translated into 33 languages, handling both static text (DeepL-generated `.po` files) and dynamic text (requesting **localised** data from the API to then be cached and used until periodically updated via a scheduled **Celery Beat** task).
* **Asynchronous & Scheduled Tasks:** Uses **Celery** and **Celery Beat** to run long processes (like AI generation and API data fetching) in the background, ensuring the UI remains fast.
* **Performance & Caching:** Leverages **Redis** to cache API responses, AI recipes, and **localised** form data for near-instant access.
* **Secure & Robust Backend:** Features full user authentication, account management, and API rate limiting (`django-ratelimit`).
 
### Design Choices & Hurdles

* **Celery & Celery Beat:** Chosen to handle long-running and asynchronous tasks without blocking the user interface. Heavy operations like AI recipe generation or external API calls are dispatched as background jobs, often triggered by Django signals (e.g., when a user adds a pantry item). Celery Beat (with `celery-redbeat`) was used to run scheduled, periodic tasks, such as refreshing cached API data.

* **Redis:** Selected for its versatility, as it solved three core problems with a single service. It acts as both the **message broker** and **result backend** for Celery. Additionally, it serves as the primary Django **application cache**, storing frequently accessed data like **localised** JSON for form choices (e.g., countries, categories) to dramatically speed up page loads for user settings and advanced search.

* **Handling Fragmented API Documentation:** A major hurdle was the Open Food Facts (OFF) API, which is undergoing a significant overhaul. This resulted in documentation that was often fragmented, incomplete, or outdated. Discovering the correct API endpoints and data structures required significant research, with their official Slack community channels often providing the most reliable information.
It felt less like software engineering and more like digital archaeology, dusting off old Slack messages to find the Rosetta Stone for a v1 endpoint.
* **Complex Localisation Strategy:** Implementing support for 33 languages was a two-part challenge, which I, in my infinite wisdom, initially estimated as a "quick weekend task". Static UI text was managed using Django's `.po`/`.mo` files, which were auto-translated via a custom shell command using the DeepL API. Dynamic content (like product names) required carefully managing API requests to Open Food Facts to fetch data in the user's selected language.

* **Performance & Rate Limit Balancing:** A central design challenge was ensuring the app felt fast and responsive with minimal user downtime, while simultaneously respecting the rate limits of external APIs. This required designing a careful data flow of retrieving, caching (in Redis), and serving data to the user efficiently.



## Technologies Used

### Backend:
* **Python 3**
* **Django 5.2.4**: The web framework.
* **Celery 5.5.3**: For asynchronous task processing.
* **Google Generative AI SDK (`google-genai`):** For communicating with the Gemini AI.

### Database & Caching:
* **SQLite3**: Default database for development.
* **Redis 7.0.0b1**: In-memory data store used for:
    * Celery broker & result backend
    * Celery Beat scheduler (`celery-redbeat`)
    * Django caching backend (`django-redis`)
    * Rate limiting counters

### Frontend:
* **HTML5**
* **CSS3**
* **JavaScript (ES6+)**
* **`html5-qrcode`**: For client-side barcode and QR code scanning.

### APIs & Services:
* **Open Food Facts API (v1, v2, v3):** For all product data, search, and taxonomies.
* **Google Gemini AI:** For recipe generation.
* **DeepL API:** Used during development (via a custom command) to generate `.po` translation files.

### Python Tools:
* **`django-environ`**: For managing environment variables.
* **`django-ratelmit`**: For server-side request rate limiting.
* **`django-widget-tweaks`**: For easier template form rendering.
* **`celery-redbeat`**: Database-backed periodic task scheduler for Celery.



## Core Components

The project is organised into a primary project folder (`savor`) and three main Django apps (`users`, `pantry`, `recipes`).

### Project Root (`savor`)

This directory contains the core configuration and project-wide components that orchestrate the entire application.

* **`settings.py`:** Manages all project-level settings. This includes database configuration, `django-environ` for API keys (like `GOOGLE_API_KEY`), cache settings (pointing to Redis), Celery/Celery Beat configuration, internationalisation/localisation paths, and rate-limiting rules.
* **`celery.py`:** Standard Celery configuration file. It defines the Celery app instance and auto-discovers tasks from all registered Django apps, enabling the asynchronous architecture.
* **`urls.py`:** The main URL routing file. It includes paths for the admin interface and delegates app-specific URLs to the `urls.py` files within the `users`, `pantry`, and `recipes` apps.
* **`tasks.py`:** Contains project-wide Celery tasks. The most important is `update_facet_data`, a periodic task managed by Celery Beat, which refreshes and caches search filter data (like categories, brands, and allergens) from the Open Food Facts API for all supported languages. This ensures that forms in the `pantry` and `users` apps are populated with up-to-date, localised data without hitting the API on every request.
* **`middleware.py`:** Contains custom middleware classes that run on each request:
    *   `PantryRecipeMiddleware`: A smart middleware that checks a session flag to see if new AI recipes should be generated for the user, preventing redundant API calls to the Gemini AI. It interacts with `pantry.signals` to schedule recipe generation.
    *   `UserLanguageMiddleware`: Sets the translation language for the session based on the authenticated user's profile settings, ensuring a personalised, multilingual experience.
* **`utils.py`:** Contains project-wide helper functions and constants, such as the `rate_limit_error_response` function and mappings for language and country codes used across the `pantry` and `users` apps.
 
### `users` app

This app handles everything related to user accounts, authentication, and preferences.

* **`models.py`:** Defines two key models:
    *   **`User`**: A custom model inheriting from Django's `AbstractUser`, extended with a `favourited_products` relationship to the `pantry.Product` model.
    *   **`UserSettings`**: A `OneToOneField` linked to `User` that stores all user-specific preferences, including `language_preference`, `country`, dietary needs (`allergens`, `dietary_requirements`), and UI settings.
* **`views.py`:** Handles all user authentication and management logic, including registration, and account deletion. The `account_settings` view is particularly complex, as it dynamically populates the `UserSettingsForm` with choices fetched from the Redis cache, providing localised options for allergens, diets, and languages.
* **`forms.py`:** Defines the forms for user management. The `UserSettingsForm` is notable for its dynamic initialisation, where choice fields are populated from data passed in by the `account_settings` view.
* **`signals.py`:** Contains a `post_save` signal for the `User` model, which automatically creates a `UserSettings` instance for a new user upon registration.
* **`admin.py`:** Customises the Django admin interface, allowing administrators to manage `User`, `Allergen`, and `DietaryRequirement` models. It uses an inline for `UserSettings` to manage user preferences directly within the user admin page.
 
### `pantry` app

This is the core app for managing products, searching, and interacting with the user's pantry.

* **`models.py`:** Defines the **`Pantry`**, **`PantryItem`**, and **`Product`** models. `PantryItem` is the central through-model linking a `User`'s `Pantry` to a `Product` and storing the quantity. The `Pantry` model also contains methods to calculate aggregate Nutri-Score and Eco-Score grades based on its contents.

* **`views.py`:** Manages all views related to finding and managing products. This includes:
    *   The main pantry display (`pantry_view`), which checks for user dietary conflicts.
    *   API-style views for basic (`search_product`) and advanced (`advanced_product_search`) searches, which build complex API queries using helpers from `pantry.utils`. These views also check for dietary and allergen conflicts against user settings.
    *   Views that act as endpoints for frontend JavaScript, such as `add_product`, `remove_pantryitem`, and `toggle_favourite_product`.
*   **`forms.py`:** Contains the `ProductSearchForm` for validating basic search and barcode scan inputs.

* **`utils.py`:** A critical file containing helper functions that interact with the Open Food Facts API. It includes rate-limited functions for fetching products by barcode or name, building complex search parameters, and saving/updating product data in the local `Product` model. It also contains the `get_localised_names` function, which translates API tags (e.g., `en:milk`) into human-readable, localised names using cached data.

* **`signals.py`:** Defines `post_save` and `post_delete` signals on the `PantryItem` model. These signals are the primary trigger for AI recipe generation; they call `schedule_recipe_generation_task`, which debounces requests and dispatches a `recipes.tasks.generate_recipes_task` to Celery.

* **`static/pantry/pantry.js`:** Contains JavaScript for the pantry page, handling real-time search/filtering of pantry items and removing items from the pantry via AJAX requests.
 
### `recipes` app

This app is responsible for generating, managing, and displaying AI-powered recipes.

* **`models.py`:** Defines the **`SuggestedRecipe`** and **`SavedRecipe`** models. `SuggestedRecipe` stores the raw JSON output from the AI, the original prompt, and links to the `pantry.Product` models used. This design is intentional for future scalability, allowing the collected data to be used as a dataset for training a custom, local recipe-generation model. `SavedRecipe` stores a user-saved version with structured ingredient data.

* **`tasks.py`:** Contains the most critical asynchronous tasks:
    *   `generate_recipes_task`: This Celery task is the heart of the AI feature. It takes a user's pantry contents, formats a detailed prompt, calls the Google Gemini AI API with a required JSON schema, and saves the results as `SuggestedRecipe` instances.
    *   `update_recent_recipes_status`: A periodic task run by Celery Beat to clean up old, unseen recipe suggestions.
* **`utils.py`:** Defines the `RECIPES_ARRAY_SCHEMA` that is sent to the Gemini API. This schema forces the AI to return a structured JSON response, ensuring the data is predictable and can be reliably parsed and saved to the database.
* **`views.py`:** Contains the main `recipes_view` to display new, recent, and saved recipes. It also includes logic to check which ingredients for a saved recipe are currently in the user's pantry. AJAX-based views for saving and deleting recipes are also here.
* **`static/recipes/recipes.js`:** JavaScript for the recipes page, handling user interactions like saving a suggested recipe or deleting a saved one without a full page reload.
 
### Other Key Files
*   **`static/` (Root Directory):** Contains all frontend assets:
    *   `savor.js`: The main JavaScript file for the application. It handles global functionality like sidebar navigation, barcode scanning initialisation (`html5-qrcode`), product search (including autocomplete suggestions), and dynamic rendering of search results and favourite products.
*   **`templates/` (Root Directory):** Contains all base HTML templates (like `layout.html`) and the app-specific templates organised in sub-directories (`users/`, `pantry/`, `recipes/`).
*   **`requirements.txt`:** Lists all Python dependencies required to run the project, including `django`, `celery`, `redis`, `google-genai`, `django-ratelimit`, etc.


 
## Usage

This section outlines how to use Savor, both for developers looking to run the project locally and for end-users interacting with the live application.

### For Users (Application Workflow)

Savor is designed to be an intuitive and powerful kitchen assistant. Heres a typical user journey:

1.  **Account Management:**
    *   **Registration & Login:** New users can register for an account, which automatically creates a personal pantry. The application includes standard login, password change, and password reset functionalities.
    
        **Note on Password Reset:** In this local development setup, password reset emails are not sent to an actual inbox. Instead, the reset link is printed to the terminal where the Django development server is running (`Terminal 4` in the setup instructions). This is because `settings.py` uses Django's console email backend via the setting: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`. For a production deployment, this would need to be changed to a real email service (like SendGrid or Mailgun).

    *   **Account Deletion:** Users have the option to permanently delete their account and all associated data through the account settings page.

2.  **Personalisation (User Settings):**
    *   After logging in, users can navigate to **Account Settings** to tailor their experience.
    *   **Localisation:** Set a preferred language from 33 options. The entire UI, including product data fetched from the API, will be translated. Users can also set their country to prioritise local search results.
    *   **Dietary Preferences:** Specify any allergies (e.g., peanuts, gluten) and dietary requirements (e.g., vegan, halal). This is a critical step for the next feature.
    *   **UI Preferences:** Toggle the visibility of Nutri-Score and Eco-Score on products and enable the "scan-to-add" feature for quickly adding items to the pantry after a barcode scan.

3.  **Finding & Managing Products:**
    *   **Search:** Users can find products using a simple text search, an advanced search with filters (category, brand, country), or by scanning a product's barcode with their device's camera.
        
        **Note on Unauthenticated Access:** Basic search functionality is available to all visitors. However, features like adding products to a pantry, favouriting items, viewing the pantry, and receiving AI-generated recipes require user authentication.
    *   **Conflict Highlighting:** When viewing search results or favourited products as a logged-in user, the application will automatically display prominent warnings if a product conflicts with the user's specified allergies or does not meet their dietary requirements.
    *   **Favourites:** Products can be "favourited" for quick access from the homepage.

4.  **Pantry Management:**
    *   **Adding Items:** Users can add any product to their virtual pantry, specifying the quantity.
    *   **Viewing the Pantry:** The pantry page displays all current items and includes a "search-as-you-type" filter to instantly find items in the pantry. It also shows aggregate Nutri-Score and Eco-Score grades for the pantry's entire contents.
    *   **Removing Items:** As items are used, they can be removed from the pantry by a specified quantity.

5.  **AI Recipe Generation & Saving:**
    *   **Automatic Generation:** When a user logs in or modifies their pantry (by adding or removing items), a background task is automatically triggered to generate new, personalised recipes using Google's Gemini AI. The AI is prompted to create recipes using *only* the ingredients currently available in the user's pantry.
    *   **Viewing Suggestions:** On the "Recipes" page, users can view newly generated suggestions. Unseen recipes are highlighted in orange to draw attention; this highlight is removed once the recipe is expanded. A loading indicator is shown while the AI is working.
    *   **Saving Recipes:** If a user likes a suggested recipe, they can save it. This moves it to a permanent "Saved Recipes" list.
    *   **Ingredient Checking:** When viewing a saved recipe, the application cross-references the required ingredients with the current pantry contents, highlighting which ingredients are available and which are missing.

### For Developers (Running Locally)

These instructions are for running the application on a **local development server** and are not intended for a production deployment.
 
To run this application locally, you will need to have Python, Redis, and `pip` installed.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-project-directory>
    ```

2.  **Set up Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a `.env` file in the root directory (where `manage.py` is) and add your secret keys:
    ```.env
    SECRET_KEY='<your-django-secret-key>'
    GOOGLE_API_KEY='<your-google-api-key>'
    ```

5.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start Required Services:**
    This application requires **three** separate terminal processes to be running concurrently:
    * **Terminal 1: Start Redis Server** (if not already running as a service)
        ```bash
        redis-server
        ```
    * **Terminal 2: Start Celery Worker**
        ```bash
        celery -A savor worker -l info
        ``` 
    * **Terminal 3: Start Celery Beat Scheduler**
        ```bash
        celery -A savor beat -l info --scheduler redbeat.RedBeatScheduler
        ```

7.  **Run the Django App:**
    * **Terminal 4: Start the Django Development Server**
        ```bash
        python manage.py runserver
        ```

8.  **Initial Data Population (CRUCIAL FIRST STEP):**
    The app's advanced search and user settings rely on "facet data" (categories, countries, brands, etc.) from the Open Food Facts API, which must be stored in the Redis cache. On a fresh install, this cache is empty, and **the search/settings pages will not work correctly.**

    You must trigger a manual task to populate this cache. This task is handled asynchronously by Celery, so **you can browse other parts of the app** (like registration/login) while it runs in the background.

    **NOTE:** Due to API rate limits and the 33 languages being fetched, this initial population is **very slow** and can take **1.5 to 2 hours** to complete. Yes, you read that right. Go make a cup of tea. Or perhaps a three-course meal. Maybe learn a new language, since you'll have the time. The app will be ready when you get back. Probably.

    * Open a **new (fifth) terminal** and activate the virtual environment:
        ```bash
        source venv/bin/activate 
        ```
    * Run the Django shell:
        ```bash
        python manage.py shell
        ```
    * Inside the shell, import and run the task:
        ```python
        from savor.tasks import update_facet_data
        update_facet_data.delay()
        exit()
        ```
    * You can monitor the task's progress in your **Celery Worker (Terminal 2)** log. The advanced search and settings pages will become fully functional once this task completes.

9.  **Access the Application:**
    Access the application at `http://127.0.0.1:8000` in your web browser.



## Additional Information

* **Python Dependencies:** All required Python packages are listed in the `requirements.txt` file, as per the project instructions.


For a more detailed and complete, step-by-step representation of this application's development lifecycle, please refer to my public GitHub repository here: https://github.com/mnmfullmetal/savor