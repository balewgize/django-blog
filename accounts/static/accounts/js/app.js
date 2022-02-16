$(document).ready(function () {
    // CSRF protection used by django for POST requests
    var csrf_token = $("input[name=csrfmiddlewaretoken]").val()

    // AJAX request to save/unsave posts
    $(".bookmark").off("click").on("click", function () {
        const $this = $(this); // clicked button
        const post_id = $this.val();

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

    // AJAX request to follow/unfollow users
    $(".follow").off("click").on("click", function () {
        const $this = $(this);
        const user_id = $this.val();
        console.log("TARGET USER ID", user_id);

        $.ajax({
            method: "POST",
            url: "/ac/follow/",
            data: {
                user_id: user_id,
                csrfmiddlewaretoken: csrf_token,
            },
            statusCode: {
                200: function (response) {
                    if (response["is_following"] == true) {
                        $this.html('Following');
                        $this.attr("class", "btn btn-sm btn-outline-primary follow");
                    } else {
                        $this.html('Follow');
                        $this.attr("class", "btn btn-sm btn-primary follow");
                    }
                },
                401: function (response) {
                    window.location.reload();
                }
            }
        })
    });

    // AJAX request to like/unlike posts
    $(".upvote").off("click").on("click", function () {
        const $this = $(this); // clicked button
        const post_id = $this.val();

        $.ajax({
            method: "POST",
            url: "/ac/like/",
            data: {
                post_id: post_id,
                csrfmiddlewaretoken: csrf_token,
            },
            statusCode: {
                200: function (response) {
                    const likes = response["likes_count"]
                    if (response["is_liked"] == true) {
                        $this.html('<span class="text-muted"><i class="fas fa-heart text-primary me-2"></i>' + likes + '</span>');
                    }
                },
                401: function (response) {
                    location.reload(); 
                }
            }
        })
    })
})