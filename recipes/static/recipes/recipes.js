document.addEventListener("DOMContentLoaded", () => {
  const saveButtons = document.querySelectorAll(".save-recipe-btn");
  const accordions = document.querySelectorAll(".accordion");
  const deleteButtons = document.querySelectorAll('.delete-btn');

  if(deleteButtons.length > 0){
    for (const button of deleteButtons){
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const recipeId = clickedButton.dataset.recipeId;
        const csrfToken = clickedButton.dataset.csrfToken;

        deleteRecipe(recipeId, csrfToken)
      })
    }
  }

  if (saveButtons.length > 0) {
    for (const button of saveButtons) {
      button.addEventListener("click", (event) => {
        const clickedButton = event.target;
        const recipeId = clickedButton.dataset.recipeId;
        const csrfToken = clickedButton.dataset.csrfToken;

        saveRecipe(recipeId, csrfToken);
      });
    }
  }

  if (accordions.length > 0) {
    accordions.forEach((accordion) => {
      accordion.addEventListener("shown.bs.collapse", function (event) {
        const collapseElement = event.target;
        const button =
          collapseElement.previousElementSibling.querySelector(
            ".accordion-button"
          );

        if (button.classList.contains("unseen-recipe")) {
          const recipeId = button.dataset.recipeId;
          const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
          ).value;

          fetch(`/recipes/mark_as_seen/${recipeId}/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              console.log("Success:", data);
              button.classList.remove("unseen-recipe");
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        }
      });
    });
  }
});


function deleteRecipe(recipeId, csrfToken){
  fetch(`/recipes/delete_recipe/${recipeId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    }
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message)
  })
  .catch(error =>  {

  })
}

function saveRecipe(recipeId, csrfToken) {
  fetch(`/recipes/save_recipe/${recipeId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((errorData) => {
          throw new Error(errorData.error);
        });
      }
      return response.json();
    })
    .then((data) => {
      alert(data.message);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert(error.message);
    });
}
