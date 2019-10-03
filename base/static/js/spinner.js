$( document ).ready(function() {
    closeOverlaySpinner();
});

$( document ).on( 'keyup', function ( e ) {
    if ( e.key === 'Escape' ) { // ESC
        closeOverlaySpinner();
    }
});

window.addEventListener('beforeunload', function (e) {
      $("#loader").show();
      document.getElementById("overlay_fadein").style.display = "block";
});


function closeOverlaySpinner(){
    // $("#loader").hide();
    // document.getElementById("overlay").style.display = "none";
    setTimeout(function(){
        document.getElementById("overlay").style.display = "none";
    },700);
    document.getElementById("overlay_fadein").style.display = "none";
}