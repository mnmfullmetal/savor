document.addEventListener("DOMContentLoaded", () => {

  const categorySelect = document.getElementById('categorySelect');
  const brandSelect = document.getElementById('brandSelect');
  const countrySelect = document.getElementById('countrySelect');
  fetchAndPopulateDropdowns(categorySelect, brandSelect, countrySelect );

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



});

function advProductSearch(){

}


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
