let html5QrCode = null;

const readerId = "reader";
const config = { 
    fps: 10, 
    qrbox: { width: 250, height: 250 }
};

function onScanSuccess(decodedText, decodedResult) {
  console.log(`Code matched = ${decodedText}`, decodedResult);
  const productSearchForm = document.querySelector("#searchForm");
  const csrfToken = productSearchForm.elements.csrfmiddlewaretoken.value;
  productSearchForm.elements.barcode.value = decodedText;
  const wasScanned = true
  handleProductSearch(productSearchForm, csrfToken, wasScanned); 

  stopScanningAndHide(); 

}

function onScanFailure(error) {
    //console.warn(`Scan error: ${error}`);
}

function stopScanningAndHide() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop()
            .then(() => {
                console.log("QR Code scanning stopped.");
                document.getElementById("scanner-container").style.display = "none";
                document.getElementById(readerId).innerHTML = ""; 
                html5QrCode = null; 
            })
            .catch((err) => {
                console.error("Failed to stop scanning:", err);
                document.getElementById("scanner-container").style.display = "none";
            });
    } else {
        document.getElementById("scanner-container").style.display = "none";
    }
}


document.addEventListener("DOMContentLoaded", () => {

  const body = document.body;
  const desktopSidebarToggle = document.getElementById("sidebarToggle");

  if (desktopSidebarToggle) {
    const toggleIcon = desktopSidebarToggle.querySelector("i");

    const savedState = localStorage.getItem("sidebarState");
    if (savedState === "minimized") {
      body.classList.add("sidebar-minimized");
      toggleIcon.classList.remove("bi-box-arrow-in-left");
      toggleIcon.classList.add("bi-box-arrow-right");
    }

    desktopSidebarToggle.addEventListener("click", () => {
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
}

  const scanButtons = document.querySelectorAll(".scan-button")
  scanButtons.forEach(button => {
    button.addEventListener("click", () => {
     body.classList.add("sidebar-minimized");
      document.getElementById("sidebarToggle").querySelector("i").classList.remove("bi-box-arrow-in-left");
      document.getElementById("sidebarToggle").querySelector("i").classList.add("bi-box-arrow-right");
      startScanner();
    });

    
  })

  document.getElementById("stop-scanner-btn").addEventListener("click", () => {
        stopScanningAndHide();
    });

  const searchForms = document.querySelectorAll("#searchForm, #searchFormMobile");
  searchForms.forEach(form => {
      const csrfToken = form.elements.csrfmiddlewaretoken.value;
      const productNameInput = form.querySelector("input[name='product_name']");
      const autocompleteSuggestionsDiv = form.querySelector(".list-group");
      const debounceSpeed = 300;

      if (productNameInput && autocompleteSuggestionsDiv) {
          productNameInput.addEventListener("input", debounce(async (event) => {
              const query = event.target.value.trim();

              if (query.length === 0) {
                  autocompleteSuggestionsDiv.innerHTML = "";
                  return;
              }

              fetch(`/suggestions/?query=${encodeURIComponent(query)}`)
                  .then((response) => response.json())
                  .then((data) => {
                      const suggestionsArray = data.suggestions;
                      displaySuggestions(suggestionsArray, autocompleteSuggestionsDiv, productNameInput);
                  })
                  .catch((error) => {
                      console.error("Error fetching suggestions:", error);
                      autocompleteSuggestionsDiv.innerHTML =
                          '<div class="list-group-item text-danger">Failed to load suggestions.</div>';
                  });
          }, debounceSpeed));
      }

      form.addEventListener("submit", (event) => {
          event.preventDefault();
          const wasScanned = false;
          handleProductSearch(form, csrfToken, wasScanned);
      });
  });

  const csrfToken = document.querySelector("#searchFormMobile, #searchForm").elements.csrfmiddlewaretoken.value;

  const savedBarcode = sessionStorage.getItem("searchBarcode");
  const savedProductName = sessionStorage.getItem("searchProductName");
  const wasScannedString = sessionStorage.getItem("wasScanned");
  
  if (savedBarcode || savedProductName) {
    const csrfToken = document.querySelector("#searchForm, #searchFormMobile").elements.csrfmiddlewaretoken.value;

    sessionStorage.removeItem("searchBarcode");
    sessionStorage.removeItem("searchProductName");
    sessionStorage.removeItem("searchCsrfToken");
    sessionStorage.removeItem("wasScanned");

    const barcodeInput = document.querySelector("#searchForm").elements.barcode;
    const productNameInput = document.querySelector("#searchForm").elements.product_name;

    if (barcodeInput) barcodeInput.value = savedBarcode;
    if (productNameInput) productNameInput.value = savedProductName;

    const wasScanned = wasScannedString === 'true';
    
    searchProduct(savedBarcode, savedProductName, csrfToken, wasScanned, page=1);
    if (barcodeInput) barcodeInput.value = '';
    if (productNameInput) productNameInput.value = '';
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

  const categorySelect = document.getElementById('categorySelect');
  const brandSelect = document.getElementById('brandSelect');
  const countrySelect = document.getElementById('countrySelect');
  if (categorySelect && brandSelect && countrySelect){
  fetchAndPopulateDropdowns(categorySelect, brandSelect, countrySelect );
  }

});



function fetchAndPopulateDropdowns(categorySelect, brandSelect, countrySelect) {
  brandSelect.innerHTML = brandSelect.options[0].outerHTML;
  categorySelect.innerHTML = categorySelect.options[0].outerHTML;
  countrySelect.innerHTML = countrySelect.options[0].outerHTML;

  fetch(`/adv_search/populate_criteria`)
  .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
  .then(data => {
    const categoryNames = data.categories;
    const brandNames = data.brands;
    const countryNames = data.countries;

    categoryNames.sort();
    brandNames.sort();
    countryNames.sort();

    categoryNames.forEach(name => {
      const categoryOption = document.createElement("option");
      categoryOption.value = name;
      categoryOption.textContent = name;
      categorySelect.appendChild(categoryOption)
    });

    brandNames.forEach(name => {
      const brandOption = document.createElement("option");
      brandOption.value = name;
      brandOption.textContent = name;      
      brandSelect.appendChild(brandOption)
    });

    countryNames.forEach(name => {
      const countryOption = document.createElement('option')
      countryOption.value = name;
      countryOption.textContent = name;
      countrySelect.appendChild(countryOption)
    })
  })
}


function handleProductSearch(form, csrfToken, wasScanned) {
    const barcode = form.elements.barcode.value.trim();
    const productName = form.elements.product_name.value.trim();
    const currentPath = window.location.pathname;

    if (!barcode && !productName) {
        return; 
    }

    if (currentPath !== "/" && currentPath !== "/index/") { 

        sessionStorage.setItem("searchBarcode", barcode);
        sessionStorage.setItem("searchProductName", productName);
        sessionStorage.setItem("wasScanned", wasScanned)
        sessionStorage.setItem("searchCsrfToken", csrfToken);
        
        window.location.href = "/";
        form.elements.barcode.value = ''; 
        form.elements.product_name.value = '';
    } else {
        searchProduct(barcode, productName, csrfToken, wasScanned, page = 1);
        form.reset();
    }
}


function searchProduct(barcode = "None", productName = "None", csrfToken, wasScanned, page = 1) {
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
    page: page,
    wasScanned: wasScanned
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
       displaySearchResults(searchedProductsDiv, data, csrfToken, {barcode, productName}, (params, token) => searchProduct(params.barcode, params.productName, token, wasScanned, params.page));
        console.log(`scan to add: ${data.scan_to_add}`)
       if(data.scan_to_add === true && data.products.length > 0 && wasScanned === true){
        data.products.forEach(product => {
        console.log(`adding product: ${product.id}`)
        addProduct(product.id, quantityInput=1, csrfToken=csrfToken )
        });
       }
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
       displaySearchResults(searchedProductsDiv, data, csrfToken, searchRequestData, advProductSearch);
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


function displaySearchResults(container, data, csrfToken, searchParams, searchFunction) {
  if (data.products && data.products.length > 0) {
    container.innerHTML = "";
    data.products.forEach((product) => {
      const productColumnDiv = document.createElement("div");
      productColumnDiv.classList.add("col-12", "col-sm-6", "col-md-4", "col-lg-4", "mb-4");
      const hasAllergenConflict = product.has_allergen_conflict;
      const hasDietaryMismatch = product.has_dietary_mismatch;
      const missingTags = product.missing_dietary_tags || [];
      const conflictingTags = product.conflicting_allergens || []; 
      let safetyAlertsHtml = '';
      let cardClasses = "card h-100 border-0 shadow-sm";

      if (hasAllergenConflict) {
        const conflictingTagsList = conflictingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        cardClasses = "card h-100 shadow-lg border-danger border-3"; 
        safetyAlertsHtml += `
        <div class="alert alert-danger p-1 mb-2 small" role="alert">
        <strong> <i class="bi bi-exclamation-circle"></i>  WARNING : </strong> Contains user-specified allergens: ${conflictingTagsList}
        </div>`;
      }
            
      if (hasDietaryMismatch) {
        const missingTagsList = missingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        safetyAlertsHtml += `
        <div class="alert alert-warning p-1 mb-2 small" role="alert">
        <strong> <i class="bi bi-question-circle"></i>  POSSIBLE MISMATCH : </strong> Missing dietary requirements: ${missingTagsList}.
        </div>`;
      }

      const productCard = document.createElement("div");
      productCard.classList.add(...cardClasses.split(' '));
      const placeholderImageUrl = "/static/media/placeholder-img.jpeg";
      const imageUrl = product.image_url || placeholderImageUrl;

      productCard.innerHTML = `
          <img src="${imageUrl}" 
             alt="${product.product_name || "Product Image"}" 
             class="card-img-top img-fluid rounded-top" 
             style="max-height: 150px; object-fit: cover;"
             onerror="this.onerror=null;this.src='${placeholderImageUrl}';">
          <div class="card-body d-flex flex-column justify-content-between">
            <h3 class="card-title h5 mb-2 text-dark">${
              product.product_name || "No Name"
            }</h3>
            <div>
            <p class="card-text text-muted mb-1 small"><strong>Brands:</strong> ${
              product.brands || "N/A"
            }</p>
            <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${
              product.code || "N/A"
            }</p>
            </div>
            <div>
             ${safetyAlertsHtml} 
             </div>
            <div class="d-flex align-items-center mb-3">
              <input class="product-quantity-input form-control me-2" type="number" min="1.00" step="1.00" value="1">
              <span class="text-secondary me-1">${
                product.product_quantity || ""
              }</span>
              <span class="text-muted small">${
                product.product_quantity_unit || "item"
              }</span>
            </div>

            <div class="mt-1 d-flex flex-column">
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


function addProduct(productIdToAdd, quantityInput, csrfToken, productCard=null) {
  const quantity = parseFloat(quantityInput); 
  if (isNaN(quantity) || quantity <= 0) {
    showToast("Invalid quantity. Please enter a number greater than 0.", false);
    return;
  }
  
  const addProductRequestData = {
    product_id: productIdToAdd,
    quantityToAdd: quantity,
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
        window.location.href = "/users/login";
        throw new Error("Redirecting to login page...");
      }
      return response.json();
    })
    .then((data) => {
     showToast(data.message, data.success);
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      if (error.message !== "Redirecting to login page...") {
        showToast("A network error occurred.", false);
      }
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
    .then((response) => {
      if (response.status === 401) {
          window.location.href = "/users/login/"; 
        }
      return response.json();
    })
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
  const emptyMessageContainer = favouriteSection.querySelector(".product-card-wrapper.text-center");

  if (is_favourited) {
    if (emptyMessageContainer) {
      emptyMessageContainer.remove();
    }
    
    const hasAllergenConflict = product.has_allergen_conflict;
    const hasDietaryMismatch = product.has_dietary_mismatch;
    const conflictingTags = product.conflicting_allergens || [];
    const missingTags = product.missing_dietary_tags || [];
    let safetyAlertsHtml = '';
    let cardClasses = "card h-100 border-0 shadow-sm"; 

    if (hasAllergenConflict) {
        const conflictingTagsList = conflictingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        cardClasses = "card h-100 shadow-lg border-danger border-3"; 
        safetyAlertsHtml += `
            <div class="alert alert-danger p-1 mb-2 small" role="alert">
            <strong><i class="bi bi-exclamation-circle"></i>  WARNING: </strong> Contains user-specified allergens: ${conflictingTagsList}
            </div>`;
    }
            
    if (hasDietaryMismatch) {
        const missingTagsList = missingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        safetyAlertsHtml += `
          <div class="alert alert-warning p-1 mb-2 small" role="alert">
          <strong><i class="bi bi-question-circle"></i>  POSSIBLE MISMATCH: </strong> Missing dietary requirements: ${missingTagsList}.
          </div>`;
    }

    const newFavouriteCard = document.createElement("div");
    newFavouriteCard.className = "product-card-wrapper";

    const productCard = document.createElement("div");
    productCard.classList.add("card", "h-100", "shadow-sm");

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

        <div>
         ${safetyAlertsHtml}
        </div>

        <div>
        <p class="card-text text-muted mb-1 small"><strong>Brands:</strong> ${
          product.brands || "N/A"
        }</p>
        <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${
          product.code || "N/A"
        }</p>
        </div>

        <div class="d-flex align-items-center mb-3">
          <input class="product-quantity-input form-control me-2" type="number" min="1.00" step="1.00" value="1">
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


function displaySuggestions(suggestions, autocompleteSuggestionsDiv, productNameInput) {
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


function showToast(message, isSuccess = true) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const toastBgClass = isSuccess ? 'bg-success' : 'bg-danger';
    const toastIcon = isSuccess 
        ? '<i class="bi bi-check-circle-fill me-2"></i>' 
        : '<i class="bi bi-exclamation-triangle-fill me-2"></i>';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${toastBgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${toastIcon}
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

 function startScanner() {
        
    if (!html5QrCode) {
       html5QrCode = new Html5Qrcode(readerId);
            
       document.getElementById("scanner-container").style.display = "flex";

       html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanFailure
        )
        .catch((err) => {
          console.error("Camera failed to start:", err);
          alert("Camera start failed.");
          document.getElementById("scanner-container").style.display = "none";
          html5QrCode = null;
        });
    }
  }