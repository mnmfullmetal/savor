document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".remove-button");

  if (buttons.length > 0) {

    for (const button of buttons) {
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const productId = clickedButton.dataset.productId;
        const quantityToRemove = clickedButton
          .closest(".pantry-item")
          .querySelector(".remove-quantity-input").value;

        const removeRequestData = {
          productId: productId,
          quantityToRemove: quantityToRemove,
        };

        removeProduct(removeRequestData);
      });
    };

  };

});

function removeProduct(removeRequestData) {
  fetch(`/pantry/remove_pantryitem`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(removeRequestData)
  })
  .then(response => response.json())
  
}
