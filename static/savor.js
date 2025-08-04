document.addEventListener("DOMContentLoaded", () => {
  const productSearchForm = document.querySelector("#search-form");

  productSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const barcode = productSearchForm.elements.barcode.value.trim();
    const productName = productSearchForm.elements.product_name.value.trim();
    const csrftoken = productSearchForm.elements.csrfmiddlewaretoken.value;

    

    searchProduct(barcode, productName, csrftoken);
  });
});

function searchProduct(barcode = "None", productName = "None", csrftoken) {
  const productDetailsDiv = document.querySelector("#product_details");
  productDetailsDiv.innerHTML = "<p>Searching...</p>";

  if (!barcode && !productName) {
    alert("Please enter a barcode or product name to search.");
    productDetailsDiv.innerHTML = "";
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
        productDetailsDiv.innerHTML = `<p>Error: ${
          data.error || "Invalid input."
        }</p>`;
      } else if (data.products && data.products.length > 0) {
        productDetailsDiv.innerHTML = "";
        data.products.forEach((product) => {
          const productDiv = document.createElement("div");
          productDiv.classList.add("card", "mb-3");
          productDiv.innerHTML = `<h3 class="mb-2">${
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
    <button id="favourite_button" class="btn btn-outline-secondary">Favourite</button>
  </div>`;

          productDetailsDiv.appendChild(productDiv);

          const addButton = productDiv.querySelector(".add-to-pantry-button");

          addButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const productIdToAdd = clickedButton.dataset.productId;
            const quantityInput = productDiv.querySelector(
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
              .catch((error) => {
                console.error("Fetch network error:", error);
              });
          });
        });
      } else {
        productDetailsDiv.innerHTML = "<p>No products found.</p>";
      }
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      productDetailsDiv.innerHTML =
        "<p>A network error occurred. Please check your connection.</p>";
    });
}
