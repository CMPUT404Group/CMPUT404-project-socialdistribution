window.onload = function() {
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
        $("button#closeUploadImageModal").click();
        // clear upload image form
        $("form#uploadImageForm").trigger("reset");
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
    var Data = JSON.stringify({ "id": authorID ,"github_name": "http://github.com/"+formData});
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
        $("button#closeeditGithubModal").click();
        // clear editgithub form
        $("form#editGithubForm").trigger("reset");
        // change wuthor github
        $("#id-github").empty();
        $("#id-github").html("github: " + response.github_name);
        toastr.info("Github Updated!");
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
      }
    });
  });


  // prepare response to formulate friend request
  // only extract everything but the friendsList
  function parseProfileResponse(author_profile_obj) {
    delete author_profile_obj["friends"];
    return author_profile_obj;
  }

  function sendLocalFriendRequest(follower_id, followee_author_obj) {
    var followee_id = followee_author_obj["id"]

    // get follower_id object to formulate friend request
    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + follower_id,
      type: "GET",
      contentType: "application/json",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response, statusText, xhr) {
        if (xhr.status == 200) {
          var follower_author_obj = parseProfileResponse(response);
          var JSONobject = { "query": "friendrequest", "author":  follower_author_obj, "friend": followee_author_obj };
          var jsonData = JSON.stringify( JSONobject);
          console.log(jsonData);
          $.ajax({
            url: 'http://' + window.location.host + '/api/friendrequest/',
            type: "POST",
            data:  jsonData,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response2) {
              console.log(response2);
              toastr.info("Followed!");
              $("button#follow-btn-"+followee_id).text("Followed");
              $("button#follow-btn-"+followee_id).removeClass("follow-btn");
              $("button#follow-btn-"+followee_id).removeClass("btn-success");
              $("button#follow-btn-"+followee_id).addClass("btn-info");
            },
            error: function(xhr, ajaxOptions, error) {
              console.log(xhr.status);
              console.log(xhr.responseText);
              console.log(error);
              toastr.error("Error. Could not send request");
            }
          });
        }
        else {
          toastr.error("Author not found.");
        }
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
        toastr.error("Error. Could not send request");
      }
    });
  }

  function sendRemoteFriendRequest(follower_id, followee_author_obj, remote_host_url) {
    var followee_id = followee_author_obj["id"];
    var remote_url = remote_host_url;
    if (remote_host_url.slice(-1) != '/') {
      remote_url = remote_host_url = '/';
    }

    // get follower_id object to formulate friend request
    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + follower_id,
      type: "GET",
      contentType: "application/json",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
        // put authentication credentials to REMOTE SITES here - may be different for each group
      },
      success: function(response, statusText, xhr) {
        if (xhr.status == 200) {
          var follower_author_obj = parseProfileResponse(response);
          var JSONobject = { "query": "friendrequest", "author":  follower_author_obj, "friend": followee_author_obj };
          var jsonData = JSON.stringify( JSONobject);
          console.log(jsonData);
          $.ajax({
            url: remote_url + 'api/friendrequest/',
            type: "POST",
            data:  jsonData,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            beforeSend: function(xhr, settings) {
              // put authentication credentials to REMOTE SITES here - may be different for each group
              xhr.setRequestHeader("Authorization", "Basic " + btoa( follower_id + "@nodeHost4B:host4b"));
            },
            success: function(response2, statusText, xhr) {
              console.log(response2);
              if (xhr.status == 200 || xhr.status == 201) {
                toastr.info("Followed!");
                $("button#follow-btn-"+followee_id).text("Followed");
                $("button#follow-btn-"+followee_id).removeClass("follow-btn");
                $("button#follow-btn-"+followee_id).removeClass("btn-success");
                $("button#follow-btn-"+followee_id).addClass("btn-info");
                
                // // remote node friend request success - now record it in our db by hitting our api
                $.ajax({
                  url: "http://" + window.location.host + '/api/friendrequest/',
                  type: "POST",
                  data:  jsonData,
                  contentType: 'application/json; charset=utf-8',
                  dataType: 'json',
                  beforeSend: function(xhr, settings) {
                    // put authentication credentials   - OUR OWN CREDENTIALS TO OUR SITE
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    // xhr.setRequestHeader("Authorization", "Basic " + btoa( follower_id + "@:city"));
                  },
                  success: function(response3, statusText, xhr) {
                  },
                  error: function(xhr, ajaxOptions, error) {
                    console.log(xhr.status);
                    console.log(xhr.responseText);
                    console.log(error);
                    toastr.error("Error. Response from remote node is not 200 or 201 - Remote node friend request success but local node friend request unsuccessful"); 

                  }
                });
              }
              else {
                console.log(xhr.status);
                console.log(xhr.responseText);
                toastr.error("Error. Response from remote node is not 200 or 201"); 
              }
            },
            error: function(xhr, ajaxOptions, error) {
              console.log(xhr.status);
              console.log(xhr.responseText);
              console.log(error);
              toastr.error("Error. Could not send request");
            }
          });
        }
        else {
          toastr.error("Author not found.");
        }
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
        toastr.error("Error. Could not send request");
      }
    });
  }



  // click button to follow someone
  $("button.follow-btn").one("click", function(event) {
    var author_id = this.id.slice(11);
    var follower_id = document.getElementById('logged-in-author').getAttribute("data");

    // we assume that follower_id (loggedInAuthor sending the friend request) is an author on our node

    // check if followee (person being followed) is a local or remote author
    // var checkAuthorNodeRequest 
    // hit out api, if followee id has a profile page, check their host to see if remote or local
    // else if followee id doesn't have a profile page on our node, its a remote
    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + author_id,
      type: "GET",
      contentType: "application/json",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response, statusText, xhr) {
        // console.log(response);
        // console.log(statusText);
        // console.log(xhr.status)
        if (xhr.status == 200) {
          var host = response["host"];
          if (host == undefined) {
            toastr.error("Error. Unknown host.");
            return;
          }
          // console.log(host);
          var followee_author_obj = parseProfileResponse(response);
          if ((host == 'http://' + window.location.host) || (host == 'http://' + window.location.host + '/')) {
            // is a local author - send request to our api
            sendLocalFriendRequest(follower_id, followee_author_obj);    // parameters : source author id, destination author object
          }
          else {
            // is a remote author - send request to remote node's api
            sendRemoteFriendRequest(follower_id, followee_author_obj, host);   // parameters : source author id, destination author object, destination/remote host
          }
        }
      },
      error: function(xhr, ajaxOptions, error) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
        if (xhr.status == 404) {
          console.log("IN HERERLKE*U)*&");
          // var followee_author_obj = parseProfileResponse(response);
          // is a remote author - send request to remote node's api
          // sendRemoteFriendRequest(follower_id, followee_author_obj, host);   // parameters : source author id, destination author object, destination/remote host
        }

        toastr.error("Error. Could not send request");

      }
    })
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
          authorCallback(true, username);
        } else if (e.status === 404) {
          authorCallback(false, username);
        }
      }
    });
  }

  //respond correctly if it is an actual user or not
  function authorCallback(result,username){
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

// use bootstrap tooltip to display the small pop-up box
  $(document).ready(function(){
      $('[data-toggle="tooltip"]').tooltip(); 
  });
};