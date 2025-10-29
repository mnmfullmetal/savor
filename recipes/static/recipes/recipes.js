document.addEventListener("DOMContentLoaded", () => {

  //  event listeners for delete buttons
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

  // event listeners for save recipe buttons 
  const saveButtons = document.querySelectorAll(".save-recipe-btn");
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

  // event listeners for accordion elements
  const accordions = document.querySelectorAll(".accordion");
  if (accordions.length > 0) {
    accordions.forEach((accordion) => {
      accordion.addEventListener("shown.bs.collapse", function (event) {
        const collapseElement = event.target;
      
        // button is the header of the accordion item, which holds the recipe ID, so its found relative to the collapse element.
        const button =
          collapseElement.previousElementSibling.querySelector(
            ".accordion-button"
          );

        // handle visual feedback for unseen vs seen recipes 
        if (button.classList.contains("unseen-recipe")) {
          const recipeId = button.dataset.recipeId;
          const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

          fetch(`/recipes/mark_as_seen/${recipeId}/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          })
            .then((response) => response.json())
            .then((data) => {

              // if no error and recipe successfully marked as seen, remove unseen-recipe class
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
   // get closest ancestor with class 'accordion-item' and remove it ensuring entire recipe card is removed from the UI.
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
        // remove message that tells user they have no saved recipes.
        const emptyMessage = savedRecipesSection.nextElementSibling;
        if (emptyMessage && emptyMessage.classList.contains('alert-info')) {
          emptyMessage.remove();
        }
        // create the html for the new recipe and prepend it to the accordion ensuring the newest saved recipe appears at the top.
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
          <h5>${gettext('Ingredients')}</h5>
          <ul>
            ${recipe.ingredients.map(ingredient => 
            `<li>${ingredient.quantity} ${ingredient.unit} of ${ingredient.name}</li>`).join('')}
          </ul>
          <h5>${gettext('Instructions')}</h5>
            <ol>
            ${recipe.instructions.map(instruction => 
            `<li>${instruction}</li>` ).join('')}
            </ol>
            <button class="btn btn-outline-danger delete-btn" data-recipe-id="${recipe.id}" data-csrf-token="${csrfToken}">Delete Recipe</button>
        </div>
      </div>
    </div> `;

    //  event listener for newly created delete button.
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
