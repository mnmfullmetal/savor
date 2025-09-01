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

        deleteRecipe(recipeId, csrfToken, clickedButton)
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


function deleteRecipe(recipeId, csrfToken, clickedButton){
  fetch(`/recipes/delete_recipe/${recipeId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    }
  })
  .then(response => response.json())
  .then(data => {
   const recipeToDelete = clickedButton.closest('.accordion-item')
   recipeToDelete.remove();
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
        if (data.new_recipe) {
            const savedRecipesSection = document.getElementById('saved-recipes-accordion');
            if (savedRecipesSection) {
                const emptyMessage = savedRecipesSection.nextElementSibling;
                if (emptyMessage && emptyMessage.classList.contains('alert-info')) {
                    emptyMessage.remove();
                }

                const newRecipeHtml = createSavedRecipeHtml(data.new_recipe, csrfToken);
                savedRecipesSection.prepend(newRecipeHtml); 
            }
        }
    })
    .catch((error) => {
        console.error("Error:", error);
        alert(error.message);
    });
}



function createSavedRecipeHtml(recipe, csrfToken) {
    const accordionItem = document.createElement('div');
    accordionItem.className = 'card recipe-card mb-3';
    accordionItem.innerHTML = `
        <div class="accordion-item">
            <h4 class="accordion-header" id="headingSaved${recipe.id}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSaved${recipe.id}" aria-expanded="false" aria-controls="collapseSaved${recipe.id}">
                    ${recipe.title}
                </button>
            </h4>
            <div id="collapseSaved${recipe.id}" class="accordion-collapse collapse" aria-labelledby="headingSaved${recipe.id}" data-bs-parent="#saved-recipes-accordion">
                <div class="accordion-body">
                    <h5>Ingredients</h5>
                    <ul>
                        ${recipe.ingredients.map(ingredient => 
                            `<li>${ingredient.quantity} ${ingredient.unit} of ${ingredient.name}</li>`
                        ).join('')}
                    </ul>
                    <h5>Instructions</h5>
                    <ol>
                        ${recipe.instructions.map(instruction => 
                            `<li>${instruction}</li>`
                        ).join('')}
                    </ol>
                    <button class="btn btn-outline-danger delete-btn" data-recipe-id="${recipe.id}" data-csrf-token="${csrfToken}">Delete Recipe</button>
                </div>
            </div>
        </div>
    `;

    const deleteButton = accordionItem.querySelector('.delete-btn');
    if (deleteButton) {
        deleteButton.addEventListener("click", (event) => {
            const clickedButton = event.target;
            const recipeId = clickedButton.dataset.recipeId;
            const csrfTokenFromBtn = clickedButton.dataset.csrfToken;
            deleteRecipe(recipeId, csrfTokenFromBtn, clickedButton);
        });
    }

    return accordionItem;
}



