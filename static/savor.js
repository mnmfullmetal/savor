document.addEventListener("DOMContentLoaded", () => {
  const productSearchForm = document.querySelector("#search-form");

  productSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const barcode = productSearchForm.elements.barcode.value.trim();
    const productName = productSearchForm.elements.product_name.value.trim();
    const csrftoken = productSearchForm.elements.csrfmiddlewaretoken.value;

    const currentPath = window.location.pathname;

    if (currentPath !== "index" && currentPath !== "/") {
      sessionStorage.setItem("searchBarcode", barcode);
      sessionStorage.setItem("searchProductName", productName);
      sessionStorage.setItem("searchCsrfToken", csrftoken);
      window.location.href = "/";
    } else {
      searchProduct(barcode, productName, csrftoken);
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
});

function searchProduct(barcode = "None", productName = "None", csrftoken) {
    const searchedProductsDiv = document.querySelector("#searched-product-section");
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
                "X-CSRFToken": csrftoken,
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
                    productColumnDiv.classList.add("col-12", "col-sm-6", "col-md-4", "col-lg-4", "mb-4");

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
                        <p class="card-text text-muted mb-3 small"><strong>Code:</strong> ${product.code || "N/A"}</p>

                        <div class="d-flex align-items-center mb-3">
                            <input class="product-quantity-input form-control me-2"
                                type="number" min="0.01" step="0.01" value="1" style="max-width: 80px;"> <!-- Added me-2 and max-width -->

                            <span class="text-secondary me-1">${ 
                                product.product_quantity || "?" 
                            } </span>
                            <span class="text-muted small">${ 
                                product.product_quantity_unit || "item"
                            }</span>

                            <button class="btn btn-primary btn-sm add-to-pantry-button" data-product-name="${ 
                                product.product_name
                            }" data-product-id="${product.id}"> Add to Pantry </button> <!-- Changed button text -->
                        </div>

                        <div class="mt-auto d-flex flex-column">
                            <button class="btn btn-outline-secondary btn-sm favourite-btn" data-product-id="${
                                product.id
                            }"> Favourite</button>
                        </div>
                    </div>`; 


                    productColumnDiv.appendChild(productCard);

                    searchedProductsDiv.appendChild(productColumnDiv);

                    const favouriteButton = productCard.querySelector(".favourite-btn");

                    favouriteButton.addEventListener("click", (event) => {
                        const clickedButton = event.target;
                        const productIdToFav = clickedButton.dataset.productId;

                        fetch(`/favourite_product/${productIdToFav}`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": csrftoken,
                            },
                        })
                        .then((response) => response.json())
                        .then((data) => {
                            clickedButton.textContent = data.is_favourited ? "Remove Favourite" : "Favourite";
                            clickedButton.classList.toggle('btn-outline-secondary');
                            clickedButton.classList.toggle('btn-outline-danger'); 
                        })
                        .catch((error) => console.error("Error toggling favourite:", error));
                    });

                    const addButton = productCard.querySelector(".add-to-pantry-button");

                    addButton.addEventListener("click", (event) => {
                        const clickedButton = event.target;
                        const productIdToAdd = clickedButton.dataset.productId;
                        const quantityInput = productCard.querySelector(".product-quantity-input").value; 

                        if (isNaN(quantityInput) || parseFloat(quantityInput) <= 0) {
                            const cardBody = productCard.querySelector(".card-body");
                            let messageElement = cardBody.querySelector(".alert");
                            if (!messageElement) {
                                messageElement = document.createElement("div");
                                cardBody.appendChild(messageElement);
                            }
                            messageElement.className = "alert alert-warning mt-2 py-1";
                            messageElement.textContent = "Please enter a valid quantity (> 0).";
                            setTimeout(() => { messageElement.remove(); }, 3000); 
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
                                "X-CSRFToken": csrftoken,
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
                            messageElement.className = `alert mt-2 py-1 ${data.success ? 'alert-success' : 'alert-danger'}`;
                            messageElement.innerHTML = `${data.message}`;
                            setTimeout(() => { messageElement.remove(); }, 3000); 
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
                            setTimeout(() => { messageElement.remove(); }, 3000); 
                        });
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
