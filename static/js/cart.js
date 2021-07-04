$(document).ready(function() {
    $('.update-cart').click(function() {
        var productId = $(this).attr('data-product');
        var action = $(this).attr('data-action');

        if (user == 'AnonymousUser'){
            addCookieItem(productId, action)       
        }else{
            updateUserOrder(productId, action)
        }
    })
})

function updateUserOrder(productId, action){

        $.ajax({
            url: '/update_item/',
            method:'POST',
            data: {
                'productId':productId,
                'action':action,
                'csrfmiddlewaretoken': csrftoken,
            },
            success: function(data) {
                location.reload();
            },
            error: function(data) {
            }
        })

}

function addCookieItem(productId, action) {
    console.log("User not authenticated")
    console.log(productId)
    console.log(action)

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity':1}
        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Item should be deleted')
            delete cart[productId];
        }
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload();
}
