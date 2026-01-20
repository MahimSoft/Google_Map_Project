function jumpToPage(pageObject) {
    const pageInput = document.getElementById('jump-page-input');
    const pageNumber = pageInput.value;
    const maxPages = pageObject;

    if (pageNumber && pageNumber > 0 && pageNumber <= maxPages) {
        // Get current URL and parameters
        const urlParams = new URLSearchParams(window.location.search);
        
        // Update the 'page' parameter
        urlParams.set('page', pageNumber);
        
        // Redirect to the new URL with all existing filters preserved
        window.location.search = urlParams.toString();
    } else {
        alert("Please enter a valid page number between 1 and " + maxPages);
    }
}

// Allow pressing "Enter" key to trigger the jump
function jumpToPageOnEnter(pageObject) {
document.getElementById('jump-page-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        jumpToPage(pageObject);
    }
});
}