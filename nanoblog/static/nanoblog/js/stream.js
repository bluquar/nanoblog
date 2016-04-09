var mostRecentPostTime;
var refreshPeriodMS = 5000;

function setCommentListeners() {
	$("body").on("click", ".comment_form a", function(event) {
		var $form = $(this).parents("form");
		var $textField = $form.find("#id_text");
		var $errorField = $form.find(".comment_error");
		var comment_text = $textField[0].value;
		var csrf_token = $form.find('input[name="csrfmiddlewaretoken"]').val();
		var post_id = $form.find('input[name="postid"]').val();

		$textField.val("");
		$errorField.text("Posting...");
		$.ajax({
			url: "add_comment",
			type: "POST",
			dataType: "json",
			data: {
				'csrfmiddlewaretoken': csrf_token,
				'text': comment_text,
				'post': post_id
			},
			success: function (json) {
				if (json.success) {
					var $commentList = $form.parents(".postcard").find(".comment_list");
					var $comment = $(json.html);
					$comment.appendTo($commentList);
					$errorField.text("");
				} else {
					$errorField.html(json.errors);
					$textField.val(comment_text);
				}
			},
			error: function (xhr, status, err) {
				$errorField.text("Network or server error - please try again.");
				$textField.val(comment_text);
			}
		});
	});
}

function updatePosts() {
	setTimeout(updatePosts, refreshPeriodMS);
	var csrf_token = $('input[name="csrfmiddlewaretoken"]').first().val();
	// Get the "last_updated" attribute of the first (chronologically newest) post
	var last_updated = $('.postcard').first().attr("last_updated");
	if (last_updated === undefined) {
		// There are no posts yet. Use Python.datetime's minimum datetime value
		last_updated = '0001-01-01 00:00:00'
	}
	$.ajax({
		url: window.location.pathname,
		type: "GET",
		data: {
			'csrfmiddlewaretoken': csrf_token,
			'last_updated': last_updated
		},
		dataType: "html",
		success: function(html) {
			$(html).insertBefore($("#blogpost_list"));
		}
	});
}

$(function() {
	setCommentListeners();
	setTimeout(updatePosts, refreshPeriodMS);
});