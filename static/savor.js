document.addEventListener("DOMContentLoaded", () => {

const sidebarToggle = document.getElementById('sidebarToggle');
sidebarToggle.addEventListener('click', () => {
const body = document.body;
const toggleIcon = sidebarToggle.querySelector('i');

    body.classList.toggle('sidebar-minimized');
    
    if (body.classList.contains('sidebar-minimized')) {
        toggleIcon.classList.remove('bi-box-arrow-in-left');
        toggleIcon.classList.add('bi-box-arrow-right');
    } else {
        toggleIcon.classList.remove('bi-box-arrow-right');
        toggleIcon.classList.add('bi-box-arrow-in-left');
    }
});

const accountDropdown = document.getElementById('account-dropdown-item')
if (accountDropdown){

  accountDropdown.addEventListener('show.bs.dropdown', function() {
    if (document.body.classList.contains('sidebar-minimized')) {
        document.body.classList.remove('sidebar-minimized');
        document.getElementById('sidebarToggle').querySelector('i').classList.add('bi-arrow-left-short');
        document.getElementById('sidebarToggle').querySelector('i').classList.remove('bi-arrow-right-short');
    }
});

};

  const productSearchForm = document.querySelector("#search-form");
  const  csrfToken = productSearchForm.elements.csrfmiddlewaretoken.value;

    document.getElementById('scan-button').addEventListener('click', () => {
        document.getElementById('scanner-container').style.display = 'block';
        document.getElementById('searched-product-section').innerHTML = ''; 
        startScanner(csrfToken);
    });

    document.getElementById('stop-scanner-btn').addEventListener('click', () => {
        Quagga.stop();
        document.getElementById('scanner-container').style.display = 'none';
    });

  productSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const barcode = productSearchForm.elements.barcode.value.trim();
    const productName = productSearchForm.elements.product_name.value.trim();
    const csrfToken = productSearchForm.elements.csrfmiddlewaretoken.value;

    const currentPath = window.location.pathname;

    if (currentPath !== "index" && currentPath !== "/") {
      sessionStorage.setItem("searchBarcode", barcode);
      sessionStorage.setItem("searchProductName", productName);
      sessionStorage.setItem("searchCsrfToken", csrfToken);
      window.location.href = "/";
    } else {
      searchProduct(barcode, productName, csrfToken);
    }
  });

  const savedBarcode = sessionStorage.getItem("searchBarcode");
  const savedProductName = sessionStorage.getItem("searchProductName");
  const savedCsrfToken = sessionStorage.getItem("searchCsrfToken");

  if (savedBarcode || savedProductName) {
    sessionStorage.removeItem("searchBarcode");
    sessionStorage.removeItem("searchProductName");
    sessionStorage.removeItem("searchCsrfToken");

    const barcodeInput =
      document.querySelector("#search-form").elements.barcode;
    const productNameInput =
      document.querySelector("#search-form").elements.product_name;

    if (barcodeInput) barcodeInput.value = savedBarcode;
    if (productNameInput) productNameInput.value = savedProductName;

    searchProduct(savedBarcode, savedProductName, savedCsrfToken);
  }

  const initialFavoriteButtons = document.querySelectorAll(".favourite-btn");
  const initialAddButtons = document.querySelectorAll(".add-to-pantry-button");

  initialFavoriteButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      const clickedButton = event.target;
      const productIdToFav = clickedButton.dataset.productId;
      favouriteProduct(productIdToFav,  csrfToken, clickedButton);
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
      addProduct(productIdToAdd, quantityInput,  csrfToken, productCard);
    });
  });


   
});

function searchProduct(barcode = "None", productName = "None", csrfToken) {
  const searchedProductsDiv = document.querySelector(
    "#searched-product-section"
  );
  searchedProductsDiv.innerHTML = "<p>Searching...</p>";

  if (!barcode && !productName) {
    searchedProductsDiv.innerHTML = `<div class="alert alert-warning text-center mt-3" role="alert">
 Please enter a barcode or product name to search.
 </div>`;
    return;
  }

  const requestData = {
    barcode: barcode,
    product_name: productName,
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
        searchedProductsDiv.innerHTML = `<div class="alert alert-danger text-center mt-3" role="alert">
 Error: ${data.error || "Invalid input."}
 </div>`;
      } else if (data.products && data.products.length > 0) {
        searchedProductsDiv.innerHTML = "";
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
          productCard.classList.add("card", "h-100", "shadow-sm");
          productCard.innerHTML = `<h3 class="card-title mb-2 h5">${
            product.product_name || "No Name"
          }</h3>
                    ${
                      product.image_url
                        ? `<img src="${product.image_url}" alt="${
                            product.product_name || "Product Image"
                          }" class="card-img-top img-fluid rounded-top mb-3" style="max-height: 150px; object-fit: cover;">`
                        : ""
                    }

                    <div class="card-body d-flex flex-column justify-content-between">
                        <p class="card-text text-muted mb-1 small"><strong>Brands:</strong> ${
                          product.brands || "N/A"
                        }</p>
                        <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${
                          product.code || "N/A"
                        }</p>

                        <div class="d-flex align-items-center mb-3">
                            <input class="product-quantity-input form-control me-2"
                                type="number" min="0.01" step="0.01" value="1" style="max-width: 80px;"> 

                            <span class="text-secondary me-1">${
                              product.product_quantity || "?"
                            } </span>
                            <span class="text-muted small">${
                              product.product_quantity_unit || "item"
                            }</span>

                            <button class="btn btn-primary btn-sm add-to-pantry-button" data-product-name="${
                              product.product_name
                            }" data-product-id="${
            product.id
          }"> Add to Pantry </button> 
                        </div>

                       <div class="mt-auto d-flex flex-column">
                        <button class="btn btn-sm favourite-btn ${
                          product.is_favourited
                            ? "btn-outline-danger"
                            : "btn-outline-secondary"
                        }" data-product-id="${product.id}">
                         ${
                           product.is_favourited
                             ? "Remove Favourite"
                             : "Favourite"
                         }
                          </button>
                          </div>
                    </div>`;

          productColumnDiv.appendChild(productCard);
          searchedProductsDiv.appendChild(productColumnDiv);

          const favouriteButton = productCard.querySelector(".favourite-btn");
          favouriteButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const productIdToFav = clickedButton.dataset.productId;
            favouriteProduct(productIdToFav, csrfToken, clickedButton);
          });

          const addButton = productCard.querySelector(".add-to-pantry-button");
          addButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const productIdToAdd = clickedButton.dataset.productId;
            const quantityInput = productCard.querySelector(
              ".product-quantity-input"
            ).value;
            addProduct(productIdToAdd, quantityInput, csrfToken, productCard);
          });
        });
      } else {
        searchedProductsDiv.innerHTML = `<div class="alert alert-info text-center mt-3" role="alert">
                                                    No products found. Try a different search term.
                                                </div>`;
      }
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      searchedProductsDiv.innerHTML = `<div class="alert alert-danger text-center mt-3" role="alert">
                                                A network error occurred. Please check your connection.
                                            </div>`;
    });
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
      clickedButton.classList.toggle("btn-outline-secondary");
      clickedButton.classList.toggle("btn-outline-danger");

      if (data.is_favourited) {
        updateFavouriteSection(data.product, true, csrfToken);
      } else {
        updateFavouriteSection(data.product, false, csrfToken);
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
          <button class="btn btn-primary btn-sm mb-2 add-to-pantry-button" 
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

    const addButton = newFavouriteCard.querySelector(".add-to-pantry-button");
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
    cardToRemove.remove();
  }
}


function startScanner(csrfToken) {
        Quagga.init({
            inputStream : {
                name : "Live",
                type : "LiveStream",
                target: document.querySelector('#interactive'),
                constraints: {
                   width: { min: 640 },
                   height: { min: 480 },
                    facingMode: "environment" 
                }
            },
            decoder: {
                readers: ["ean_reader", "upc_reader", "upc_e_reader", "ean_8_reader", "code_39_reader"]
            }
        }, function(err) {
            if (err) {
                console.error(err);
                return;
            }
            console.log("Initialization finished. Ready to start");
            Quagga.start();
        });

        Quagga.onDetected(function(result) {
            const barcode = result.codeResult.code;
            console.log("Barcode detected:", barcode);
            Quagga.stop();
            document.getElementById('scanner-container').style.display = 'none';
            
            searchProduct(barcode, "", csrfToken);
        });
    }
