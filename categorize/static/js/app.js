$(document).ready(function() {
    $.getJSON('/categorize', function(data) {
        $.each(data, function(key, value) {
            var row = $('<tr>');
            row.append($('<td>').text(key));
            var categorySelect = $('<select class="form-control">');
            $.each(EXPENSE_CATEGORIES, function(_, category) {
                categorySelect.append($('<option>').text(category).prop('selected', category === value.category));
            });
            row.append($('<td>').append(categorySelect));
            row.append($('<td contenteditable="true" class="confidence-cell">').text(value.confidence));
            row.append($('<td><input type="checkbox" class="confirm-checkbox" ' + (value.confirm ? 'checked' : '') + '></td>'));
            row.append($('<td><button class="btn btn-sm btn-info see-more-btn"><i class="fas fa-info-circle"></i></button></td>'));
            row.append($('<td contenteditable="true">').text(value.explanation));
            $('#transaction-table tbody').append(row);
        });

        // Sort the table by conviction (high to low)
        var table = $('#transaction-table');
        table.find('tbody tr').sort(function(a, b) {
            return parseFloat($(b).find('td:eq(2)').text()) - parseFloat($(a).find('td:eq(2)').text());
        }).appendTo(table.find('tbody'));

        // Add click event listener to the update button
        $('#update-button').click(function() {
            var updatedData = {};
            $('#transaction-table tbody tr').each(function() {
                var businessName = $(this).find('td:eq(0)').text();
                var category = $(this).find('td:eq(1) select').val();
                var confidence = $(this).find('td:eq(2)').text();
                var confirmed = $(this).find('td:eq(3) input').is(':checked');
                var explanation = $(this).find('td:eq(5)').text();
                updatedData[businessName] = {
                    'category': category,
                    'confidence': confidence,
                    'explanation': explanation,
                    'confirm': confirmed
                };
            });
            $.ajax({
                type: 'POST',
                url: '/categorize',
                data: JSON.stringify(updatedData),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function(data) {
                    location.reload(); // Reload the page to reflect the updated data
                },
                error: function(xhr, status, error) {
                    alert('Error updating data: ' + error);
                }
            });
        });

        // Add click event listener to the "See More" buttons
        $('#transaction-table').on('click', '.see-more-btn', function() {
            var businessName = $(this).closest('tr').find('td:eq(0)').text();
            $.ajax({
                type: 'POST',
                url: '/get_details',
                data: JSON.stringify({ 'business_name': businessName }),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function(data) {
                    var modal = $('#detailsModal');
                    var table = $('#detailsTable tbody');
                    table.empty();
                    $.each(data, function(_, row) {
                        var tr = $('<tr>');
                        tr.append($('<td>').text(row['תאריך עסקה']));
                        tr.append($('<td>').text(row['שם בית עסק']));
                        tr.append($('<td>').text(row['סכום בש"ח']));
                        tr.append($('<td>').text(row['מועד חיוב']));
                        tr.append($('<td>').text(row['סוג עסקה']));
                        tr.append($('<td>').text(row['מזהה כרטיס בארנק דיגילטי']));
                        tr.append($('<td>').text(row['הנחה']));
                        tr.append($('<td>').text(row['הערות']));
                        table.append(tr);
                    });
                    modal.show();
                },
                error: function(xhr, status, error) {
                    alert('Error fetching details: ' + error);
                }
            });
        });

        // Add click event listener to the close button
        $('.close-button').click(function() {
            $('#detailsModal').hide();
        });
    });
});