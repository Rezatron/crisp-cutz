document.addEventListener('DOMContentLoaded', function() {
    // Get the modal
    var modal = document.getElementById("account-details-modal");

    // Get the button that opens the modal
    var btn = document.getElementById("account-details-button");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal 
    if (btn) {
        btn.onclick = function () {
            console.log('Button clicked');
            modal.style.display = "block";
        }
    }

    // When the user clicks on <span> (x), close the modal
    if (span) {
        span.onclick = function () {
            console.log('Close button clicked');
            modal.style.display = "none";
        }
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            console.log('Clicked outside the modal');
            modal.style.display = "none";
        }
    }
});