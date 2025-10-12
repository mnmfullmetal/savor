
document.addEventListener("DOMContentLoaded", () => {

  const buttons = document.querySelectorAll(".remove-button");
  if (buttons.length > 0) {
    for (const button of buttons) {
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const itemId = clickedButton.dataset.itemId;
        const csrfToken = clickedButton.dataset.csrfToken;
        const quantityToRemove = clickedButton.closest(".pantry-item").querySelector(".remove-quantity-input").value;
        const itemCardDiv = clickedButton.closest(".pantry-item");
        const itemCardCol = clickedButton.closest(".col-12");

        const removeRequestData = {
          itemId: itemId,
          quantityToRemove: quantityToRemove,
          csrfToken: csrfToken,
          itemCardDiv: itemCardDiv,
          itemCardCol: itemCardCol,
        };
        removePantryItem(removeRequestData);
      });
    }
  }  


  const pantrySearchInput = document.getElementById('pantrySearchInput')
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const debouncedSearch = debounce(searchPantry, 200);
  if (pantrySearchInput){
    pantrySearchInput.addEventListener("input", (event) => {

      const query = (event.target.value ?? '').trim();
      debouncedSearch(csrfToken, query);

    })
  }


});


function searchPantry(csrfToken, query){
  fetch('/search_pantry/', {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({
      'query': query
    }),
  })
  .then(response => response.json())
  .then(data => {
    updatePantryList(data.found_items, csrfToken);

  })
  .catch(error => console.error('Error during pantry search:', error));
}


function updatePantryList(items, csrfToken){
  const pantryItemsPage = document.querySelector(".pantry-items-page")
  pantryItemsPage.innerHTML = "";
  if (items.length === 0){
    pantryItemsPage.innerHTML = `
  <div class="col-12 text-center py-5">
  <p class="text-muted">No items found matching your search.</p>
  </div>`;
  }

  items.forEach((item) => {

    const placeholderImageUrl = "/static/media/placeholder-img.jpeg";
    const imageUrl = item.image_url || placeholderImageUrl;
    const hasAllergenConflict = item.has_allergen_conflict;
    const hasDietaryMismatch = item.has_dietary_mismatch;
    const missingTags = item.missing_dietary_tags || [];
    const conflictingTags = item.conflicting_allergens || [];
    let safetyAlertsHtml = '';
    let cardClasses = "card h-100 border-0 shadow-sm pantry-item";

    const pantryItemWrapper = document.createElement('div');
    pantryItemWrapper.classList.add('col-12', 'col-sm-6', 'col-md-4', 'col-lg-4', 'mb-4', 'pantry-item-col');

    if (hasAllergenConflict) {
        const conflictingTagsList = conflictingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        cardClasses = "card h-100 shadow-lg border-danger border-3 pantry-item"; 
        safetyAlertsHtml += `
        <div class="alert alert-danger p-1 mb-2 small" role="alert">
        <strong><i class="bi bi-exclamation-circle"></i>  WARNING : </strong> Contains user-specified allergens: ${conflictingTagsList}
        </div>`;
      }
            
    if (hasDietaryMismatch) {
        const missingTagsList = missingTags.map(tag => `<code>${tag.replace(/_/g, ' ').toUpperCase()}</code>`).join(', ');
        safetyAlertsHtml += `
        <div class="alert alert-warning p-1 mb-2 small" role="alert">
        <strong> <i class="bi bi-question-circle"></i>  POSSIBLE MISMATCH : </strong> Missing dietary requirements: ${missingTagsList}.
        </div>`;
    }

    const pantryItemCard = document.createElement('div');
    pantryItemCard.classList.add(...cardClasses.split(' '));
    
    pantryItemCard.innerHTML =`
             <img src="${imageUrl}" 
             alt="${item.product_name || "Product Image"}" 
             class="card-img-top img-fluid rounded-top" 
             style="max-height: 150px; object-fit: cover;"
             onerror="this.onerror=null;this.src='${placeholderImageUrl}';">

             <div class="card-body d-flex flex-column justify-content-between">
            <h3 class="card-title h5 mb-2 text-dark">${
              item.product_name || "No Name"
            }</h3>
            
             ${safetyAlertsHtml} 

              <p class="card-text text-muted mb-1 small ">
              <strong>Quantity:</strong> <span class="pantry-quantity-count">${item.quantity}</span>
              </p>

              <p class="card-text text-muted mb-1 small ">
              <strong>Product Size:</strong> ${item.product_quantity ||""} ${item.product_quantity_unit || 'item'}
              </p>

              <div class="mt-auto d-flex align-items-center justify-content-left">
                <input class="remove-quantity-input form-control me-2" type="number" min="1.00" step="1.00" value="1" style="max-width: 80px;">
                <button class="btn btn-outline-danger btn-sm remove-button"
                  data-item-id=${ item.id }
                  data-csrf-token=${csrfToken}>
                  Remove
                </button>
              </div>

             <div class="message-container mt-2">
            </div>`;

    pantryItemWrapper.appendChild(pantryItemCard);
    pantryItemsPage.appendChild(pantryItemWrapper);

    const removeButton = pantryItemCard.querySelector('.remove-button');
    removeButton.addEventListener('click', (event) => {
    const clickedButton = event.target;
    const csrfToken = clickedButton.dataset.csrfToken;
    const quantityToRemove = clickedButton.closest(".pantry-item").querySelector(".remove-quantity-input").value;
    const itemCardDiv = clickedButton.closest(".pantry-item");
    const itemCardCol = clickedButton.closest(".col-12");

    const removeRequestData = {
          itemId: item.id,
          quantityToRemove: quantityToRemove,
          csrfToken: csrfToken,
          itemCardDiv: itemCardDiv,
          itemCardCol: itemCardCol,
    };

    removePantryItem(removeRequestData);

    })
  });
}


function removePantryItem(removeRequestData) {
  const csrftoken = removeRequestData.csrfToken;
  const itemCardDiv = removeRequestData.itemCardDiv;
  const itemCardCol =removeRequestData.itemCardCol;

  fetch(`/pantry/remove_pantryitem`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(removeRequestData),
  })
    .then(response => response.json())
    .then(data => {
      const newQuantity = data["quantity_left"];
      const pantryQtyCount = itemCardDiv.querySelector(
        ".pantry-quantity-count"
      );
      pantryQtyCount.innerHTML = newQuantity;

      if (newQuantity <= 0) {

        itemCardCol.classList.add('fade-out');
                
         setTimeout(() => {
              itemCardCol.remove();
          }, 400); 
      }
    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      alert(`error: ${error}`);
    });
}
