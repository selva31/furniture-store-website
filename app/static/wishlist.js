document.addEventListener('DOMContentLoaded', () => {
  const wishlistButtons = document.querySelectorAll('.heart-icon');

  wishlistButtons.forEach(button => {
      button.addEventListener('click', async (event) => {
          event.preventDefault();
          const form = button.closest('form');
          const action = form.action;
          const formData = new FormData(form);

          try {
              const response = await fetch(action, {
                  method: 'POST',
                  body: formData
              });

              if (response.ok) {
                  // Update the button state based on current status
                  const isInWishlist = button.textContent.trim() === '🤍';
                  button.textContent = isInWishlist ? '❤️' : '🤍';

                  // Optionally update the action URL for the form
                  form.action = isInWishlist
                      ? '/remove_from_wishlist'
                      : '/wishlist';
              } else {
                  alert('Failed to update wishlist. Please try again.');
              }
          } catch (error) {
              console.error('Error:', error);
              alert('An error occurred. Please try again.');
          }
      });
  });
});
// document.addEventListener('DOMContentLoaded', () => {
//   const wishlistButtons = document.querySelectorAll('.heart-icon');

//   wishlistButtons.forEach(button => {
//       button.addEventListener('click', async (event) => {
//           event.preventDefault();
//           const form = button.closest('form');
//           const action = form.action;
//           const formData = new FormData(form);

//           try {
//               const response = await fetch(action, {
//                   method: 'POST',
//                   body: formData
//               });

//               const data = await response.json();  // Parse the JSON response from the server

//               if (response.ok) {
//                   // Update the button state based on current status
//                   const isInWishlist = button.textContent.trim() === '🤍';
//                   button.textContent = isInWishlist ? '❤️' : '🤍';

//                   // Optionally update the action URL for the form
//                   form.action = isInWishlist
//                       ? '/remove_from_wishlist'
//                       : '/wishlist';

//                   // Display the flash message on the page
//                   displayFlashMessage(data.message, data.status);
//               } else {
//                   alert(data.message || 'Failed to update wishlist. Please try again.');
//               }
//           } catch (error) {
//               console.error('Error:', error);
//               alert('An error occurred. Please try again.');
//           }
//       });
//   });

//   // Function to display flash message
//   function displayFlashMessage(message, status) {
//       const flashMessageContainer = document.createElement('div');
//       flashMessageContainer.classList.add('flash-message', status); // Add custom styles based on status
//       flashMessageContainer.textContent = message;
//       document.body.prepend(flashMessageContainer);

//       // Remove the flash message after a delay (optional)
//       setTimeout(() => {
//           flashMessageContainer.remove();
//       }, 5000); // Adjust time as needed
//   }
// });
