$(document).ready(function () {
    // Define a function to handle the search input
    $("#search-input").on("keyup", function () {
      var searchText = $(this).val().toLowerCase();
  
      // Loop through each table row
      $("table tbody tr").each(function () {
        var rowData = $(this).text().toLowerCase();
        // Check if the row data contains the search text
        if (rowData.indexOf(searchText) === -1) {
          // Hide the row if it doesn't match the search
          $(this).hide();
        } else {
          // Show the row if it matches the search
          $(this).show();
        }
      });
    });
  });
  