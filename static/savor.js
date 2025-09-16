
document.addEventListener("DOMContentLoaded", () => {

  const savedState = localStorage.getItem("sidebarState");
  const body = document.body;
  const toggleIcon = document.getElementById("sidebarToggle").querySelector("i");
  if (savedState === "minimized") {
    body.classList.add("sidebar-minimized");
    toggleIcon.classList.remove("bi-box-arrow-in-left");
    toggleIcon.classList.add("bi-box-arrow-right");
  }

  const sidebarToggle = document.getElementById("sidebarToggle");
  sidebarToggle.addEventListener("click", () => {
    const body = document.body;
    const toggleIcon = sidebarToggle.querySelector("i");
    body.classList.toggle("sidebar-minimized");

    if (body.classList.contains("sidebar-minimized")) {
      localStorage.setItem("sidebarState", "minimized");
      toggleIcon.classList.remove("bi-box-arrow-in-left");
      toggleIcon.classList.add("bi-box-arrow-right");
    } else {
      localStorage.setItem("sidebarState", "expanded");
      toggleIcon.classList.remove("bi-box-arrow-right");
      toggleIcon.classList.add("bi-box-arrow-in-left");
    }
  });

  const accountDropdown = document.getElementById("account-dropdown-item");
  if (accountDropdown) {
    accountDropdown.addEventListener("show.bs.dropdown", function () {
      if (document.body.classList.contains("sidebar-minimized")) {
        document.body.classList.remove("sidebar-minimized");
        document.getElementById("sidebarToggle").querySelector("i").classList.add("bi-box-arrow-in-left");
        document.getElementById("sidebarToggle").querySelector("i").classList.remove("bi-box-arrow-right");
      }
    });
  }

  document.getElementById("scan-button").addEventListener("click", () => {
    document.getElementById("scanner-container").style.display = "block";
    document.getElementById("searched-product-section").innerHTML = "";
    startScanner(csrfToken);
  });

  document.getElementById("stop-scanner-btn").addEventListener("click", () => {
    Quagga.stop();
    document.getElementById("scanner-container").style.display = "none";
  });

  const productSearchForm = document.querySelector("#search-form");
  const csrfToken = productSearchForm.elements.csrfmiddlewaretoken.value;
  const productNameInput = document.getElementById("product_name_input");
  const autocompleteSuggestionsDiv = document.getElementById("autocomplete-suggestions");
  const debounceSpeed = 200; 
  productNameInput.addEventListener("input",debounce(async (event) => {
    const query = event.target.value.trim();

    if (query.length === 0) {
      autocompleteSuggestionsDiv.innerHTML = "";
      return;
    }

    fetch(`/suggestions/?query=${encodeURIComponent(query)}`)
    .then((response) => response.json())
    .then((data) => {
      const suggestionsArray = data.suggestions;
      displaySuggestions(suggestionsArray);
    })
    .catch((error) => {
      console.error("Error fetching suggestions:", error);
      autocompleteSuggestionsDiv.innerHTML =
            '<div class="list-group-item text-danger">Failed to load suggestions.</div>';
    });
  }, debounceSpeed));

  productSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const barcode = productSearchForm.elements.barcode.value.trim();
    const productName = productSearchForm.elements.product_name.value.trim();
    const currentPath = window.location.pathname;

    if (currentPath !== "index" && currentPath !== "/") {
     
      sessionStorage.setItem("searchBarcode", barcode);
      sessionStorage.setItem("searchProductName", productName);
      sessionStorage.setItem("searchCsrfToken", csrfToken);
      window.location.href = "/";
    } else {
      searchProduct(barcode, productName, csrfToken);
      productNameInput.value = '';

    }
  });

  const savedBarcode = sessionStorage.getItem("searchBarcode");
  const savedProductName = sessionStorage.getItem("searchProductName");
  const savedCsrfToken = sessionStorage.getItem("searchCsrfToken");

  if (savedBarcode || savedProductName) {
    sessionStorage.removeItem("searchBarcode");
    sessionStorage.removeItem("searchProductName");
    sessionStorage.removeItem("searchCsrfToken");

    const barcodeInput = document.querySelector("#search-form").elements.barcode;
    const productNameInput = document.querySelector("#search-form").elements.product_name;

    if (barcodeInput) barcodeInput.value = savedBarcode;
    if (productNameInput) productNameInput.value = savedProductName;

    searchProduct(savedBarcode, savedProductName, savedCsrfToken);
    productNameInput.value = '';
  }

  const initialFavoriteButtons = document.querySelectorAll(".favourite-btn");
  const initialAddButtons = document.querySelectorAll(".add-btn");
  initialFavoriteButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      const clickedButton = event.target;
      const productIdToFav = clickedButton.dataset.productId;
      favouriteProduct(productIdToFav, csrfToken, clickedButton);
    });
  });

  initialAddButtons.forEach((button) => {
    const productCard = button.closest(".card");
    button.addEventListener("click", (event) => {
      const clickedButton = event.target;
      const productIdToAdd = clickedButton.dataset.productId;
      const quantityInput = productCard.querySelector(
        ".product-quantity-input"
      ).value;
      addProduct(productIdToAdd, quantityInput, csrfToken, productCard);
    });
  });

  const advSearchForm = document.getElementById("advSearchForm")
  if (advSearchForm){

    advSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const search_term = advSearchForm.elements.product_name.value.trim()
    const country = advSearchForm.elements.countries_tags.value.trim()
    const category = advSearchForm.elements.categories_tags.value.trim()
    const brand = advSearchForm.elements.brands_tags.value.trim()
    const csrfToken = advSearchForm.elements.csrfmiddlewaretoken.value;

    const searchRequestData = {
      search_term: search_term,
      country:country,
      category:category,
      brand:brand,
    }
    
    advProductSearch(searchRequestData, csrfToken)
    })
  }
});


function searchProduct(barcode = "None", productName = "None", csrfToken, page = 1) {
  const searchedProductsDiv = document.querySelector("#searched-product-section");
  searchedProductsDiv.innerHTML = "<p class='text-muted'>Searching...</p>";

  if (!barcode && !productName) {
    searchedProductsDiv.innerHTML = `
    <div class="alert alert-warning text-center mt-3" role="alert">
    Please enter a barcode or product name to search.
    </div>`;
    return;
  }

  const requestData = {
    barcode: barcode,
    product_name: productName,
    page: page
  };

  fetch("/product/search/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(requestData),
  })
  .then((response) => response.json())
  .then((data) => {
    console.log("Response from Django API:", data);
    if (data.error || data.errors) {
      const errorMessage = data.error || JSON.parse(data.errors);
      console.error("Error from backend:", errorMessage);
      searchedProductsDiv.innerHTML = `
      <div class="alert alert-danger text-center mt-3" role="alert">
       Error: ${data.error || "Invalid input."}
       </div>`;
    } else  {
       displayProducts(searchedProductsDiv, data, csrfToken, {barcode, productName}, (params, token) => searchProduct(params.barcode, params.productName, token, params.page));
    } 
  })
  .catch((error) => {
        console.error("Fetch network error:", error);
        searchedProductsDiv.innerHTML = `
        <div class="alert alert-danger text-center mt-3" role="alert">
            A network error occurred. Please check your connection.
        </div>`;
  });
}




function advProductSearch(searchRequestData, csrfToken){
  const searchedProductsDiv = document.querySelector("#searched-product-section");
  searchedProductsDiv.innerHTML = "<p class='text-muted'>Searching...</p>";
  
  fetch("/product/adv_search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(searchRequestData),
  })
  .then((response) => response.json())
  .then((data) => {
    console.log("Response from Django API:", data);
    if (data.error || data.errors) {
      const errorMessage = data.error || JSON.parse(data.errors);
      console.error("Error from backend:", errorMessage);
      searchedProductsDiv.innerHTML = `
      <div class="alert alert-danger text-center mt-3" role="alert">
       Error: ${data.error || "Invalid input."}
       </div>`;
    } else {
       displayProducts(searchedProductsDiv, data, csrfToken, searchRequestData, advProductSearch);
    }
   })      
  .catch((error) => {
        console.error("Fetch network error:", error);
        searchedProductsDiv.innerHTML = `
            <div class="alert alert-danger text-center mt-3" role="alert">
                A network error occurred. Please check your connection.
            </div>`;
    });
}


function displayProducts(container, data, csrfToken, searchParams, searchFunction) {
  if (data.products && data.products.length > 0) {
    container.innerHTML = "";
    data.products.forEach((product) => {
      const productColumnDiv = document.createElement("div");
      productColumnDiv.classList.add(
        "col-12",
        "col-sm-6",
        "col-md-4",
        "col-lg-4",
        "mb-4"
      );

      const productCard = document.createElement("div");
      productCard.classList.add("card", "h-100", "border-0", "shadow-sm");
      const placeholderImageUrl = "/static/media/placeholder-img.jpeg";
      const imageUrl = product.image_url || placeholderImageUrl;

      productCard.innerHTML = `
        <div class="card h-100 border-0 shadow-sm">
          <img src="${imageUrl}" 
             alt="${product.product_name || "Product Image"}" 
             class="card-img-top img-fluid rounded-top" 
             style="max-height: 150px; object-fit: cover;"
             onerror="this.onerror=null;this.src='${placeholderImageUrl}';">
          <div class="card-body d-flex flex-column justify-content-between">
            <h3 class="card-title h5 mb-2 text-dark">${
              product.product_name || "No Name"
            }</h3>
            
            <p class="card-text text-muted mb-1 small"><strong>Brands:</strong> ${
              product.brands || "N/A"
            }</p>
            <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${
              product.code || "N/A"
            }</p>

            <div class="d-flex align-items-center mb-3">
              <input class="product-quantity-input form-control me-2" type="number" min="0.01" step="0.01" value="1">
              <span class="text-secondary me-1">${
                product.product_quantity || ""
              }</span>
              <span class="text-muted small">${
                product.product_quantity_unit || "item"
              }</span>
            </div>

            <div class="mt-auto d-flex flex-column">
              <button class="btn btn-outline-primary btn-sm mb-2 add-btn" 
                      data-product-name="${
                        product.product_name || "No Name"
                      }" 
                      data-product-id="${product.id}">
                Add to Pantry
              </button>
              <button class="btn btn-sm favourite-btn ${
                product.is_favourited
                  ? "btn-outline-danger"
                  : "btn-outline-primary"
              }" data-product-id="${product.id}">
                ${product.is_favourited ? "Remove Favourite" : "Favourite"}
              </button>
            </div>
          </div>
        </div>`;

      productColumnDiv.appendChild(productCard);
      container.appendChild(productColumnDiv);

      const favouriteButton = productCard.querySelector(".favourite-btn");
      favouriteButton.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const productIdToFav = clickedButton.dataset.productId;
        favouriteProduct(productIdToFav, csrfToken, clickedButton);
      });

      const addButton = productCard.querySelector(".add-btn");
      addButton.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const productIdToAdd = clickedButton.dataset.productId;
        const quantityInput = productCard.querySelector(
          ".product-quantity-input"
        ).value;
        addProduct(productIdToAdd, quantityInput, csrfToken, productCard);
      });
    });

   const totalCount = data.count;
  const pageSize = data.page_size;
  const currentPage = data.page_count;
  const totalPages = Math.ceil(totalCount / pageSize);

  if (totalPages > 1) { 
   const paginationDiv = document.createElement("nav");
   paginationDiv.setAttribute("aria-label", "Page navigation");
   
   let paginationHtml = `<ul class="pagination justify-content-center">`;
   
   paginationHtml += `
    <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
     <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
    </li>`;

    const maxLinks = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxLinks / 2));
    let endPage = Math.min(totalPages, startPage + maxLinks - 1);

    if (endPage - startPage + 1 < maxLinks) {
        startPage = Math.max(1, endPage - maxLinks + 1);
    }
    
    if (startPage > 1) {
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (startPage > 2) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
    }

   paginationHtml += `
    <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
     <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
    </li>`;
   paginationHtml += `</ul>`;
   
   paginationDiv.innerHTML = paginationHtml;
   container.appendChild(paginationDiv);

   paginationDiv.querySelectorAll('.page-link').forEach(link => {
    link.addEventListener('click', (event) => {
     event.preventDefault();
     const newPage = parseInt(event.target.dataset.page);
     if (newPage !== currentPage) {
      const newSearchParams = { ...searchParams, page: newPage };
      searchFunction(newSearchParams, csrfToken);
     }
    });
   });
  }
 } else {
  container.innerHTML = `
   <div class="alert alert-info text-center mt-3" role="alert">
    No products found. Try a different search term.
   </div>`;
 }
}


function addProduct(productIdToAdd, quantityInput, csrfToken, productCard) {
  if (isNaN(quantityInput) || parseFloat(quantityInput) <= 0) {
    const cardBody = productCard.querySelector(".card-body");
    let messageElement = cardBody.querySelector(".alert");
    if (!messageElement) {
      messageElement = document.createElement("div");
      cardBody.appendChild(messageElement);
    }
    messageElement.className = "alert alert-success mt-2 py-1";
    messageElement.textContent = "Please enter a valid quantity (> 0).";
    setTimeout(() => {
      messageElement.remove();
    }, 3000);
    return;
  }

  const addProductRequestData = {
    product_id: productIdToAdd,
    quantityToAdd: quantityInput,
  };

  fetch(`/pantry/add_product`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(addProductRequestData),
  })
    .then((response) => {
      if (response.status === 401) {
        window.location.href = "/accounts/login";
        throw new Error("Redirecting to login page...");
      }
      return response.json();
    })
    .then((data) => {
      const cardBody = productCard.querySelector(".card-body");
      let messageElement = cardBody.querySelector(".alert");
      if (!messageElement) {
        messageElement = document.createElement("div");
        cardBody.appendChild(messageElement);
      }
      messageElement.className = `alert mt-2 py-1 ${
        data.success ? "alert-success" : "alert-danger"
      }`;
      messageElement.innerHTML = `${data.message}`;
      setTimeout(() => {
        messageElement.remove();
      }, 3000);
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      const cardBody = productCard.querySelector(".card-body");
      let messageElement = cardBody.querySelector(".alert");
      if (!messageElement) {
        messageElement = document.createElement("div");
        cardBody.appendChild(messageElement);
      }
      messageElement.className = "alert alert-danger mt-2 py-1";
      messageElement.innerHTML = "A network error occurred.";
      setTimeout(() => {
        messageElement.remove();
      }, 3000);
    });
}

function favouriteProduct(productIdToFav, csrfToken, clickedButton) {
  fetch(`/favourite_product/${productIdToFav}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      clickedButton.textContent = data.is_favourited
        ? "Remove Favourite"
        : "Favourite";

      if (data.is_favourited) {
        updateFavouriteSection(data.product, true, csrfToken);
        clickedButton.classList.remove("btn-outline-primary");
        clickedButton.classList.add("btn-outline-danger");
      } else {
        updateFavouriteSection(data.product, false, csrfToken);
        clickedButton.classList.remove("btn-outline-danger");
        clickedButton.classList.add("btn-outline-primary");
      }
    })
    .catch((error) => console.error("Error toggling favourite:", error));
}

function updateFavouriteSection(product, is_favourited, csrfToken) {
  const favouriteSection = document.querySelector(".product-cards-wrapper");

  const emptyMessage = favouriteSection.querySelector("p.text-muted");

  if (is_favourited) {
    if (emptyMessage) {
      emptyMessage.remove();
    }

    const newFavouriteCard = document.createElement("div");
    newFavouriteCard.className = "product-card-wrapper";

    const productCard = document.createElement("div");
    productCard.classList.add("card", "h-100", "shadow-sm");

    productCard.innerHTML = `
    <div class="card h-100 border-0 shadow-sm">
      ${
        product.image_url
          ? `<img src="${product.image_url}" alt="${
              product.product_name || "Product Image"
            }" class="card-img-top img-fluid rounded-top" style="max-height: 150px; object-fit: cover;">`
          : ""
      }
      <div class="card-body d-flex flex-column justify-content-between">
        <h3 class="card-title h5 mb-2 text-dark">${
          product.product_name || "No Name"
        }</h3>
        
        <p class="card-text text-muted mb-1 small"><strong>Brands:</strong> ${
          product.brands || "N/A"
        }</p>
        <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${
          product.code || "N/A"
        }</p>

        <div class="d-flex align-items-center mb-3">
          <input class="product-quantity-input form-control me-2" type="number" min="0.01" step="0.01" value="1">
          <span class="text-secondary me-1">${
            product.product_quantity || ""
          }</span>
          <span class="text-muted small">${
            product.product_quantity_unit || "item"
          }</span>
        </div>

        <div class="mt-auto d-flex flex-column">
          <button class="btn btn-outline-primary btn-sm mb-2 add-btn" 
                  data-product-name="${product.product_name || "No Name"}" 
                  data-product-id="${product.id}">
            Add to Pantry
          </button>
          <button class="btn btn-outline-danger btn-sm favourite-btn" 
                  data-product-id="${product.id}">
            Remove Favourite
          </button>
        </div>
      </div>
    </div>`;

    newFavouriteCard.appendChild(productCard);

    favouriteSection.append(newFavouriteCard);

    const favouriteButton = newFavouriteCard.querySelector(".favourite-btn");
    favouriteButton.addEventListener("click", (event) => {
      const clickedButton = event.target;
      const productIdToFav = clickedButton.dataset.productId;
      favouriteProduct(productIdToFav, csrfToken, clickedButton);
    });

    const addButton = newFavouriteCard.querySelector(".add-btn");
    addButton.addEventListener("click", (event) => {
      const clickedButton = event.target;
      const productIdToAdd = clickedButton.dataset.productId;
      const quantityInput = newFavouriteCard.querySelector(
        ".product-quantity-input"
      ).value;
      addProduct(productIdToAdd, quantityInput, csrfToken, newFavouriteCard);
    });
  } else {
    const cardToRemove = favouriteSection
      .querySelector(`[data-product-id="${product.id}"]`)
      .closest(".product-card-wrapper");

    cardToRemove.classList.add("fade-out");

    setTimeout(() => {
      cardToRemove.remove();
    }, 400);
  }
}

function startScanner(csrfToken) {
  Quagga.init(
    {
      inputStream: {
        name: "Live",
        type: "LiveStream",
        target: document.querySelector("#interactive"),
        constraints: {
          width: { min: 640 },
          height: { min: 480 },
          facingMode: "environment",
        },
      },
      decoder: {
        readers: [
          "ean_reader",
          "upc_reader",
          "upc_e_reader",
          "ean_8_reader",
          "code_39_reader",
        ],
      },
    },
    function (err) {
      if (err) {
        console.error(err);
        return;
      }
      console.log("Initialization finished. Ready to start");
      Quagga.start();
    }
  );

  Quagga.onDetected(function (result) {
    const barcode = result.codeResult.code;
    console.log("Barcode detected:", barcode);
    Quagga.stop();
    document.getElementById("scanner-container").style.display = "none";

    searchProduct(barcode, "", csrfToken);
  });
}

function displaySuggestions(suggestions) {
  const autocompleteSuggestionsDiv = document.getElementById("autocomplete-suggestions");
  const productNameInput = document.getElementById("product_name_input");

  autocompleteSuggestionsDiv.innerHTML = "";

  if (!suggestions || suggestions.length === 0) {
    return;
  }

  suggestions.forEach((suggestion) => {
    const suggestionItem = document.createElement("a");
    suggestionItem.classList.add("list-group-item", "list-group-item-action");
    suggestionItem.href = "#";
    suggestionItem.textContent = suggestion;

    suggestionItem.addEventListener("click", () => {
      productNameInput.value = suggestion;
      autocompleteSuggestionsDiv.innerHTML = "";
    });

    document.addEventListener("click", () => { 
      autocompleteSuggestionsDiv.innerHTML = "";
    })

    autocompleteSuggestionsDiv.appendChild(suggestionItem);
  });
}

function debounce(func, delay) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}
