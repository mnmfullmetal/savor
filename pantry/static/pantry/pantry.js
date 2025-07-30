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

        const removeRequestData = {
          itemId: itemId,
          quantityToRemove: quantityToRemove,
          csrfToken: csrfToken, 
        };

        removePantryItem(removeRequestData);
      });
    }
  }
});

function removePantryItem(removeRequestData) {
  const csrftoken = removeRequestData.csrfToken;
  fetch(`/pantry/remove_pantryitem`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(removeRequestData),
  }).then((response) => response.json());
}
