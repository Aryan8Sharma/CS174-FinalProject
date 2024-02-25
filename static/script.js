// script.js

document.addEventListener('DOMContentLoaded', function() {
    const body = document.querySelector('body');

    document.querySelector('body.home button').addEventListener('click', function() {
        // Toggle the clicked class to change the background image
        body.classList.toggle('clicked');
    });
});
