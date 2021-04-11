$(document).ready(function () {

  $(document).on('submit', 'form[name="add_city"]', function (event) {

    req = $.ajax({
      data: {
        city_name: $('#input-city').val()
      },
      type: 'POST',
      url: '/add',
      timeout: 20000,
      error: function (error) {
        $('.alert').text(error.responseText);
        $('.alert').show();
      }
    })

    req.done(function (response) {
      if ($.trim(response)) {
        if (typeof response == "object") {
          console.log(response);
        }
        else {
          $('.cards').html(response);
        }
      }
    });
    event.preventDefault();
  });

  $(document).on('submit', 'form[name="del_city"]', function (event) {
    del_req = $.ajax({
      type: 'POST',
      url: $(this).closest('form').attr('action'),
      timeout: 20000,
      error: function (error) {
        $('.alert').text(error.responseText);
        $('.alert').show();
      }
    });
    del_req.done(function (response) {
      $('#' + response).remove();
    });
    event.preventDefault();
  });
});
