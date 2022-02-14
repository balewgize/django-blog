$(document).ready(function () {
    // CSRF protection used by django for POST requests
    var csrf_token = $("input[name=csrfmiddlewaretoken]").val()

    $(".bookmark").off("click").on("click", function () {
        let $this = $(this); // clicked button
        let post_id = $this.val();
        console.log("POST_ID", post_id)

        $.ajax({
            method: "POST",
            url: "/ac/bookmark/",
            data: {
                post_id: post_id,
                csrfmiddlewaretoken: csrf_token,
            },
            statusCode: {
                200: function (response) {
                    clicked_btn = $("button[value='" + response["post_id"] + "']")
                    if (response["is_bookmarked"] == true) {
                        $this.html('<i class="fas fa-bookmark"></i>');
                    } else {
                        $this.html('<i class="far fa-bookmark"></i>');
                    }
                },
                401: function (response) {
                    window.location.reload();
                }
            }
        })
    })
})