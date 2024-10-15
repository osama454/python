// script.js
$(document).ready(function() {
  $("#loanForm").submit(function(event) {
    event.preventDefault(); // Prevent form submission

    // Get form data
    // ...

    // AJAX call to backend API
    $.ajax({
      url: "/api/apply", // Example API endpoint
      type: "POST",
      data: formData,
      success: function(response) {
        // Display EMI details
        // ...
      },
      error: function(error) {
        // Handle errors
        // ...
      }
    });
  });
});
