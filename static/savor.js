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
          productDiv.innerHTML = 
                    `<h3>${product.product_name || "No Name"}</h3>
                     <p>Brands: ${product.brands || "N/A"}</p>
                     <p>Code: ${product.code || "N/A"}</p>
                     ${product.image_url ? `<img src="${product.image_url}" alt="${product.product_name || "Product Image"}" style="max-width: 100px; height: auto;">`: ""}
                     <hr>
                    <div> 
                    <input class="product-quantity-input" type="number" min="0.01" step="0.01" value="${product.product_quantity || 1}" placeholder="Qty"> 
                    <span class="product-display-unit">${product.product_quantity_unit || 'item'}</span> <button  class="btn btn-primary add-to-pantry-button" data-product-id=${product.id} data-product-unit="${product.product_quantity_unit || 'item'}"> Add </button> 
                    </div>   
                    <div>
                    <button id="favourite_button" class="btn btn-primary">Favourite</button>
                    </div>`;

          productDetailsDiv.appendChild(productDiv);

          const addButton = productDiv.querySelector(".add-to-pantry-button");


          addButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const productIdToAdd = clickedButton.dataset.productId;
            const productUnitToAdd = clickedButton.dataset.productUnit;
            const quantityInput = productDiv.querySelector(".product-quantity-input");
            const quantity = parseFloat(quantityInput.value); 
            if (isNaN(quantity) || quantity <= 0) {
              alert("Please enter a valid quantity (number greater than 0).");
              return;
            }
            const addProductRequestData = {
              product_id: productIdToAdd,
              product_unit: productUnitToAdd,
              product_quantity: quantity,
            };

            fetch(`/pantry/add_product`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
              },
              body: JSON.stringify(addProductRequestData),
            })
              .then((response) => response.json())
              .catch((error) => {
                console.error("Fetch network error:", error);
                alert(`error: ${error}`);
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
