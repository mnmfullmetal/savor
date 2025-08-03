document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".remove-button");

  if (buttons.length > 0) {
    for (const button of buttons) {
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const itemId = clickedButton.dataset.itemId;
        const csrfToken = clickedButton.dataset.csrfToken;
        const quantityToRemove = clickedButton
          .closest(".pantry-item")
          .querySelector(".remove-quantity-input").value;
        const itemCardDiv = clickedButton.closest(".pantry-item");
        const removeRequestData = {
          itemId: itemId,
          quantityToRemove: quantityToRemove,
          csrfToken: csrfToken,
          itemCardDiv: itemCardDiv,
        };

        removePantryItem(removeRequestData);
      });
    }
  }
});

function removePantryItem(removeRequestData) {
  const csrftoken = removeRequestData.csrfToken;
  const itemCardDiv = removeRequestData.itemCardDiv;

  fetch(`/pantry/remove_pantryitem`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(removeRequestData),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      const newQuantity =  data['quantity_left']
      const pantryQtyCount = itemCardDiv.querySelector('.pantry-quantity-count')
      pantryQtyCount.innerHTML = newQuantity

      if (newQuantity <= 0) {
        itemCardDiv.remove();
      }

    })
    .catch((error) => {
      console.error("Fetch network error:", error);
      alert(`error: ${error}`);
    });
}
