document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".save-recipe-btn");

  if (buttons.length > 0) {
    for (const button of buttons) {
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const recipeId = clickedButton.dataset.recipeId;
        const csrfToken = clickedButton.dataset.csrfToken;

        save_recipe(recipeId, csrfToken);
      });
    }
  }
});

function save_recipe(recipeId, csrfToken) {
  fetch(`/recipes/save_recipe/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ recipeId: recipeId }),
  })
     .then(response => {
      if (!response.ok) {
        return response.json().then(errorData => {
          throw new Error(errorData.error); 
        });
      }
      return response.json();
    })
    .then(data => {
      alert(data.message);
    })
    .catch(error => {

        console.error("Error:", error);
      alert(error.message); 
    });
}
