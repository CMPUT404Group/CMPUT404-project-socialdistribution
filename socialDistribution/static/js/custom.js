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

  // $("button#submit_edit_post").submit(function(event) {
  //   event.preventDefault();
  //   var formData = new FormData($("#postForm")[0]);
  //   $.ajax({
  //     url: 'http://' + window.location.host + '/api//',
  //     type: "POST",
  //     data: formData,
  //     contentType: false,
  //     processData: false,
  //     beforeSend: function(xhr, settings) {
  //       xhr.setRequestHeader("X-CSRFToken", csrftoken);
  //     },
  //     success: function(response) {
  //       console.log(response);
  //       // close modal
  //       $("button#closeUploadImageModal").click();
  //       // clear upload image form
  //       $("form#uploadImageForm").trigger("reset");
  //       // append "Image Attached" element
  //       $("#uploadImageTrigger").after('<span class="label label-primary imageAttachedIcon">Image Attached!</span>');
  //       // disable add image button in create post form
  //       $("#uploadImageTrigger").prop("disabled", true);
  //       // add image url to form's hidden image_url field (on create post form)
  //       $("input#id_image_url").val(response.photo);
  //       toastr.info("Image Uploaded!");
  //     },
  //     error: function(xhr, ajaxOptions, error) {
  //       console.log(xhr.status);
  //       console.log(xhr.responseText);
  //       console.log(error);
  //     }
  //   });

  // /* -- Edits posts -- */
  // $("button.edit-post").click(function(event) {
  //   var that = this;
  //   var id = this.id.slice(9);
  //   var formData = new FormData($("#uploadImageForm")[0]);

  //   $.ajax({
  //     url: 'http://' + window.location.host +'/api/posts/' + id + '/',
  //     type: "PUT",
  //     data: formData,
  //     beforeSend: function(xhr, settings) {
  //       xhr.setRequestHeader("X-CSRFToken", csrftoken);
  //     },
  //     success: function(response) {
  //       console.log(response);
  //       toastr.info("Post Edited");
  //     },
  //     error: function(xhr, ajaxOptions, error) {
  //       console.log(xhr.status);
  //       console.log(xhr.responseText);
  //       console.log(error);
  //     }
  //   });
  // });


  /* -- Hide Upload Image Modal Initially -- */
  $("#uploadImageModal").hide();
  
  $("#uploadImageForm").submit(function(event) {
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

};