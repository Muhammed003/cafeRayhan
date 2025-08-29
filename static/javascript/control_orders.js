$(document).ready(function () {
    // Function to filter orders based on button click
    function filterOrders(filterType, filterValue) {

        // Hide all orders
        $('.order-controller').hide();

        // Show orders that match the filter criteria
        $('.order-controller').each(function () {
            var orderNumber = $(this).attr('id');

            switch (filterType) {
                case 'number_of_order':
                    if (orderNumber.includes(filterValue)) {
                        $(this).show();
                    }
                    break;
                case 'number_of_desk':
                    var numberOfDesk = $(this).find('.order-items #number_of_desk').text();
                    if (parseInt(numberOfDesk) === parseInt(filterValue)) {
                        $(this).show();
                    }
                    break;
                case 'username':
                    if ($(this).find('.order-items #username:contains(' + filterValue + ')').length) {
                        $(this).show();
                    }
                    break;
                // Add cases for other filter types if needed
            }
        });
    }

    // Attach event handlers to dynamically generated filter buttons
    $('.number_of_order_filter button, .number_of_desk_filter button, .username_filter button, .all_orders_filter button').on('click', function () {
        var filterType = $(this).data('filter');
        var filterValue = $(this).data('value');
        if (filterType === 'all') {
            // Show all orders
            $('.order-controller').show();
        } else {
            // Filter based on the selected criteria
            filterOrders(filterType, filterValue);
        }
    });
});
