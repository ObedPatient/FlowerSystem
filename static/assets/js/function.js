const monthsAbbr = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

$("#form-review").submit(function(e){
    e.preventDefault();

    let dt = new Date();
    let day = dt.getDate(); // Use getDate() to get the day of the month
    let month = monthsAbbr[dt.getMonth()]; // Use getMonth() to get the month (0-indexed)
    let year = dt.getFullYear();

    let time = day + " " + month + ", " + year;
    
    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",

        success: function(response){
            console.log("review saved !!!!");

            if (response.bool == true){
                $('#review-res').html("Review added Successfully.")
                $(".hide-form-review").hide()

            let _html = '<table class="table table-striped table-bordered" style="border: none;">'
                _html += '<tbody>';
                _html += '<tr>';
                _html += '<td style="width: 50%;"><img src="{% static \'assets/images/th.jpg\' %}" alt="" width="50px" height="50px">&nbsp;&nbsp;<strong>' + response.context.user + '</strong>';
                _html += '</td>';
                _html += '<td class="text-right">' + time + '</td>';
                _html += '</tr>';

                _html += '<tr>';
                _html += '<td colspan="2">';
                _html += '<p>' + response.context.review + '</p>';
                _html += '<div class="rating-box">';

                for(let i = 1; i <= response.context.rating; i++){
                    _html += '<i class="fas fa-star text-warning"></i>';
                }
                _html += '</div>';
                _html += '</td>';
                _html += '</tr>';
                _html += '</tbody>';
                _html += '</table>';

                $(".review-forms").prepend(_html);
            }
        }
    });
});



$(document).ready(function(){
    $(".filter-checkbox, #price-filter-btn").on("click", function(){
        console.log("Button has been clicked!!!");

        let filter_object = {};
        let min_price = parseFloat($("#max_price").attr("min"));
        let max_price = parseFloat($("#max_price").val()) || parseFloat($("#max_price").attr("max"));

        filter_object.min_price = min_price;
        filter_object.max_price = max_price; // Consistent naming

        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val();
            let filter_key = $(this).data("filter");
            console.log("filtervalue is :", filter_value)
            console.log("filtervalue is :", filter_key)

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function(element){
                return element.value;
            });
        });

        console.log("Filter Object is: ", filter_object);

        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function(){
                console.log("Trying to filter ....");
            },
            success: function(response){
                console.log(response);
                console.log("Filtered Successfully");
                $("#filterd-products").html(response.data);
            }
        });
    });

    $("#max_price").on("blur", function(){
        let min_price = parseFloat($(this).attr("min"));
        let max_price = parseFloat($(this).attr("max"));
        let current_price = parseFloat($(this).val());

        if(current_price < min_price || current_price > max_price){
            console.log("Price Error Occurred");

            alert("Price Must be Between " + min_price + " Rwf and " + max_price + " Rwf");
            $(this).val(min_price);
            $('#range').val(min_price);

            $(this).focus();
            return false;
        }
    });
});

$(document).ready(function() {
    // Add to cart button functionality
    $(".add-to-cart-btn").on("click", function() {
        let this_val = $(this);
        let index = this_val.attr("data-index");

        let quantity = $(".product-quantity-" + index).val();
        let product_title = $(".product-title-" + index).val();
        let product_slug = $(".product-slug-" + index).val();
        let product_id = $(".product-id-" + index).val();
        let product_price = $(".current-product-price-" + index).text(); // Ensure this element exists
        let product_pid = $(".product-pid-" + index).val();
        let product_image = $(".product-image-" + index).val();
        let product_currency = $(".current-product-currency-" +  index).text();

        console.log("quantity:", quantity);
        console.log("product title:", product_title);
        console.log("product slug:", product_slug);
        console.log("product price:", product_price);
        console.log("product Currency:", product_currency);
        console.log("product id:", product_id);
        console.log("product Image", product_image);
        console.log("product pid", product_pid);
        console.log("Index", index);

        $.ajax({
            url: '/add_to_cart',
            data: {
                'id': product_id,
                'pid': product_pid,
                'image': product_image,
                'qty': quantity,
                'title': product_title,
                'slug': product_slug,
                'price': product_price,
                'currency': product_currency,
                
            },
            dataType: 'json',
            beforeSend: function() {
                console.log("adding product to cart.......");
            },
            success: function(res) {
                this_val.html('✔️');
                console.log('product added to cart!!');
                console.log('Response:', res);
                $(".cart-items-count").text(res.totalcartitems);
            }
        });
    });

    // Use event delegation for delete button functionality
    $(document).on("click", ".delete-product", function(){
        let product_id = $(this).attr("data-product");
        let this_val = $(this);
    
        console.log("Product ID:", product_id);

        $.ajax({
            url:"/delete_from_cart",
            data: {
                "id": product_id
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems);
                $("#cart-list").html(response.data)
            }
        })
    });


    $(document).on("click", ".update-product", function(){
        let product_id = $(this).attr("data-product");
        let this_val = $(this);
        let product_quantity = $(".product-qty-"+ product_id).val()
    
        console.log("Product ID:", product_id);

        $.ajax({
            url:"/update_cart",
            data: {
                "id": product_id,
                "qty": product_quantity,
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems);
                $("#cart-list").html(response.data)
            }
        })
    });

    
    
    $(document).on("click", ".make-address-default", function(){
        let id = $(this).attr("data-address-id")
        let this_val = $(this)

        console.log("ID is: ", id)
        console.log("ELEMENT IS: ", this_val)

        $.ajax({
            url:"/make_address_default",
            data: {
                "id": id,
            },
            dataType: "json",
            success: function(response){
                console.log("Address Made Default...")
                if (response.boolean == true){
                    $(".check").hide()
                    $(".action_btn").show()

                    $(".check"+id).show()
                    $(".button"+id).hide()
                }
            }
        })
    })

    // Adding to wishlist

    $(document).on("click", ".add-to-wishlist", function(){
        let product_id = $(this).attr("data-product-item");
        let this_val = $(this);
        

        let product_price = $(".current-product-price-" + product_id).text();
        let product_currency = $(".current-product-currency-" + product_id).text();
    
        console.log("PRODUCT ID:", product_id);
        console.log("product price:", product_price);
        console.log("product Currency:", product_currency);
    
        $.ajax({
            url: "/add_to_wishlist/",
            data: {
                "id": product_id,
                'price': product_price,
                'currency': product_currency,
            },
            dataType: "json",
            beforeSend: function(){
                console.log("Adding to Wishlist...");
            },
            success: function(response){
                console.log(response); // Debugging the response
                if (response.bool === true ){
                    this_val.html('✔️');
                    $(".wishlist-items-count").text(response.wishlist_count);
                    console.log("Added to Wishlist...");
                }
            },
            error: function(xhr, status, error){
                console.error("Error adding to wishlist:", error);
            }
        });
    });
    

    // Remove Product from wishlist

    $(document).ready(function() {
        $(document).on("click", ".delete-wishlist-product", function() {
            let wishlist_id = $(this).attr("data-wishlist-product");
            let this_val = $(this);
    
            console.log("WISHLIST ID:", wishlist_id);
    
            $.ajax({
                url: "/remove_wishlist/",
                data: {
                    "id": wishlist_id,
                },
                dataType: "json",
                beforeSend: function(){
                    console.log("Deleting from wishlist...");
                },
                success: function(response){
                    $("#wishlist-list").html(response.data); // Update the wishlist items list
                    $(".wishlist-items-count").text(response.wishlist_count); // Update the wishlist count
                    console.log("Deleted from wishlist and count updated.");
                },
                error: function(xhr, status, error){
                    console.error("Error deleting from wishlist:", error);
                }
            });
        });
    });
    
    
    $(document).on("submit", "#contact-form-ajx", function(e){
        e.preventDefault()
        console.log("SUBMITTED..")

        let full_name = $("#full_name").val()
        let email = $("#email").val()
        let phone = $("#phone").val()
        let subject = $("#subject").val()
        let message = $("#message").val()

        console.log("Name:", full_name);
        console.log("email:", email);
        console.log("phone:", phone);
        console.log("subject:", subject);
        console.log("message:", message);


        $.ajax({
            url: "/ajax_contact",
            data: {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "subject": subject,
                "message": message,
            },
            dataType: "json",
            beforeSend: function(){
                console.log("Sending Data to server...");
            },
            success: function(){
                console.log("Sent...")
                $("#contact-form-ajx").hide()
                $('.contact-page-title').hide()
                $("#message-response").html("Message Sent Successfully ✔️")
            }
        })
    })

});




// add cart functionality

//$(".add-to-cart-btn").on("click", function(){
    //let = quantity = $("#product-quantity").val()
    //let product_title = $(".product-title").val()
    //let product_id = $(".product-id").val()
    //let this_val = $(this)

    //let product_price = $("#current-product-price").text()

    //console.log("quantity:", quantity)
    //console.log("product title:", product_title)
    //console.log("product price:", product_price)
    //console.log("product id:", product_id)
    //console.log("Current element:", this_val)

    //$.ajax({
       // url: '/add_to_cart',
        //data: {
            //'id': product_id,
            //'qty': quantity,
            //'title': product_title,
           // 'price': product_price, // Ensure this key matches what is used in the Django view
       // },
       // dataType: 'json',
        //beforeSend: function() {
            //console.log("adding product to cart.......");
       // },
        //success: function(res) {
           // this_val.html('Item Added to cart');
           // console.log('product added to cart!!');
           // console.log('Response:', res);
           // $(".cart-items-count").text(res.totalcartitems)
       // }
    //});
    
//})
