// script.js
$(document).ready(function() {
  $("#loanForm").submit(function(event) {
    event.preventDefault(); // Prevent form submission

    // Get form data
    var aadhaar = $("#aadhaar").val();
    var pan = $("#pan").val();
    var loanAmount = $("#loanAmount").val();
    var loanTerm = $("#loanTerm").val();
    var formData = {
      aadhaar: aadhaar,
      pan: pan,
      loanAmount: loanAmount,
      loanTerm: loanTerm
    };


    // AJAX call to backend API
    $.ajax({
      url: "/api/apply", // Example API endpoint
      type: "POST",
      data: JSON.stringify(formData), // Send data as JSON string
      contentType: "application/json", // Set content type
      success: function(response) {
        // Display EMI details
        var emi = response.emi;
        var loanTerm = response.loan_term;
        $("#emiDetails").html("EMI: " + emi + "<br>Loan Term: " + loanTerm + " months");

      },
      error: function(error) {
        // Handle errors
        console.error("Error:", error);
        $("#emiDetails").html("Error: " + error.responseJSON);

      }
    });
  });
});
