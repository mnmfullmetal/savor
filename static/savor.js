document.addEventListener('DOMContentLoaded', () => {

    const productSearchForm = document.querySelector('#search-form')

    if (productSearchForm){
        productSearchForm.onsubmit = searchProduct;
    }

})

function searchProduct(event, ){
    event.preventDefault();
    const barcode = document.querySelector("#barcode_input").value.trim();
    const productName = document.querySelector("#product_name_input").value.trim();
    const productDetailsDiv = document.querySelector('#product_details');
    productDetailsDiv.innerHTML = '<p>Searching...</p>'; 

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    if (!barcode && !productName) {
        alert("Please enter a barcode or product name to search.");
        productDetailsDiv.innerHTML = '';
        return;
    }

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
    .then(response => {
        if (!response.ok) {
            console.error(`HTTP error from Django backend! status: ${response.status}`);
            return response.json().catch(() => ({ error: 'Error parsing Django error response.' }));
        }
        return response.json();
    })
    .then(data => {
        console.log("Response from Django API:", data);

        if (data.error) {
            alert(`Error: ${data.error}`);
            productDetailsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else if (data.products && data.products.length > 0) {
            productDetailsDiv.innerHTML = '';

            data.products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.innerHTML = 
                   `<h3>${product.product_name || 'No Name'}</h3>
                    <p>Brands: ${product.brands || 'N/A'}</p>
                    <p>Code: ${product.code || 'N/A'}</p>`;
                productDetailsDiv.appendChild(productDiv);
            });
        } else {
            alert("No products found.");
            productDetailsDiv.innerHTML = '<p>No products found.</p>';
        }
    })
    .catch(error => {
        console.error("Fetch error to Django API:", error);
        alert("An unexpected error occurred. Please try again.");
        productDetailsDiv.innerHTML = '<p>An error occurred during the search.</p>';
    });



}