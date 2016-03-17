window.onload = function() {
  // alert("HELLO");
  /* -- SETTINGS -- */
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "500",
    "hideDuration": "1000",
    "timeOut": "650",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  };

  /* Taken from http://jsfiddle.net/raving/2thfaxeu/ Author: raving 02-17-2016 */
  var originalLeave = $.fn.popover.Constructor.prototype.leave;
  $.fn.popover.Constructor.prototype.leave = function(obj){
    var self = obj instanceof this.constructor ?
      obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data('bs.' + this.type)
    var container, timeout;

    originalLeave.call(this, obj);

    if(obj.currentTarget) {
      container = $(obj.currentTarget).siblings('.popover')
      timeout = self.timeout;
      container.one('mouseenter', function(){
        //We entered the actual popover – call off the dogs
        clearTimeout(timeout);
        //Let's monitor popover content instead
        container.one('mouseleave', function(){
          $.fn.popover.Constructor.prototype.leave.call(self, self);
        });
      })
    }
  };

  /* Taken from http://jsfiddle.net/raving/2thfaxeu/ Author: raving 02-17-2016 */
  $('body').popover({ selector: '[data-popover]', trigger: 'click hover', placement: 'auto', delay: {show: 50, hide: 400}});


  // Taken from https://docs.djangoproject.com/en/1.8/ref/csrf/#ajax 2016-03-04
  function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) == (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');


  /* -- Deletes posts -- */
  $("button.delete-post").click(function(event) {
    var that = this;
    var id = this.id.slice(12);
    $.ajax({
      url: 'http://' + window.location.host +'/api/posts/' + id + '/',
      type: "DELETE",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        console.log(response);
        $(that).parent().parent().remove();
        toastr.info("Post Deleted!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  /* -- Deletes posts from editing page -- */
  $("button.delete-post-single").click(function(event) {
    var that = this;
    var id = this.id.slice(12);
    $.ajax({
      url: 'http://' + window.location.host +'/api/posts/' + id + '/',
      type: "DELETE",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        console.log(response);
        toastr.info("Post Deleted!");
        window.location.replace("http://" + window.location.host);
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  /* -- Deletes comments -- */
  $("button.delete-comment").click(function(event) {
    var that = this;
    var comment_id = this.id.slice(15);
    var post_id = $(this).data("post-id");
    $.ajax({
      url: 'http://' + window.location.host +'/api/posts/' + post_id + '/comments/' + comment_id,
      type: "DELETE",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        console.log(response);
        var commentItem = $(that).parent().parent().parent();
        var commentHR = commentItem.next();
        commentHR.remove();
        commentItem.remove();
        toastr.info("Comment Deleted!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  /* -- Hide Upload Image Modal Initially -- */
  $("#uploadImageModal").hide();
  $("#uploadProfileImageModal").hide();
  
  $("#uploadImageForm").submit(function(event){
    event.preventDefault();
    var formData = new FormData($("#uploadImageForm")[0]);
    $.ajax({
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        console.log(response);
        // close modal
        $("button#closeChooseAuthorModal").click();
        // clear upload image form
        $("form#chooseAuthorForm").trigger("reset");
        // append "Image Attached" element
        $("#uploadImageTrigger").after('<span class="label label-primary imageAttachedIcon">Image Attached!</span>');
        // disable add image button in create post form
        $("#uploadImageTrigger").prop("disabled", true);
        // add image url to form's hidden image_url field (on create post form)
        $("input#id_image_url").val(response.photo);
        toastr.info("Image Uploaded!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  $("#uploadProfileImageForm").submit(function(event) {
    event.preventDefault();
    var formData = new FormData($("#uploadProfileImageForm")[0]);
    formData.append("github_name", "");
    formData.append("host", "");
    var authorID = $("#uploadProfileImageForm").data("author-id");
    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + authorID + '/',
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        // close modal
        $("button#closeUploadProfileImageModal").click();
        // clear upload image form
        $("form#uploadProfileImageForm").trigger("reset");
        // change user profile image
        $("img#id-user-profile-image").attr('src', response.picture);
        toastr.info("Profile Image Updated!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  $("#editGithubForm").submit(function(event) {
    event.preventDefault();
    var formData = document.getElementById('id_github').value;
    var authorID = $("#editGithubForm").data("author-id");
    var Data = JSON.stringify({"author":  { "id": authorID ,"github_name": "http://github.com/"+formData}});
    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + authorID + '/',
      type: "POST",
      data: Data,
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        // close modal
        $("button#closeeditGithubForm").click();
        // clear editgithub form
        $("form#editGithubForm").trigger("reset");
        // change wuthor github
        $("p#id-github").html("github: http://github.com/" + response.github_name);
        toastr.info("Github Updated!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

// click button to follow someone
  $("button.follow-btn").one("click", function(event) {
    var author_id = this.id.slice(11);
    var follower_id = document.getElementById('logged-in-author').getAttribute("data");
    var JSONobject = { "query": "friendrequest", "author":  { "id": follower_id }, "friend": { "id": author_id } };
    var jsonData = JSON.stringify( JSONobject);
    console.log(jsonData);
    $.ajax({
      url: 'http://' + window.location.host + '/api/friendrequest/',
      type: "POST",
      data:  jsonData,
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      beforeSend: function(xhr, response) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response) {
        console.log(response);
        toastr.info("Followed!");
        $("button#follow-btn-"+author_id).text("Followed");
        $("button#follow-btn-"+author_id).removeClass("follow-btn");
        $("button#follow-btn-"+author_id).removeClass("btn-success");
        $("button#follow-btn-"+author_id).addClass("btn-info");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });

  // on manager's page, click author's profile pic, shows author's firiends
  // $("img.")

  //hide the choose author modal
  $("#chooseAuthorModal").hide();

  //when other_author is selected, open a pop up box so they can choose which author
  //http://stackoverflow.com/questions/9744288/django-jquery-dialog-box-when-specific-radio-button-selected 2016/03/16
  $('#id_visibility_5').click(function(e){
    if(e.target.value ==='OTHERAUTHOR') {
      $("#chooseAuthorModal").modal('show');
    }
  });

  //after the author is typd in, check if it is an actual username
  $("#submitChooseAuthor").click(function(event){
    event.preventDefault();
    var username = $("#friend_username").val();
    if (username === "") {
      $("button#closeChooseAuthorModal").click();
    } else {
      checkUserName(username);
    }
  });

  //if nothing is entered. reset the radio button
  $(".reset_radio").click(function(e) {
      var username = $("#friend_username").val();
      if (username === "") {
        $('#id_visibility_5').prop('checked', false);
        $('#id_visibility_2').prop('checked', true);
        toastr.info("No Friend Added! Resetting Privacy settings.");
      }
  });

  //send an ajax request to see if that userpae exists
  function checkUserName(username){
    $.ajax({
      url: "/author/"+username+"/",
      complete: function(e,xhr,settings){
        if(e.status === 200) {
          callback(true, username);
        } else if (e.status === 404) {
          callback(false, username);
        }
      }
    });
  }

  //respond correctly if it is an actual user or not
  function callback(result,username){
    if (result) {
      $("#author_added").html("For Author: "+ username);
      $("input#other_author").val(username);
      toastr.info("Friend Added!");
      $("button#closeChooseAuthorModal").click();
      $("input#friend_username").val("");
    } else {
      alert("That is not a valid username. Try again");
    }
  }

};


// use bootstrap tooltip to display the small pop-up box
  $(document).ready(function(){
      $('[data-toggle="tooltip"]').tooltip(); 
  });



};

