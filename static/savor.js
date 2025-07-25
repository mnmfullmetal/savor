const { jsx } = require("react/jsx-runtime");

document.addEventListener('DOMContentLoaded', () => {

    const productSearchForm = document.querySelector('#search-form')

    productSearchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const barcode = productSearchForm.elements.barcode.value.trim();
        const productName = productSearchForm.elements.product_name.value.trim();
        const csrftoken = productSearchForm.elements.csrfmiddlewaretoken.value;

        searchProduct(barcode, productName, csrftoken);

    })

})


function searchProduct( barcode ='None', productName = 'None', csrftoken) {

    const productDetailsDiv = document.querySelector('#product_details')
    productDetailsDiv.innerHTML = '<p>Searching...</p>';
 

    if (!barcode && !productName) {
        alert("Please enter a barcode or product name to search.");
        productDetailsDiv.innerHTML = '';
        return;
    };

    const requestData = {
        barcode: barcode,
        product_name: productName
    };

    fetch("/product/search/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from Django API:", data);
        const isAuthenticated = data.is_authenticated;

        if (data.error || data.errors) {
            const errorMessage = data.error || JSON.parse(data.errors);
            console.error("Error from backend:", errorMessage);
            productDetailsDiv.innerHTML = `<p>Error: ${data.error || 'Invalid input.'}</p>`;

        } else if (data.products && data.products.length > 0) {
            productDetailsDiv.innerHTML = '';
            data.products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.innerHTML =
                    `<h3>${product.product_name || 'No Name'}</h3>
                     <p>Brands: ${product.brands || 'N/A'}</p>
                     <p>Code: ${product.code || 'N/A'}</p>
                     ${product.image_url ? `<img src="${product.image_url}" alt="${product.product_name || 'Product Image'}" style="max-width: 100px; height: auto;">` : ''}
                     <hr>
                     <span> <button id="favourite_button" class="btn btn-primary">Like</button> </span> <span> <button id="add_button"  class="btn btn-primary"> Add </button> </span>`;
                productDetailsDiv.appendChild(productDiv);
                addButton = document.querySelector("#add_button")
                addButton.addEventListener("click",() => {
                    
                    fetch(`/pantry/add_product`, {
                        method: "POST", // put? not get because not geeting information 
                        body: JSON.stringify(requestData)

                    })
                    .then(response => json.response)
                    .then({

                    })
                    // backend will handle user validation and saving to DB
                })
            });

        } else {
            productDetailsDiv.innerHTML = '<p>No products found.</p>';
        }
    })
    .catch(error => {
        console.error("Fetch network error:", error);
        productDetailsDiv.innerHTML = '<p>A network error occurred. Please check your connection.</p>';
    });
}