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

  const accordions = document.querySelectorAll(".accordion");

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

function save_recipe(recipeId, csrfToken) {
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
