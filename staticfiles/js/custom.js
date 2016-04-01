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
      url: 'http://' + window.location.host + '/api/images/',
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
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
        console.log(response.photo);
        $("input#id_image").val("http://" + window.location.host + response.photo);
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
    var Data = JSON.stringify({ "id": authorID ,"github": "http://github.com/"+formData});
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
        $("#id-github").html("github: " + response.github);
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


  // for unfollow we only consider locally
  function sendLocalUnFriendRequest(unfollower_id, unfollowee_obj){
    var unfollowee_id = unfollowee_obj["id"]

    $.ajax({
      url: '/api/author/' + unfollower_id + '/',
      type: "GET",
      contentType: "application/json",
      beforeSend: function(xhr, settings){
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response, statusText, xhr){
        console.log(xhr.status);
        if (xhr.status == 200) {
          var unfollower_author_obj = parseProfileResponse(response);
          var JSONobject = { "query": "friendrequest", "author": unfollower_author_obj, "friend": unfollowee_obj};
          var jsonData = JSON.stringify(JSONobject);
          console.log(jsonData);
          $.ajax({
            url: 'http://' + window.location.host + '/api/friendrequest/' + unfollowee_obj["id"],
            type: "DELETE",
            data: jsonData,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            beforeSend: function(xhr, settings){
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response2) {
              console.log(response2);
              toastr.info("Unfollowed!");
              $("button#unfollow-btn-"+unfollowee_id).text("Unfollowed");
              $("button#unfollow-btn-"+unfollowee_id).removeClass("unfollow-btn");
              $("button#unfollow-btn-"+unfollowee_id).removeClass("btn-warning");
              $("button#unfollow-btn-"+unfollowee_id).addClass("btn-info");
            },
            error: function(xhr, ajaxOptions, error) {
              console.log(xhr.status);
              console.log(xhr.responseText);
              console.log(error);
              toastr.error("Error. Could not send unfollow request");
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

  // button about unfollow someone
  $("button.unfollow-btn").one("click", function(event){
    var author_id = this.id.slice(13);
    var unfollower_id = document.getElementById('logged-in-author').getAttribute("data");
    console.log(author_id)
    console.log(unfollower_id)

    $.ajax({
      url: 'http://' + window.location.host + '/api/author/' + author_id,
      type: "GET",
      contentType: "application/json",
      beforeSend: function(xhr, settings){
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response, statusText, xhr) {
        if (xhr.status == 200) {
          var host = response["host"];
          if (host == undefined) {
            toastr.error("Error. Unknown host.");
            return;
          }
          var unfollowee_obj = parseProfileResponse(response);
          if ((host == 'http://' + window.location.host) || (host == 'http://' + window.location.host + '/')){
            sendLocalUnFriendRequest(unfollower_id, unfollowee_obj);
          }
        }
      },
      error: function(xhr, ajaxOptions, error){
        console.log(xhr.status);
        console.log(xhr.responseText);
        console.log(error);
        toastr.error("Error. Cound not send unfollow request");
      }
    })
  });


  function sendRemoteFriendRequest(follower_author_obj, followee_author_obj, remote_host_url) {
    var followee_id = followee_author_obj["id"];
    var remote_url = remote_host_url;
    if ((remote_host_url.startsWith("http://") == false) && (remote_host_url.startsWith("https://") == false)) {
      remote_url = "http://" + remote_host_url
    }
    if (remote_url.slice(-1) != '/') {
      remote_url = remote_url + '/';
    }

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
        if (remote_url == "http://project-c404.rhcloud.com/") {
          xhr.setRequestHeader("Authorization", "Basic " + btoa("team4:team4team4"));
        }
        else if (remote_url == "https://mighty-cliffs-82717.herokuapp.com/") {
          xhr.setRequestHeader("Authorization", "Basic " + btoa("Team4:team4"));
        }
        // put else if other remote site credentials here
      },
      success: function(response, statusText, xhr) {
        console.log(response);
        if (xhr.status == 200 || xhr.status == 201) {
          sendLocalFriendRequest(follower_author_obj, followee_author_obj);
          toastr.info("Followed!");
          $("button#remote-follow-btn-"+followee_id).text("Followed");
          $("button#remote-follow-btn-"+followee_id).removeClass("follow-btn");
          $("button#remote-follow-btn-"+followee_id).removeClass("btn-success");
          $("button#remote-follow-btn-"+followee_id).addClass("btn-info");
        }
      },
      error: function(xhr, ajaxOptions, error) {
        toastr.error("Remote Node Error :  " + xhr.status);
        console.log(xhr.status);
        console.log(xhr.responseText);
      }
    });
  };

  // click button to follow someone
  $("button.remote-follow-btn").one("click", function(event) {
    // remote-follow-btn-{{post.author.id}}
    var author_id = this.id.slice(18);
    var displayName = $(this).data('displayname');
    var remoteHost = $(this).data('host');
    var follower_id = document.getElementById('logged-in-author').getAttribute("data");
    var follower_displayName = $('#logged-in-author').data("displayname");

    let authorProfile = { 'id' : author_id, 'host': remoteHost, 'displayName': displayName };
    let followerProfile = { 'id' : follower_id, 'host': 'http://' + window.location.host + '/', 'displayName': follower_displayName, "url": "http://"+window.location.host+'/author/'+follower_id };
    console.log("FOLLOWEE PROFILE : ");
    console.log(authorProfile);
    console.log("FOLLOWER PROFILE : ");
    console.log(followerProfile);

    // HARD CODED
    if (remoteHost == "project-c404.rhcloud.com/api") {
      remoteHost = "http://project-c404.rhcloud.com/";
    }

    sendRemoteFriendRequest(followerProfile, authorProfile, remoteHost);
  });




  // click button to follow someone
  $("button.follow-btn").one("click", function(event) {
    // follow-btn-{{post.author.id}}
    var author_id = this.id.slice(11);
    var author_displayName = $(this).data('displayName');
    var author_host = $(this).data('host');

    var follower_id = document.getElementById('logged-in-author').getAttribute("data");
    var follower_displayName = $('#logged-in-author').data("displayName");

    let authorProfile = { 'id' : author_id, 'host': author_host, 'displayName': author_displayName };
    let followerProfile = { 'id' : follower_id, 'host': 'http://' + window.location.host + '/', 'displayName': follower_displayName };

    sendLocalFriendRequest(followerProfile, authorProfile);
  });

  function sendLocalFriendRequest(follower_author_obj, followee_author_obj) {
    var JSONobject = { "query": "friendrequest", "author":  follower_author_obj, "friend": followee_author_obj };
    var jsonData = JSON.stringify( JSONobject);
    console.log(jsonData);
    var followee_id = followee_author_obj['id'];
    $.ajax({
      url: 'http://' + window.location.host + '/api/friendrequest/',
      type: "POST",
      data:  jsonData,
      contentType: "application/json",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      success: function(response, statusText, xhr) {
        console.log(response);
        if (xhr.status == 200 || xhr.status == 201) {
          toastr.info("Followed!");
          $("button#follow-btn-"+followee_id).text("Followed");
          $("button#follow-btn-"+followee_id).removeClass("follow-btn");
          $("button#follow-btn-"+followee_id).removeClass("btn-success");
          $("button#follow-btn-"+followee_id).addClass("btn-info");
        }
      },
      error: function(xhr, ajaxOptions, error) {
        toastr.error("Local Error. Response is not 200 or 201");
        console.log(xhr.status);
        console.log(xhr.responseText);
      }
    });
  };

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
      authorCallback(true, username);
    //   checkUserName(username);
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

  //send an ajax request to see if that username exists - now we are using the user ids so this wont work
  // function checkUserName(username){
  //   $.ajax({
  //     url: "/author/"+username+"/",
  //     complete: function(e,xhr,settings){
  //       if(e.status === 200) {
  //         authorCallback(true, username);
  //       } else if (e.status === 404) {
  //         authorCallback(false, username);
  //       }
  //     }
  //   });
  // }

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

  $("#get_github_events").click(function(){
    $("#github_body").empty();
    var github_html = $('#id-github').html();
    if (github_html != "github: ") {
      var github_name = github_html.split(" ")[1].split("/")[3]
      //need to check that its a valid github name
      var u_url = "https://api.github.com/users/"+github_name;
      checkGHUserName(u_url, github_name);
    } else {
      alert("no github name provided");
    }
  });

  function githubCallback(result, url, username){
    var path = url +"/events";
    console.log(path);
    if (result === true) {
      $.getJSON(path, function (data) {
          //$("#github_body").html("Under Construction -> Data received still need to make it more reader friendly.");
          $.each(data, function (i, field) {
              if (field["payload"]["commits"] != undefined) {
                $("#github_body").append("<p>"+"<b>"+field["type"]+"</b>"+" to "+field["repo"]["name"]+"</p>"+"<p>"+"<b>Message:</b>"+field["payload"]["commits"][0]["message"]+"</p><br/>")
              }
              //var textNode = document.createTextNode(i+ " " +JSON.stringify(field));
              //var textNode = document.createTextNode(JSON.stringify(JSON.stringify(field)));
              //var $newdiv = $( "<div id='github_event_"+i+"'/>" );
              //$("#github_body").append($newdiv);
              //$("#github_event_"+i).append(textNode);
              // only get most recent 5 events
              if (i > 5) {
                //$("#github_body").append("<b>Older Activity Hidden</b>");
                return false;
              }
          });
      });
    } else {
      alert(username+" is not a valid github username");
    }
  }

  //send an ajax request to see if that username exists - now we are using the user ids so this wont work
  function checkGHUserName(url, username){
    $.ajax({
      url: url,
      complete: function(e,xhr,settings){
        if(e.status === 200) {
          githubCallback(true, url);
        } else if (e.status === 404) {
          githubCallback(false, url, username);
        }
      }
    });
  }

// use bootstrap tooltip to display the small pop-up box
  $(document).ready(function(){
      $('[data-toggle="tooltip"]').tooltip();
  });


    $("#closechangePasswordModal").click(function(){
        // clear  form when press close
        $("form#changePasswordForm").trigger("reset");
    });

    // display error messages when trying to change passwords incorrectly
    $("#changePasswordForm").submit(function(event) {
        event.preventDefault();
        var oldPass = document.getElementById('old_password').value;
        var newPass = document.getElementById('new_password').value;
        var confirmNewPass = document.getElementById('reset_password').value;
        if (newPass!=confirmNewPass){
            toastr.info("new passwords did not match!");
            return
        }
        var authorID = $("#changePasswordForm").data("author-id");
        var Data = "old_password="+oldPass+"&new_password="+newPass+"&reset_password="+confirmNewPass;
        $.ajax({
            url: 'http://' + window.location.host + '/author/' + authorID + '/',
            type: "POST",
            data: Data,
            contentType: 'application/x-www-form-urlencoded; charset=utf-8',
            //dataType: 'json',
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
                // close modal
                $("button#closechangePasswordModal").click();
                // clear  form
                $("form#changePasswordForm").trigger("reset");
                toastr.info("Password Changed!");
            },
            error: function(xhr, ajaxOptions, error) {
                console.log(xhr.status);
                console.log(xhr.responseText);
                console.log(error);
                toastr.info("old password incorrect!");
      }
    });
  });




};
