$("form[name=signup_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/user/signup",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp) {
            window.location.href = "/user/login";
            window.alert("註冊成功");
        },
        
        error: function(resp) {
            console.log(resp);
            $error.text(resp.responseJSON.error).removeClass("error--hidden")
        }

    });
    e.preventDefault();

});

$("form[name=login_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/user/login",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp) {
            window.location.href = "/";
            window.alert("登入成功");
        },
        error: function(resp) {
            console.log(resp);
            $error.text(resp.responseJSON.error).removeClass("error--hidden")
        }

    });
    e.preventDefault();

});

$("form[name=update_user_form]").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/user/update_user",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp) {
            window.location.href = "/dashboard/";
            window.alert("修改成功");
        },
        error: function(resp) {
            console.log(resp);
            $error.text(resp.responseJSON.error).removeClass("error--hidden")
            window.alert("修改失敗");
        }

    });
    e.preventDefault();

});

$(document).ready(function() {

    $('#password, #password_confirm').keyup(validate);
      
    function validate() {
        if ( $('#password_confirm').val() == $('#password').val()) {
            $('#password_confirm').css('border-color', '');
            $('#password').css('border-color', '');
            
        } else { 
            $('#password_confirm').css('border-color', 'red');
            $('#password').css('border-color', 'red');
          }
    };
      
});

