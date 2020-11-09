function toggleButton() {
    let filterBtnText = $("#filter-button").text();
    if (filterBtnText !== "Disable Filter") {
        $("#filter-button").html("Disable Filter");
    } else {
        $("#filter-button").html("Filter Trails Just for You");
        // Disable filter
    }
}
$(function () {
    $("[data-toggle=popover]").popover({
        html: true,
        sanitize: false,
        container: "#filter-div",
        title: function() {
            return $("#popover-title").html();
            },
        content: function() {
            return $("#popover-content").html();
        }
    });
});
function filterSelected() {
    // filter list with selected difficulty
    // let val = document.getElementById("filter-slider").value;
    var val = document.getElementById('filter-slider-in').innerHTML;
    alert(val);
}