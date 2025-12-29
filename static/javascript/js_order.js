import { speak } from './speechUtils.js';

let sound_order = JSON.parse(localStorage.getItem('sound_order')) || true; // Default to true if not set
localStorage.setItem('sound_order', JSON.stringify(sound_order));

const audio = new Audio(audioSrc); // Audio notification
audio.volume = 0.7;

let currentOrderCount = document.querySelectorAll(".order-controller").length; // Track initial order count

function fetchUpdatedOrders() {
    $.ajax({
        url: window.location.href, // Current URL for the AJAX request
        type: 'GET',
        success: function (data) {
            // Parse the updated HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, "text/html");

            // Extract updated order data
            const updatedOrders = doc.querySelector("#orders-here").innerHTML;
            const updatedQuantities = doc.querySelector("#meal-quantities")?.innerHTML;
            const count_meals_here = doc.querySelector("#count-meals-here")?.innerHTML;

            // Replace the content if it's different
            const ordersHere = document.querySelector("#orders-here");
            if (ordersHere.innerHTML !== updatedOrders) {
                ordersHere.innerHTML = updatedOrders;

                // Detect if a new order was added
                let updatedOrderCount = document.querySelectorAll(".order-controller").length;
                if (currentOrderCount < updatedOrderCount) {
                    // Play sound and announce the new order
                    playNewOrderNotification();
                    currentOrderCount = updatedOrderCount;
                }
            }

            // Replace meal quantities if available
            if (updatedQuantities) {
                document.querySelector("#meal-quantities").innerHTML = updatedQuantities;
            }
            if (count_meals_here) {
                document.querySelector("#count-meals-here").innerHTML = count_meals_here;
            }
        },
        error: function (error) {
            console.error("Error fetching updated orders:", error);
        }
    });
}

function playNewOrderNotification() {
    if (audio.paused) {
        audio.play();
        audio.onended = function () {
            if (sound_order) {
                const newOrder = document.querySelectorAll(".order-controller");
                const textarea = newOrder[newOrder.length - 1].querySelector("textarea");
                let orderText = "Новый заказ " + textarea.innerHTML.replace(/,/g, '');
                speak(orderText); // Announce the new order
            }
        };
    }
}

$(document).ready(function () {
    setInterval(fetchUpdatedOrders, 2000); // Fetch updates every 2 seconds
});
