window.onload = function() {
  alert("HELLO");
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
};