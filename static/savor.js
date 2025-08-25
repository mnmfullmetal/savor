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
  const searchedProductsDiv = document.querySelector(
    "#searched-product-section"
  );
  searchedProductsDiv.innerHTML = "<p>Searching...</p>";

  if (!barcode && !productName) {
    alert("Please enter a barcode or product name to search.");
    searchedProductsDiv.innerHTML = "";
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
        searchedProductsDiv.innerHTML = `<p>Error: ${
          data.error || "Invalid input."
        }</p>`;
      } else if (data.products && data.products.length > 0) {
        searchedProductsDiv.innerHTML = "";
        data.products.forEach((product) => {
          const productDetailsDiv = document.createElement("div");
          productDetailsDiv.classList.add("card", "mb-3");
          productDetailsDiv.innerHTML = `<h3 class="mb-2">${
            product.product_name || "No Name"
          }</h3>
  ${
    product.image_url
      ? `<img src="${product.image_url}" alt="${
          product.product_name || "Product Image"
        }" class="img-fluid rounded mb-3" style="max-width: 100px; height: auto;">`
      : ""
  }

  <p class="text-muted mb-1"><strong>Brands:</strong> ${
    product.brands || "N/A"
  }</p>
  <p class="text-muted mb-3"><strong>Code:</strong> ${product.code || "N/A"}</p>

  <div class="d-flex align-items-center mb-3">
    <input class="product-quantity-input form-control w-auto"
           type="number" min="0.01" step="0.01" value="1">

    <span class="product-display-quantity ms-2">${
      product.product_quantity
    } </span>
    <span class="product-display-unit ms-1 me-2 text-muted">${
      product.product_quantity_unit || "item"
    }</span>

    <button class="btn btn-primary add-to-pantry-button" data-product-name="${
      product.product_name
    }" data-product-id="${product.id}"> Add </button>
  </div>

  <div class="mb-3">
    <button class="btn btn-outline-secondary favourite-btn"   data-product-id="${
      product.id
    }">Favourite</button>
  </div>`;

          searchedProductsDiv.appendChild(productDetailsDiv);

          const favouriteButton = productDetailsDiv.querySelector(".favourite-btn");

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
              .then((data) => data)
              .catch((error) => error);
          });

          const addButton = productDetailsDiv.querySelector(
            ".add-to-pantry-button"
          );

          addButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const productIdToAdd = clickedButton.dataset.productId;
            const quantityInput = productDetailsDiv.querySelector(
              ".product-quantity-input"
            ).value;
            if (isNaN(quantityInput) || quantityInput <= 0) {
              alert("Please enter a valid quantity (number greater than 0).");
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
                const message = document.createElement("div");
                message.className = "message";
                message.innerHTML = `${data.message}`;
                productDetailsDiv.append(message);
              })
              .catch((error) => {
                console.error("Fetch network error:", error);
              });
          });
        });
      } else {
        searchedProductsDiv.innerHTML = "<p>No products found.</p>";
      }
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      searchedProductsDiv.innerHTML =
        "<p>A network error occurred. Please check your connection.</p>";
    });
}
